"""
logger.py - Centralized logging configuration for Medical Services Mapping

Features:
- Colored console output (INFO and above)
- Detailed file logging (DEBUG and above)
- Automatic daily log rotation
- Structured log format
- Easy integration across modules

Usage:
    from core.logger import get_logger, log_exception

    logger = get_logger(__name__)
    logger.info("Processing started")

    try:
        risky_operation()
    except Exception as e:
        log_exception(logger, "Operation failed", e)
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colorama colors for console output"""

    # Color mapping for different log levels
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    # Symbols for each log level (Windows-safe ASCII)
    SYMBOLS = {
        logging.DEBUG: "[D]",
        logging.INFO: "[+]",
        logging.WARNING: "[!]",
        logging.ERROR: "[X]",
        logging.CRITICAL: "[!!]",
    }

    def format(self, record):
        """Format the log record with colors and symbols"""
        # Get color for this level
        color = self.COLORS.get(record.levelno, Fore.WHITE)

        # Get symbol for this level
        symbol = self.SYMBOLS.get(record.levelno, "•")

        # Add symbol and color to levelname
        record.levelname = f"{color}{symbol} {record.levelname}{Style.RESET_ALL}"

        # Color the message
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"

        return super().format(record)


def setup_logger(
    name: str = "MappingService",
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs",
    console_level: int = None,
    file_level: int = None,
    max_bytes: int = 100 * 1024 * 1024,  # 100 MB (increased to prevent rotation during batch processing)
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up and return a configured logger.

    Args:
        name: Logger name
        level: Default logging level (used if console_level/file_level not specified)
        log_to_file: Whether to also log to file
        log_dir: Directory for log files
        console_level: Specific level for console (default: level)
        file_level: Specific level for file (default: DEBUG)
        max_bytes: Maximum size of each log file
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance

    Example:
        >>> from core.logger import setup_logger
        >>> logger = setup_logger()
        >>> logger.info("Processing started")
        >>> logger.error("Failed to connect", exc_info=True)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture everything, handlers will filter

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # Set levels
    console_level = console_level or level
    file_level = file_level or logging.DEBUG

    # ===== Console Handler (with colors) =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console_handler)

    # ===== File Handler (detailed, with rotation) =====
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Create filename with date
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = log_path / f"mapping_service_{timestamp}.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get an existing logger or create a new one.

    Args:
        name: Logger name (defaults to calling module name)

    Returns:
        Logger instance

    Example:
        >>> from core.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Started processing")
    """
    if name is None:
        name = "MappingService"

    logger = logging.getLogger(name)

    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)

    return logger


# Create default logger instance for simple imports
logger = setup_logger()


def log_exception(logger_instance, message: str, exc: Exception = None):
    """
    Log an exception with full stack trace.

    Args:
        logger_instance: Logger instance
        message: Error message
        exc: Exception object (optional)

    Example:
        >>> try:
        >>>     risky_operation()
        >>> except Exception as e:
        >>>     log_exception(logger, "Operation failed", e)
    """
    if exc:
        logger_instance.exception(f"{message}: {type(exc).__name__}: {exc}")
    else:
        logger_instance.exception(message)


def log_api_call(logger_instance, provider: str, model: str, tokens: dict, latency: float, success: bool = True):
    """
    Log an API call with structured information.

    Args:
        logger_instance: Logger instance
        provider: API provider (OpenAI, OpenRouter)
        model: Model name
        tokens: Dict with 'input', 'output', 'total' keys
        latency: Response time in seconds
        success: Whether call succeeded

    Example:
        >>> log_api_call(
        >>>     logger,
        >>>     provider="OpenAI",
        >>>     model="gpt-4o",
        >>>     tokens={'input': 1000, 'output': 500, 'total': 1500},
        >>>     latency=2.5,
        >>>     success=True
        >>> )
    """
    status = "SUCCESS" if success else "FAILED"
    msg = (f"API Call [{status}] | Provider: {provider} | Model: {model} | "
           f"Tokens: {tokens.get('total', 0):,} (in: {tokens.get('input', 0):,}, out: {tokens.get('output', 0):,}) | "
           f"Latency: {latency:.2f}s")
    logger_instance.info(msg)

    # Also print to stdout for Streamlit console capture (in async threads, logger might not reach Streamlit)
    try:
        import builtins
        color = Fore.GREEN if success else Fore.RED
        builtins.print(f"{color}[+] {msg}{Style.RESET_ALL}")
    except:
        pass  # Ignore print failures in async context
