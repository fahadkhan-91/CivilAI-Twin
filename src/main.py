"""
CivilAI Twin - AI Engineer for Infrastructure
Main application entry point
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for both normal and frozen (PyInstaller) execution
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = str(Path(__file__).parent)

sys.path.insert(0, application_path)

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
from loguru import logger

from gui.main_window import MainWindow
from utils.config import ConfigManager
from utils.logger import setup_logging


def create_splash_screen():
    """Create and show splash screen"""
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.GlobalColor.white)
    
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    
    font = QFont("Arial", 16, QFont.Weight.Bold)
    splash.setFont(font)
    
    splash.showMessage(
        "CivilAI Twin\nAI Engineer for Infrastructure\n\nLoading...",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.black
    )
    
    return splash


def main():
    """Main application entry point"""
    
    # Setup logging
    setup_logging()
    logger.info("Starting CivilAI Twin application")
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("CivilAI Twin")
    app.setOrganizationName("CivilAI")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Show splash screen
    splash = create_splash_screen()
    splash.show()
    app.processEvents()
    
    try:
        # Initialize configuration
        logger.info("Initializing configuration manager")
        config_manager = ConfigManager()
        
        # Create main window
        logger.info("Creating main application window")
        main_window = MainWindow(config_manager)
        
        # Close splash screen and show main window
        QTimer.singleShot(2000, splash.close)
        QTimer.singleShot(2000, main_window.show)
        
        logger.info("Application started successfully")
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.exception(f"Critical error during application startup: {e}")
        splash.close()
        raise


if __name__ == "__main__":
    main()
