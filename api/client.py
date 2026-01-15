# api_mapping.py
import json
import time
from typing import Any, Dict, List, Optional
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError, BadRequestError
from colorama import Fore
import traceback
import sys

from config import Config
from optimization_utils import create_compact_item, expand_compact_result
from logger import get_logger, log_api_call, log_exception
from api_utils import retry_with_backoff

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
            import re
            clean_message = re.sub(r'\x1b\[[0-9;]+m', '', message)
            logger.debug(f"[print suppressed in async context] {clean_message}")
        else:
            # Re-raise if it's a different error
            raise


def get_api_client() -> tuple[Optional[OpenAI], Optional[str], str]:
    """
    Initialize and return the appropriate API client based on provider.

    Returns:
        tuple: (client, api_key, provider_name)
            - client: OpenAI client instance or None
            - api_key: API key string or None
            - provider_name: Provider name string ("OpenAI" or "OpenRouter")
    """
    if Config.provider == "OpenRouter":
        if not Config.openrouter_api_key:
            return None, None, "OpenRouter"
        # OpenRouter uses OpenAI-compatible API
        client = OpenAI(
            api_key=Config.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        return client, Config.openrouter_api_key, "OpenRouter"
    else:
        # Default to OpenAI
        if not Config.api_key:
            return None, None, "OpenAI"
        client = OpenAI(api_key=Config.api_key)
        return client, Config.api_key, "OpenAI"


def PerformMapping(first_group: List[Dict],
                   second_group: List[Dict],
                   prompt: str,
                   verbose: bool = True,
                   use_compact: bool = True,
                   full_format_first: List[Dict] = None,
                   full_format_second: List[Dict] = None) -> Optional[Dict]:
    """
    Performs the actual mapping using OpenAI or OpenRouter API with optimized token usage.
    Uses parameters from Config which are set by the user in Streamlit.

    Args:
        first_group: List of First Group items (compact or full format)
        second_group: List of Second Group items (compact or full format)
        prompt: Prompt text for the mapping
        verbose: If True, prints detailed information
        use_compact: If True, uses compact JSON format
        full_format_first: Full format of first group for result processing
        full_format_second: Full format of second group for result processing

    Returns:
        Dictionary with mapping results or None if error
    """

    safe_print(f"\n{Fore.MAGENTA}{'='*60}")
    logger.info(f"Starting Mapping Process (Optimized)")
    Config.log_configuration()
    safe_print(f"{Fore.MAGENTA}{'='*60}\n")

    # Get API client based on provider
    client, api_key, provider_name = get_api_client()

    if not api_key:
        logger.error(f"[X] Error: {provider_name} API key not found")
        logger.debug(f"Please set your {provider_name} API key")
        return None

    try:
        logger.info(f"[+] {provider_name} client initialized")
        
        # Prepare optimized prompt based on format
        if use_compact:
            # Create ultra-compact prompt
            optimized_prompt = f"""Map items from Group1 to Group2. Each item has 'c'(code) and 'n'(name).

Return JSON object with 'mappings' array. Each mapping:
{{"fc":"<first_code>","fn":"<first_name>","sc":"<second_code>","sn":"<second_name>","s":<score_1-100>,"r":"<reason>"}}

If no match: sc and sn should be null, s should be <{Config.threshold}.

Group1:
{json.dumps(first_group, ensure_ascii=False, separators=(',', ':'))}

Group2:
{json.dumps(second_group, ensure_ascii=False, separators=(',', ':'))}

Map ALL Group1 items. Return only JSON."""
        else:
            # Standard format prompt
            optimized_prompt = f"""
{prompt}

FIRST_GROUP:
{json.dumps(first_group, ensure_ascii=False, separators=(',', ':'))}

SECOND_GROUP:
{json.dumps(second_group, ensure_ascii=False, separators=(',', ':'))}

Return JSON object with 'mappings' array containing all mappings. Use threshold: {Config.threshold}"""
        
        if verbose:
            safe_print(f"\n{Fore.CYAN}Optimized Prompt Preview (first 500 chars):")
            logger.debug(f"{optimized_prompt[:500]}...")
            safe_print(f"\n{Fore.WHITE}Optimized prompt length: {len(optimized_prompt)} characters")
            logger.debug(f"Estimated tokens: ~{len(optimized_prompt)//4}")
        
        # Prepare API call
        safe_print(f"\n{Fore.YELLOW}Calling {provider_name} API...")
        logger.debug(f"API call: {provider_name} | Model: {Config.model} | Optimization: {'COMPACT' if use_compact else 'STANDARD'}")

        start_time = time.time()

        # System message based on mode
        if use_compact:
            system_msg = f"You are a laboratory mapping expert. Use the exact abbreviated JSON format specified. Be concise. Apply threshold {Config.threshold} for similarity scores."
        else:
            system_msg = f"You are a world-class Laboratory Mapping expert. Return valid JSON with all mappings. Apply threshold {Config.threshold} for similarity scores."

        # Prepare base parameters
        api_params = {
            "model": Config.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_msg
                },
                {
                    "role": "user",
                    "content": optimized_prompt
                }
            ],
            "temperature": Config.temperature,
            "top_p": Config.top_p,
        }

        # Use max_completion_tokens for newer OpenAI models (gpt-4o, gpt-5, o1, o3, etc.)
        # These models don't support the older max_tokens parameter
        model_lower = Config.model.lower()
        needs_new_token_param = (
            Config.provider == "OpenAI" and
            any(model_lower.startswith(prefix) for prefix in ["gpt-4o", "gpt-5", "o1", "o3"])
        )

        if needs_new_token_param:
            api_params["max_completion_tokens"] = Config.max_tokens
        else:
            api_params["max_tokens"] = Config.max_tokens

        # Add OpenRouter-specific headers if using OpenRouter
        if Config.provider == "OpenRouter":
            api_params["extra_headers"] = {
                "HTTP-Referer": "https://mapping-medical-services.streamlit.app",
                "X-Title": "Medical Mapping Service"
            }

        # Make API call with user-defined parameters
        try:
            response = client.chat.completions.create(
                **api_params,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            # Fallback without response_format (some models don't support it)
            logger.warning(f"Note: JSON format enforcement not supported, using text mode")
            response = client.chat.completions.create(**api_params)
        
        elapsed_time = time.time() - start_time

        # Log successful API call
        log_api_call(
            logger,
            provider=Config.provider,
            model=Config.model,
            tokens={
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens,
                'total': response.usage.total_tokens
            },
            latency=elapsed_time,
            success=True
        )

        logger.info(f"[+] API call completed in {elapsed_time:.2f} seconds")
        logger.debug(f"  - Model used: {Config.model}")
        logger.debug(f"  - Temperature used: {Config.temperature}")
        logger.debug(f"  - Top P used: {Config.top_p}")

        # Check for truncation
        finish_reason = response.choices[0].finish_reason
        if finish_reason == "length":
            logger.warning(f"[!] Response was truncated (max_tokens reached)")

        # Extract response
        response_text = response.choices[0].message.content
        
        if verbose:
            safe_print(f"\n{Fore.CYAN}Response preview (first 500 chars):")
            logger.debug(f"{response_text[:500]}...")
        
        # Parse JSON response
        mapping_results = parse_optimized_response(response_text, use_compact, verbose)
        
        if mapping_results is None:
            return None
        
        logger.info(f"[+] Successfully parsed {len(mapping_results)} mappings")
        
        # If using compact format, expand results
        if use_compact:
            expanded_results = []
            for item in mapping_results:
                expanded = expand_compact_result(item, "mapping")
                expanded_results.append(expanded)
            mapping_results = expanded_results
        
        # Return raw data for processing in another module
        return {
            "mappings": mapping_results,
            "response": response,
            "elapsed_time": elapsed_time,
            "response_text": response_text,
            "parameters_used": {
                "provider": Config.provider,
                "model": Config.model,
                "temperature": Config.temperature,
                "top_p": Config.top_p,
                "max_tokens": Config.max_tokens,
                "threshold": Config.threshold
            }
        }
            
    except Exception as e:
        logger.error(f"[X] Error during API call: {str(e)}")
        logger.debug(f"  - Model attempted: {Config.model}")
        logger.debug(f"  - Temperature: {Config.temperature}")
        logger.debug(f"  - Top P: {Config.top_p}")
        if verbose:
            logger.warning(f"Traceback:")
            safe_print(traceback.format_exc())
        return None


def parse_optimized_response(response_text: str, is_compact: bool, verbose: bool) -> Optional[List[Dict]]:
    """Parse response based on format (compact or standard)"""

    import re

    mapping_results = None
    cleaned_text = response_text.strip()

    # Step 1: Remove markdown code blocks if present
    # Handle ```json ... ``` or ``` ... ```
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned_text)
    if code_block_match:
        cleaned_text = code_block_match.group(1).strip()
        if verbose:
            logger.debug(f"Extracted content from markdown code block")

    # Step 2: Try direct JSON parsing
    try:
        parsed_json = json.loads(cleaned_text)

        # Extract mappings
        if isinstance(parsed_json, dict) and "mappings" in parsed_json:
            mapping_results = parsed_json["mappings"]
            logger.info(f"[+] Found mappings in JSON object")
        elif isinstance(parsed_json, list):
            mapping_results = parsed_json
            logger.info(f"[+] Response is a direct JSON array")

    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error, attempting extraction...")

        # Step 3: Try to find JSON object with balanced braces
        # Find the start of a JSON object containing "mappings"
        mappings_idx = cleaned_text.find('"mappings"')
        if mappings_idx == -1:
            mappings_idx = cleaned_text.find("'mappings'")

        if mappings_idx != -1:
            # Find the opening brace before "mappings"
            start_idx = cleaned_text.rfind('{', 0, mappings_idx)
            if start_idx != -1:
                # Find matching closing brace using bracket counting
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(cleaned_text)):
                    char = cleaned_text[i]
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break

                if end_idx > start_idx:
                    try:
                        json_str = cleaned_text[start_idx:end_idx]
                        parsed_obj = json.loads(json_str)
                        mapping_results = parsed_obj.get("mappings", [])
                        logger.info(f"[+] Extracted mappings using bracket matching")
                    except json.JSONDecodeError:
                        pass

        # Step 4: Try to extract just the array if object parsing failed
        if mapping_results is None:
            # Look for array after "mappings":
            array_match = re.search(r'"mappings"\s*:\s*(\[[\s\S]*\])', cleaned_text)
            if array_match:
                array_str = array_match.group(1)
                # Find balanced array using bracket counting
                bracket_count = 0
                end_idx = 0
                for i, char in enumerate(array_str):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break

                if end_idx > 0:
                    try:
                        balanced_array = array_str[:end_idx]
                        mapping_results = json.loads(balanced_array)
                        logger.info(f"[+] Extracted mappings array directly")
                    except json.JSONDecodeError:
                        pass

    # Step 5: If still no results, try to repair truncated JSON
    if mapping_results is None:
        logger.warning(f"Attempting to repair truncated JSON...")

        # Show end of response to diagnose truncation
        logger.debug(f"Response ending (last 300 chars):")
        logger.debug(f"...{cleaned_text[-300:]}")

        # Try to repair by closing unclosed brackets
        repaired_text = cleaned_text

        # Count unclosed brackets
        open_braces = repaired_text.count('{') - repaired_text.count('}')
        open_brackets = repaired_text.count('[') - repaired_text.count(']')

        if open_braces > 0 or open_brackets > 0:
            logger.warning(f"Found unclosed: {open_braces} braces, {open_brackets} brackets")

            # Find the last complete mapping object
            # Look for the last complete object pattern
            last_complete_match = None
            for match in re.finditer(r'\}(?=\s*,|\s*\])', repaired_text):
                last_complete_match = match

            if last_complete_match:
                # Truncate at the last complete object and close the structure
                truncate_pos = last_complete_match.end()
                repaired_text = repaired_text[:truncate_pos]

                # Recalculate unclosed brackets after truncation
                open_braces = repaired_text.count('{') - repaired_text.count('}')
                open_brackets = repaired_text.count('[') - repaired_text.count(']')

                # Close any remaining open brackets
                repaired_text += ']' * max(0, open_brackets) + '}' * max(0, open_braces)

                try:
                    parsed_json = json.loads(repaired_text)
                    if isinstance(parsed_json, dict) and "mappings" in parsed_json:
                        mapping_results = parsed_json["mappings"]
                        logger.info(f"[+] Repaired truncated JSON, recovered {len(mapping_results)} mappings")
                    elif isinstance(parsed_json, list):
                        mapping_results = parsed_json
                        logger.info(f"[+] Repaired truncated array, recovered {len(mapping_results)} mappings")
                except json.JSONDecodeError:
                    # Try simpler repair: just close brackets at the end
                    simple_repair = cleaned_text.rstrip()
                    # Remove any trailing incomplete object/text
                    if simple_repair.endswith(','):
                        simple_repair = simple_repair[:-1]
                    simple_repair += ']}'

                    try:
                        parsed_json = json.loads(simple_repair)
                        if isinstance(parsed_json, dict) and "mappings" in parsed_json:
                            mapping_results = parsed_json["mappings"]
                            logger.info(f"[+] Simple repair succeeded, recovered {len(mapping_results)} mappings")
                    except json.JSONDecodeError:
                        pass

    if mapping_results is None:
        logger.error(f"[X] Could not parse mapping results")
        if verbose:
            safe_print(f"\n{Fore.YELLOW}Response (first 1000 chars):")
            logger.debug(f"{response_text[:1000]}")
        return None

    return mapping_results