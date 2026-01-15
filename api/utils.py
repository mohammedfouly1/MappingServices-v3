"""
api_utils.py - API utility functions including retry logic

This module provides utilities for making resilient API calls with
exponential backoff and automatic retry on transient failures.
"""

import time
from typing import Callable, TypeVar, Tuple
from functools import wraps
from openai import RateLimitError, APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError
from logger import get_logger

logger = get_logger(__name__)

# Type variable for generic return type
T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retriable_exceptions: Tuple = (
        RateLimitError,
        APIConnectionError,
        APITimeoutError
    )
):
    """
    Decorator for retrying functions with exponential backoff.

    This decorator automatically retries failed function calls with
    exponentially increasing delays between attempts. Useful for
    handling transient API failures.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay between retries in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        retriable_exceptions: Tuple of exceptions to retry on

    Returns:
        Decorator function

    Example:
        @retry_with_backoff(max_retries=3, base_delay=2.0)
        def call_api():
            return client.chat.completions.create(...)

    Behavior:
        - Attempt 1: Immediate call
        - Attempt 2: Wait base_delay (1.0s)
        - Attempt 3: Wait base_delay * backoff_factor (2.0s)
        - Attempt 4: Wait base_delay * backoff_factor^2 (4.0s)
        - Max delay capped at max_delay

    Non-retriable exceptions (AuthenticationError, BadRequestError):
        These fail immediately without retry as they indicate permanent problems.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"[+] Retry successful on attempt {attempt + 1}/{max_retries + 1}")
                    return result

                except retriable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"[X] Max retries ({max_retries}) exceeded for {func.__name__}"
                        )
                        logger.error(f"  Final error: {type(e).__name__}: {str(e)}")
                        raise

                    # Log warning and retry
                    logger.warning(
                        f"[!] Attempt {attempt + 1}/{max_retries + 1} failed: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    logger.info(f"  Retrying in {delay:.1f}s...")

                    time.sleep(delay)

                    # Exponential backoff with max cap
                    delay = min(delay * backoff_factor, max_delay)

                except (AuthenticationError, BadRequestError) as e:
                    # Non-retriable exceptions - fail immediately
                    logger.error(
                        f"[X] Non-retriable error in {func.__name__}: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    logger.error("  This error cannot be fixed by retrying")
                    raise

                except Exception as e:
                    # Unexpected exception - fail immediately
                    logger.error(
                        f"[X] Unexpected error in {func.__name__}: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def retry_api_call(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs
) -> T:
    """
    Retry an API call function with exponential backoff.

    This is a non-decorator version for situations where you can't
    use the decorator syntax.

    Args:
        func: Function to call
        *args: Positional arguments for func
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Example:
        result = retry_api_call(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[...],
            max_retries=3
        )
    """
    decorated_func = retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay
    )(func)

    return decorated_func(*args, **kwargs)


class RetryConfig:
    """
    Configuration for retry behavior.

    This class provides a centralized way to configure retry behavior
    across the application.

    Attributes:
        max_retries: Maximum retry attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        backoff_factor: Exponential backoff multiplier
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def get_decorator(self):
        """
        Get a retry decorator with this configuration.

        Returns:
            Decorator function configured with these settings
        """
        return retry_with_backoff(
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            backoff_factor=self.backoff_factor
        )


# Default retry configuration for the application
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=2.0,  # Start with 2 second delay
    max_delay=60.0,
    backoff_factor=2.0
)


def is_retriable_error(exception: Exception) -> bool:
    """
    Check if an exception is retriable.

    Args:
        exception: The exception to check

    Returns:
        bool: True if the exception should be retried, False otherwise
    """
    retriable_types = (
        RateLimitError,
        APIConnectionError,
        APITimeoutError
    )

    return isinstance(exception, retriable_types)


def calculate_backoff_delay(
    attempt: int,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0
) -> float:
    """
    Calculate the delay for exponential backoff.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for each attempt
        max_delay: Maximum delay in seconds

    Returns:
        float: Delay in seconds for this attempt

    Example:
        >>> calculate_backoff_delay(0, 1.0, 2.0, 60.0)  # First retry
        1.0
        >>> calculate_backoff_delay(1, 1.0, 2.0, 60.0)  # Second retry
        2.0
        >>> calculate_backoff_delay(2, 1.0, 2.0, 60.0)  # Third retry
        4.0
    """
    delay = base_delay * (backoff_factor ** attempt)
    return min(delay, max_delay)
