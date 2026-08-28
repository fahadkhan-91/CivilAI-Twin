"""
Logging utilities for CivilAI Twin
"""

import sys
import os
from pathlib import Path
from loguru import logger


def setup_logging():
    """Configure logging for the application"""
    
    # Remove default handler
    logger.remove()
    
    # Determine base directory based on execution mode
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        # Use the directory where the EXE is located
        base_dir = Path(sys.executable).parent
    else:
        # Running as script
        base_dir = Path(__file__).parent.parent.parent
    
    # Create logs directory
    log_dir = base_dir / "logs"
    try:
        log_dir.mkdir(exist_ok=True)
    except Exception as e:
        # If we can't create logs folder, use temp directory
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / "CivilAI_Twin_Logs"
        log_dir.mkdir(exist_ok=True)
    
    # Console handler (INFO and above) - only if stderr is available
    if sys.stderr is not None:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True
        )
    
    # File handler (DEBUG and above)
    try:
        logger.add(
            str(log_dir / "civilai_twin.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
    except Exception as e:
        # If file logging fails, continue with console only
        print(f"Warning: Could not setup file logging: {e}")
        pass
    
    # Error file handler (ERROR and above)
    try:
        logger.add(
            str(log_dir / "errors.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention="14 days",
            compression="zip"
        )
    except Exception as e:
        # If error file logging fails, continue with console only
        print(f"Warning: Could not setup error logging: {e}")
        pass
    
    logger.info(f"Logging system initialized - Log directory: {log_dir}")
