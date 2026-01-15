"""
rate_limiter.py - Rate limiting for API calls (RPM and TPM)

This module provides rate limiting functionality to ensure API calls stay
within provider limits for Requests Per Minute (RPM) and Tokens Per Minute (TPM).

Features:
- Track API calls and token usage over time
- Check if requests can be made without exceeding limits
- Automatic cleanup of old records
- Support for different model limits
- Thread-safe operations
"""

import time
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import RLock
from core.logger import get_logger

logger = get_logger(__name__)


# Model limits - RPM (Requests Per Minute) and TPM (Tokens Per Minute)
# OpenAI Tier 3 limits - ALL models have RPM = 5,000
MODEL_LIMITS = {
    # OpenAI Models - Tier 3
    "gpt-4-turbo": {"rpm": 5000, "tpm": 600000},
    "gpt-4o-mini": {"rpm": 5000, "tpm": 4000000},
    "gpt-4o": {"rpm": 5000, "tpm": 800000},
    "chatgpt-4o-latest": {"rpm": 5000, "tpm": 800000},
    "gpt-4": {"rpm": 5000, "tpm": 5000000},
    "gpt-5": {"rpm": 5000, "tpm": 2000000},
    "gpt-5.2": {"rpm": 5000, "tpm": 2000000},
    "gpt-5-mini": {"rpm": 5000, "tpm": 4000000},
    "gpt-5.2-pro": {"rpm": 5000, "tpm": 800000},

    # OpenRouter Models (approximate limits)
    "anthropic/claude-3-opus": {"rpm": 1000, "tpm": 400000},
    "anthropic/claude-3-sonnet": {"rpm": 1000, "tpm": 400000},
    "anthropic/claude-3-haiku": {"rpm": 1000, "tpm": 400000},
    "anthropic/claude-3.5-sonnet": {"rpm": 1000, "tpm": 400000},
    "anthropic/claude-3.5-haiku": {"rpm": 1000, "tpm": 400000},
    "google/gemini-pro": {"rpm": 1000, "tpm": 500000},
    "google/gemini-pro-1.5": {"rpm": 1000, "tpm": 500000},
    "google/gemini-flash-1.5": {"rpm": 1000, "tpm": 500000},
    "google/gemini-2.0-flash": {"rpm": 1000, "tpm": 500000},
    "google/gemini-2.5-pro": {"rpm": 1000, "tpm": 500000},
    "meta-llama/llama-3-70b": {"rpm": 1000, "tpm": 300000},
    "meta-llama/llama-3.3-70b-instruct": {"rpm": 1000, "tpm": 300000},
    "mistralai/mistral-large": {"rpm": 1000, "tpm": 300000},
    "deepseek/deepseek-chat": {"rpm": 1000, "tpm": 300000},
    "deepseek/deepseek-v3": {"rpm": 1000, "tpm": 300000},

    # Default limits (conservative)
    "default": {"rpm": 500, "tpm": 100000}
}


@dataclass
class RequestRecord:
    """Record of a single API request"""
    timestamp: float  # Unix timestamp
    tokens_used: int  # Total tokens (input + output)

    def is_expired(self, window_seconds: float = 60.0) -> bool:
        """Check if this record is older than the window"""
        return time.time() - self.timestamp > window_seconds


class RateLimiter:
    """
    Rate limiter for API calls with RPM and TPM tracking.

    This class tracks API calls and token usage over a sliding time window
    to ensure rate limits are not exceeded.

    Attributes:
        rpm_limit: Maximum requests per minute
        tpm_limit: Maximum tokens per minute
        window_seconds: Time window for rate limiting (default: 60 seconds)
    """

    def __init__(
        self,
        rpm_limit: int,
        tpm_limit: int,
        window_seconds: float = 60.0,
        model_name: str = None
    ):
        """
        Initialize rate limiter with specified limits.

        Args:
            rpm_limit: Maximum requests per minute
            tpm_limit: Maximum tokens per minute
            window_seconds: Time window in seconds (default: 60)
            model_name: Optional model name for logging
        """
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.window_seconds = window_seconds
        self.model_name = model_name or "unknown"

        self.requests: List[RequestRecord] = []
        self.lock = RLock()  # Thread-safe operations (reentrant lock for nested calls)

        logger.info(f"[+] Rate limiter initialized for {self.model_name}")
        logger.debug(f"  - RPM limit: {self.rpm_limit:,}")
        logger.debug(f"  - TPM limit: {self.tpm_limit:,}")
        logger.debug(f"  - Window: {self.window_seconds}s")

    def _cleanup_old_records(self):
        """Remove expired records outside the time window"""
        current_time = time.time()
        self.requests = [
            r for r in self.requests
            if not r.is_expired(self.window_seconds)
        ]

    def get_current_usage(self) -> Tuple[int, int]:
        """
        Get current usage within the time window.

        Returns:
            tuple: (current_rpm, current_tpm)
        """
        with self.lock:
            self._cleanup_old_records()

            current_rpm = len(self.requests)
            current_tpm = sum(r.tokens_used for r in self.requests)

            return current_rpm, current_tpm

    def get_usage_percentage(self) -> Tuple[float, float]:
        """
        Get current usage as percentage of limits.

        Returns:
            tuple: (rpm_percentage, tpm_percentage)
        """
        current_rpm, current_tpm = self.get_current_usage()

        rpm_pct = (current_rpm / self.rpm_limit * 100) if self.rpm_limit > 0 else 0
        tpm_pct = (current_tpm / self.tpm_limit * 100) if self.tpm_limit > 0 else 0

        return rpm_pct, tpm_pct

    def can_make_request(self, estimated_tokens: int = 0) -> Tuple[bool, str]:
        """
        Check if a request can be made without exceeding limits.

        Args:
            estimated_tokens: Estimated tokens for the request (default: 0)

        Returns:
            tuple: (can_proceed, reason)
                - can_proceed: True if request can be made
                - reason: Explanation if request cannot be made
        """
        with self.lock:
            self._cleanup_old_records()

            current_rpm = len(self.requests)
            current_tpm = sum(r.tokens_used for r in self.requests)

            # Check RPM limit
            if current_rpm >= self.rpm_limit:
                rpm_pct = (current_rpm / self.rpm_limit * 100)
                return False, f"RPM limit reached ({current_rpm}/{self.rpm_limit} = {rpm_pct:.1f}%)"

            # Check TPM limit with estimated tokens
            if estimated_tokens > 0:
                projected_tpm = current_tpm + estimated_tokens
                if projected_tpm > self.tpm_limit:
                    tpm_pct = (projected_tpm / self.tpm_limit * 100)
                    return False, f"TPM limit would be exceeded ({projected_tpm:,}/{self.tpm_limit:,} = {tpm_pct:.1f}%)"

            return True, "OK"

    def record_request(self, tokens_used: int):
        """
        Record a completed API request.

        Args:
            tokens_used: Total tokens used (input + output)
        """
        with self.lock:
            record = RequestRecord(
                timestamp=time.time(),
                tokens_used=tokens_used
            )
            self.requests.append(record)

            # Log usage after recording
            current_rpm, current_tpm = self.get_current_usage()
            rpm_pct = (current_rpm / self.rpm_limit * 100) if self.rpm_limit > 0 else 0
            tpm_pct = (current_tpm / self.tpm_limit * 100) if self.tpm_limit > 0 else 0

            logger.debug(f"Request recorded: {tokens_used:,} tokens")
            logger.debug(f"  - RPM: {current_rpm}/{self.rpm_limit} ({rpm_pct:.1f}%)")
            logger.debug(f"  - TPM: {current_tpm:,}/{self.tpm_limit:,} ({tpm_pct:.1f}%)")

    def wait_if_needed(self, estimated_tokens: int = 0) -> float:
        """
        Wait if necessary to respect rate limits.

        Args:
            estimated_tokens: Estimated tokens for the next request

        Returns:
            float: Seconds waited (0 if no wait needed)
        """
        can_proceed, reason = self.can_make_request(estimated_tokens)

        if can_proceed:
            return 0.0

        # Calculate how long to wait
        with self.lock:
            if not self.requests:
                return 0.0

            # Wait until the oldest request expires
            oldest_timestamp = min(r.timestamp for r in self.requests)
            time_since_oldest = time.time() - oldest_timestamp
            wait_time = max(0, self.window_seconds - time_since_oldest + 1)  # +1 for safety margin

        logger.warning(f"[!] Rate limit approaching: {reason}")
        logger.info(f"  Waiting {wait_time:.1f}s before next request...")

        time.sleep(wait_time)
        return wait_time

    def get_stats(self) -> Dict:
        """
        Get current rate limiter statistics.

        Returns:
            dict: Statistics including usage, limits, and percentages
        """
        current_rpm, current_tpm = self.get_current_usage()
        rpm_pct, tpm_pct = self.get_usage_percentage()

        return {
            "model": self.model_name,
            "current_rpm": current_rpm,
            "rpm_limit": self.rpm_limit,
            "rpm_percentage": rpm_pct,
            "current_tpm": current_tpm,
            "tpm_limit": self.tpm_limit,
            "tpm_percentage": tpm_pct,
            "window_seconds": self.window_seconds,
            "active_requests": len(self.requests)
        }

    def reset(self):
        """Reset all rate limiter records"""
        with self.lock:
            self.requests.clear()
            logger.info(f"[+] Rate limiter reset for {self.model_name}")


def get_rate_limiter_for_model(model_name: str, provider: str = "OpenAI") -> RateLimiter:
    """
    Create a rate limiter configured for a specific model.

    Args:
        model_name: Name of the model (e.g., "gpt-4o", "gpt-3.5-turbo")
        provider: Provider name (e.g., "OpenAI", "OpenRouter")

    Returns:
        RateLimiter: Configured rate limiter instance
    """
    # Try to find exact match
    limits = MODEL_LIMITS.get(model_name)

    # Try partial match for model families
    if not limits:
        for known_model, model_limits in MODEL_LIMITS.items():
            if known_model in model_name.lower() or model_name.lower() in known_model:
                limits = model_limits
                logger.info(f"Using limits for similar model: {known_model}")
                break

    # Fall back to default
    if not limits:
        limits = MODEL_LIMITS["default"]
        logger.warning(f"[!] Unknown model '{model_name}', using default limits")
        logger.debug(f"  - Default RPM: {limits['rpm']:,}")
        logger.debug(f"  - Default TPM: {limits['tpm']:,}")

    return RateLimiter(
        rpm_limit=limits["rpm"],
        tpm_limit=limits["tpm"],
        model_name=model_name
    )


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text (rough approximation).

    Uses the common heuristic: 1 token ≈ 4 characters for English text.

    Args:
        text: Input text

    Returns:
        int: Estimated token count
    """
    # Rough estimation: 1 token ≈ 4 characters
    return len(text) // 4


# Example usage
if __name__ == "__main__":
    # Example: Create rate limiter for GPT-4o
    limiter = get_rate_limiter_for_model("gpt-4o")

    # Check if request can be made
    can_proceed, reason = limiter.can_make_request(estimated_tokens=1000)
    print(f"Can make request: {can_proceed} - {reason}")

    # Record a request
    limiter.record_request(tokens_used=1500)

    # Get statistics
    stats = limiter.get_stats()
    print(f"Stats: {stats}")
