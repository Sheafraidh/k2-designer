"""
Main entry point for the K2 Designer application.
"""

import sys
import os
import warnings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.k2_designer.views.main_window import MainWindow

# Suppress macOS NSOpenPanel warnings
if sys.platform == "darwin":  # macOS
    os.environ["OBJC_SILENCE_GC_DEPRECATIONS"] = "YES"
    # Filter out specific macOS PyQt6 warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, 
                          message=".*NSOpenPanel.*overrides.*identifier.*")


def main():
    """Main application entry point."""
    # Suppress macOS-specific warnings on stderr
    if sys.platform == "darwin":
        import io
        import contextlib
        
        class StderrFilter:
            def __init__(self, original_stderr):
                self.original_stderr = original_stderr
                
            def write(self, message):
                # Filter out the NSOpenPanel warning
                if "NSOpenPanel" not in message and "overrides the method identifier" not in message:
                    self.original_stderr.write(message)
                    
            def flush(self):
                self.original_stderr.flush()
                
            def fileno(self):
                return self.original_stderr.fileno()
        
        sys.stderr = StderrFilter(sys.stderr)
    
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