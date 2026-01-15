# batch_dispatcher.py
import json
import math
import time
import asyncio
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore
import re

from config import Config
from api_mapping import PerformMapping
from result_processor import ProcessMappingResults
from rate_limiter import get_rate_limiter_for_model, estimate_tokens
from logger import get_logger

logger = get_logger(__name__)


def safe_print(*args, **kwargs):
    """
    Safe print function that catches NoSessionContext errors.

    When running in async ThreadPoolExecutor, Streamlit's print() redirection
    fails with NoSessionContext. This wrapper catches that error and falls back
    to logging.
    """
    try:
        # Use builtins.print to avoid recursion
        import builtins
        builtins.print(*args, **kwargs)
    except Exception as e:
        # If print fails (e.g., NoSessionContext in async threads), use logger
        if 'NoSessionContext' in str(type(e).__name__):
            # Extract message from args
            message = ' '.join(str(arg) for arg in args)
            # Clean ANSI color codes for logger
            clean_message = re.sub(r'\x1b\[[0-9;]+m', '', message)
            logger.debug(f"[print suppressed in async context] {clean_message}")
        else:
            # Re-raise if it's a different error
            raise


def calculate_optimal_batch_split(n1: int, n2: int, max_batch_size: int = 200) -> Dict:
    """
    Calculate optimal batch splitting strategy to minimize total batches.
    
    Args:
        n1: Number of rows in first group
        n2: Number of rows in second group
        max_batch_size: Maximum rows per batch (default 200)
    
    Returns:
        Dictionary with optimal batching plan
    """
    
    best_f, best_s = 0, 0
    min_batches = float('inf')
    
    # Try all possible splits where f + s = max_batch_size
    for f in range(1, max_batch_size):
        s = max_batch_size - f
        if s < 1:
            continue
            
        b1 = math.ceil(n1 / f)
        b2 = math.ceil(n2 / s)
        total_batches = b1 * b2
        
        if total_batches < min_batches:
            min_batches = total_batches
            best_f = f
            best_s = s
        elif total_batches == min_batches:
            # Tie-breaking rules
            current_diff = abs(best_f - best_s)
            new_diff = abs(f - s)
            
            if new_diff < current_diff:
                # Prefer more balanced split
                best_f = f
                best_s = s
            elif new_diff == current_diff:
                # Prefer smaller remainders
                current_remainder = (n1 % best_f) + (n2 % best_s)
                new_remainder = (n1 % f) + (n2 % s)
                
                if new_remainder < current_remainder:
                    best_f = f
                    best_s = s
                elif new_remainder == current_remainder and s > best_s:
                    # Prefer larger s
                    best_f = f
                    best_s = s
    
    # Calculate blocks
    b1 = math.ceil(n1 / best_f)
    b2 = math.ceil(n2 / best_s)
    
    # Create block ranges
    first_blocks = []
    for i in range(b1):
        start = i * best_f
        end = min((i + 1) * best_f, n1)
        first_blocks.append({
            "index": i + 1,
            "start": start + 1,  # 1-indexed
            "end": end
        })
    
    second_blocks = []
    for j in range(b2):
        start = j * best_s
        end = min((j + 1) * best_s, n2)
        second_blocks.append({
            "index": j + 1,
            "start": start + 1,  # 1-indexed
            "end": end
        })
    
    # Create batch plan
    batches = []
    batch_index = 1
    for i in range(b1):
        for j in range(b2):
            batch = {
                "batch_index": batch_index,
                "first_block_index": i + 1,
                "second_block_index": j + 1,
                "first_range": [first_blocks[i]["start"], first_blocks[i]["end"]],
                "second_range": [second_blocks[j]["start"], second_blocks[j]["end"]]
            }
            batches.append(batch)
            batch_index += 1
    
    return {
        "n1": n1,
        "n2": n2,
        "f": best_f,
        "s": best_s,
        "b1": b1,
        "b2": b2,
        "total_batches": min_batches,
        "first_blocks": first_blocks,
        "second_blocks": second_blocks,
        "batches": batches
    }


async def process_batch_async(
    batch_info: Dict,
    batch_index: int,
    total_batches: int,
    first_group_list: List[Dict],
    second_group_list: List[Dict],
    first_group_compact: List[Dict],
    second_group_compact: List[Dict],
    prompt: str,
    rate_limiter,
    executor: ThreadPoolExecutor
) -> Optional[Dict]:
    """
    Process a single batch asynchronously with rate limiting.

    Args:
        batch_info: Batch configuration dictionary
        batch_index: Current batch number
        total_batches: Total number of batches
        first_group_list: Full format first group data
        second_group_list: Full format second group data
        first_group_compact: Compact format first group data
        second_group_compact: Compact format second group data
        prompt: Prompt text
        rate_limiter: RateLimiter instance for RPM/TPM tracking
        executor: ThreadPoolExecutor for running sync code

    Returns:
        Batch result dictionary or None if failed
    """
    logger.info(f"Processing Batch {batch_index}/{total_batches} | Model: {Config.model}")

    # Extract batch data (using 0-indexed for list slicing)
    first_start = batch_info['first_range'][0] - 1
    first_end = batch_info['first_range'][1]
    second_start = batch_info['second_range'][0] - 1
    second_end = batch_info['second_range'][1]

    # Get batch subsets
    batch_first_list = first_group_list[first_start:first_end]
    batch_second_list = second_group_list[second_start:second_end]
    batch_first_compact = first_group_compact[first_start:first_end]
    batch_second_compact = second_group_compact[second_start:second_end]

    logger.info(f"  - First group: rows {batch_info['first_range'][0]}-{batch_info['first_range'][1]} ({len(batch_first_list)} items)")
    logger.info(f"  - Second group: rows {batch_info['second_range'][0]}-{batch_info['second_range'][1]} ({len(batch_second_list)} items)")

    # Estimate tokens for this batch
    estimated_tokens = 0
    if Config.use_compact_json:
        batch_text = json.dumps(batch_first_compact + batch_second_compact)
    else:
        batch_text = json.dumps(batch_first_list + batch_second_list)
    estimated_tokens = estimate_tokens(batch_text + prompt)

    # Check rate limits and wait if necessary
    wait_time = rate_limiter.wait_if_needed(estimated_tokens)
    if wait_time > 0:
        logger.info(f"  - Waited {wait_time:.1f}s for rate limits")

    # Check if we can proceed
    can_proceed, reason = rate_limiter.can_make_request(estimated_tokens)
    if not can_proceed:
        logger.warning(f"[!] Batch {batch_index} delayed due to rate limits: {reason}")
        logger.info(f"  Waiting 5 seconds before retry...")
        await asyncio.sleep(5)  # Brief wait before retry
        # Recursive retry after delay
        return await process_batch_async(
            batch_info, batch_index, total_batches,
            first_group_list, second_group_list,
            first_group_compact, second_group_compact,
            prompt, rate_limiter, executor
        )

    # Run the synchronous PerformMapping in the thread pool
    loop = asyncio.get_event_loop()

    try:
        if Config.use_compact_json:
            api_result = await loop.run_in_executor(
                executor,
                lambda: PerformMapping(
                    first_group=batch_first_compact,
                    second_group=batch_second_compact,
                    prompt=prompt,
                    verbose=False,
                    use_compact=True,
                    full_format_first=batch_first_list,
                    full_format_second=batch_second_list
                )
            )
        else:
            api_result = await loop.run_in_executor(
                executor,
                lambda: PerformMapping(
                    first_group=batch_first_list,
                    second_group=batch_second_list,
                    prompt=prompt,
                    verbose=False,
                    use_compact=False
                )
            )

        if api_result is None:
            logger.error(f"[X] Batch {batch_index} failed - PerformMapping returned None")
            logger.error(f"  Possible causes: Missing API key, invalid credentials, or API error")
            return None

        # Record the API call in rate limiter
        total_tokens = api_result["response"].usage.total_tokens
        rate_limiter.record_request(total_tokens)

        # Get current rate limiter stats
        stats = rate_limiter.get_stats()
        logger.debug(f"  - Rate limiter: RPM {stats['current_rpm']}/{stats['rpm_limit']} ({stats['rpm_percentage']:.1f}%), "
                    f"TPM {stats['current_tpm']:,}/{stats['tpm_limit']:,} ({stats['tpm_percentage']:.1f}%)")

        # Process batch results
        batch_result = ProcessMappingResults(
            mappings=api_result["mappings"],
            response=api_result["response"],
            elapsed_time=api_result["elapsed_time"],
            verbose=False,
            reset_before_processing=False
        )

        if batch_result:
            logger.info(f"[+] Batch {batch_index} of {total_batches} completed successfully")
            logger.info(f"  - Mappings in this batch: {len(api_result['mappings'])}")
            return batch_result

        return None

    except Exception as e:
        logger.error(f"[X] Batch {batch_index} encountered exception")
        logger.error(f"  Exception type: {type(e).__name__}")
        logger.error(f"  Exception message: {str(e) if str(e) else '(empty error message)'}")
        logger.exception(f"  Full traceback for batch {batch_index}:")
        return None


async def process_batches_async(
    batch_plan: Dict,
    first_group_list: List[Dict],
    second_group_list: List[Dict],
    first_group_compact: List[Dict],
    second_group_compact: List[Dict],
    prompt: str,
    max_concurrent_batches: int = 3
) -> List[Dict]:
    """
    Process multiple batches asynchronously with rate limiting.

    Args:
        batch_plan: Batch planning dictionary from calculate_optimal_batch_split
        first_group_list: Full format first group data
        second_group_list: Full format second group data
        first_group_compact: Compact format first group data
        second_group_compact: Compact format second group data
        prompt: Prompt text
        max_concurrent_batches: Maximum number of concurrent batch operations (default: 3)

    Returns:
        List of batch results
    """
    # Initialize rate limiter for the current model
    rate_limiter = get_rate_limiter_for_model(Config.model, Config.provider)

    # Create thread pool for running sync code
    executor = ThreadPoolExecutor(max_workers=max_concurrent_batches)

    # Create semaphore to limit concurrent batches
    semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def process_with_semaphore(batch_info, batch_index):
        async with semaphore:
            return await process_batch_async(
                batch_info, batch_index, batch_plan['total_batches'],
                first_group_list, second_group_list,
                first_group_compact, second_group_compact,
                prompt, rate_limiter, executor
            )

    # Create tasks for all batches
    tasks = [
        process_with_semaphore(batch, i + 1)
        for i, batch in enumerate(batch_plan['batches'])
    ]

    # Process all batches concurrently
    logger.info(f"Starting async batch processing with max {max_concurrent_batches} concurrent batches...")
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out None results and exceptions
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"[X] Batch {i+1} raised exception: {str(result)}")
        elif result is not None:
            successful_results.append(result)

    executor.shutdown(wait=True)

    return successful_results


def Dispatcher(first_group_list: List[Dict],
               second_group_list: List[Dict],
               first_group_compact: List[Dict],
               second_group_compact: List[Dict],
               prompt: str,
               n1: int,
               n2: int,
               verbose: bool = True,
               max_batch_size: int = None,
               wait_between_batches: int = None) -> Optional[Dict]:
    """
    Dispatcher function that handles batching of large datasets.
    
    Args:
        first_group_list: Full format first group data
        second_group_list: Full format second group data
        first_group_compact: Compact format first group data
        second_group_compact: Compact format second group data
        prompt: Prompt text
        n1: Number of rows in first group
        n2: Number of rows in second group
        verbose: Print detailed information
        max_batch_size: Maximum rows per batch (uses Config if None)
        wait_between_batches: Seconds to wait between batches (uses Config if None)
    
    Returns:
        Combined results from all batches
    """
    
    # Use Config values if not provided
    max_batch_size = max_batch_size or Config.max_batch_size
    wait_between_batches = wait_between_batches or Config.wait_between_batches
    
    safe_print(f"\n{Fore.MAGENTA}{'='*60}")
    logger.info(f"DISPATCHER: Batch Processing Handler")
    Config.log_configuration()
    safe_print(f"{Fore.MAGENTA}{'='*60}\n")

    # Pre-flight check: Validate API key before processing
    from api_mapping import get_api_client
    test_client, test_api_key, test_provider = get_api_client()
    if not test_api_key:
        logger.error(f"[X] CRITICAL: {test_provider} API key not found!")
        logger.error(f"  Cannot proceed with batch processing without valid API credentials")
        logger.error(f"  Please set {test_provider} API key in environment or Streamlit secrets")
        safe_print(f"\n{Fore.RED}[X] ERROR: Missing API key for {test_provider}")
        safe_print(f"{Fore.YELLOW}Please set your API key before processing:")
        safe_print(f"  - Environment variable: {'OPENAI_API_KEY' if test_provider == 'OpenAI' else 'OPENROUTER_API_KEY'}")
        safe_print(f"  - Or Streamlit secrets: .streamlit/secrets.toml")
        return None
    logger.info(f"[+] API key validated for {test_provider}")

    # Check if batching is needed
    total_rows = n1 + n2
    
    if total_rows <= max_batch_size:
        # No batching needed
        logger.info(f"Total rows ({total_rows}) ≤ max batch size ({max_batch_size})")
        logger.info("Proceeding without batching...")
        
        # Call PerformMapping directly
        if Config.use_compact_json:
            api_result = PerformMapping(
                first_group=first_group_compact,
                second_group=second_group_compact,
                prompt=prompt,
                verbose=verbose,
                use_compact=True,
                full_format_first=first_group_list,
                full_format_second=second_group_list
            )
        else:
            api_result = PerformMapping(
                first_group=first_group_list,
                second_group=second_group_list,
                prompt=prompt,
                verbose=verbose,
                use_compact=False
            )
        
        if api_result is None:
            return None
        
        # Process results
        return ProcessMappingResults(
            mappings=api_result["mappings"],
            response=api_result["response"],
            elapsed_time=api_result["elapsed_time"],
            verbose=verbose
        )
    
    # Batching is needed
    logger.warning(f"Total rows ({total_rows}) > max batch size ({max_batch_size})")
    logger.info("Calculating optimal batch strategy...")
    
    # Calculate optimal batching plan
    batch_plan = calculate_optimal_batch_split(n1, n2, max_batch_size)
    
    # Display batch plan
    safe_print(f"\n{Fore.CYAN}Batch Plan:")
    logger.info(f"  - First group rows (n1): {batch_plan['n1']}")
    logger.info(f"  - Second group rows (n2): {batch_plan['n2']}")
    logger.info(f"  - Rows per batch from first group (f): {batch_plan['f']}")
    logger.info(f"  - Rows per batch from second group (s): {batch_plan['s']}")
    logger.info(f"  - Number of first group blocks (b1): {batch_plan['b1']}")
    logger.info(f"  - Number of second group blocks (b2): {batch_plan['b2']}")
    logger.info(f"  - Total batches: {batch_plan['total_batches']}")
    logger.info(f"  - Wait between batches: {wait_between_batches} seconds")
    logger.info(f"  - Estimated total time: ~{batch_plan['total_batches'] * (wait_between_batches + 10) / 60:.1f} minutes")
    
    if verbose:
        safe_print(f"\n{Fore.CYAN}Batch Details (first 5):")
        for batch in batch_plan['batches'][:5]:
            safe_print(f"{Fore.WHITE}  Batch {batch['batch_index']}: "
                  f"First[{batch['first_range'][0]}-{batch['first_range'][1]}] × "
                  f"Second[{batch['second_range'][0]}-{batch['second_range'][1]}]")
        if len(batch_plan['batches']) > 5:
            logger.info(f"  ... and {len(batch_plan['batches']) - 5} more batches")
    
    # Process batches asynchronously with rate limiting
    safe_print(f"\n{Fore.YELLOW}Starting async batch processing with rate limiting...")

    # Determine max concurrent batches from Config
    max_concurrent = min(Config.max_concurrent_batches, batch_plan['total_batches'])
    logger.info(f"  - Max concurrent batches: {max_concurrent}")
    logger.info(f"  - Rate limiting: Automatic RPM/TPM tracking")

    # Run async batch processing
    try:
        all_results = asyncio.run(
            process_batches_async(
                batch_plan=batch_plan,
                first_group_list=first_group_list,
                second_group_list=second_group_list,
                first_group_compact=first_group_compact,
                second_group_compact=second_group_compact,
                prompt=prompt,
                max_concurrent_batches=max_concurrent
            )
        )
    except Exception as e:
        logger.error(f"[X] Async batch processing failed: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None
    
    # Combine all results
    safe_print(f"\n{Fore.CYAN}{'='*60}")
    logger.info(f"Combining results from all batches...")
    logger.info(f"{'='*60}")
    
    if not all_results:
        logger.error(f"[X] No successful batches")
        return None
    
    # Return the last batch result (which contains accumulated DataFrames)
    final_result = all_results[-1] if all_results else None
    
    if final_result:
        # Update summary statistics
        total_mappings = sum(len(r.get("mappings", [])) for r in all_results)
        safe_print(f"\n{Fore.GREEN}[+] Batch processing completed")
        logger.info(f"  - Total batches processed: {len(all_results)}/{batch_plan['total_batches']}")
        logger.info(f"  - Total mappings: {total_mappings}")
        
        # Add batch processing metadata
        final_result["batch_metadata"] = {
            "total_batches": batch_plan['total_batches'],
            "batches_processed": len(all_results),
            "batch_plan": batch_plan,
            "parameters_used": {
                "model": Config.model,
                "temperature": Config.temperature,
                "top_p": Config.top_p,
                "max_batch_size": max_batch_size,
                "wait_between_batches": wait_between_batches
            }
        }
    
    return final_result