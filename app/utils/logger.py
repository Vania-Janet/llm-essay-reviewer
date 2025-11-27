"""
Centralized logging configuration for the application.

Usage:
    from app.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("User logged in")
    logger.error("Failed to process", exc_info=True)
"""
import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger (typically __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if logger.handlers:
        return logger
    
    # Determine log level from environment
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        level = logging.INFO
    elif env == 'testing':
        level = logging.WARNING
    else:
        level = logging.DEBUG
    
    logger.setLevel(level)
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format for console
    if env == 'development':
        # More detailed format for development
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Simpler format for production
        console_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler for production (rotating logs)
    if env == 'production':
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# Pre-configured loggers for common use cases
def get_auth_logger():
    """Get logger for authentication operations."""
    return get_logger('app.auth')


def get_db_logger():
    """Get logger for database operations."""
    return get_logger('app.database')


def get_api_logger():
    """Get logger for API operations."""
    return get_logger('app.api')


def get_evaluation_logger():
    """Get logger for essay evaluation operations."""
    return get_logger('app.evaluation')
