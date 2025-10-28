"""
Main entry point for the K2 Designer application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.k2_designer.views.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create the Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("K2 Designer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("K2 Designer Team")
    
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()