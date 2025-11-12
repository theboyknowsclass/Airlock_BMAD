"""
Logging utilities for Airlock Common
"""
import logging
import sys
from typing import Optional


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
):
    """
    Setup structured logging for the application
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format string
        date_format: Date format string
    
    Example:
        >>> setup_logging(log_level="INFO")
    """
    import os
    
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello, world!")
    """
    return logging.getLogger(name)

