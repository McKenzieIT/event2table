#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging Module
Centralized logging configuration for the application
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from backend.core.config import LogConfig, BASE_DIR


class Logger:
    """Centralized logger class"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name (usually __name__ from the calling module)

        Returns:
            Configured logger instance
        """
        if name is None:
            name = "dwd_generator"

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(getattr(logging, LogConfig.LOG_LEVEL))

            # Remove existing handlers
            logger.handlers.clear()

            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)

            # Create formatter
            formatter = logging.Formatter(LogConfig.LOG_FORMAT, datefmt=LogConfig.LOG_DATE_FORMAT)
            console_handler.setFormatter(formatter)

            # Add handler to logger
            logger.addHandler(console_handler)

            # Create file handler (optional)
            log_file = BASE_DIR / "logs" / "dwd_generator.log"
            log_file.parent.mkdir(exist_ok=True)

            try:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except (IOError, OSError) as e:
                # If we can't create log file, continue with console logging only
                logger.warning(f"Could not create log file: {e}")

            cls._loggers[name] = logger

        return cls._loggers[name]


# Convenience functions for easy access
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance"""
    return Logger.get_logger(name)


def debug(message: str, *args, **kwargs):
    """Log a debug message"""
    get_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """Log an info message"""
    get_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """Log a warning message"""
    get_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """Log an error message"""
    get_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """Log a critical message"""
    get_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """Log an exception with traceback"""
    get_logger().exception(message, *args, **kwargs)
