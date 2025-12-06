"""
K2 Designer - Database Schema Designer

Copyright (c) 2025 Karel Švejnoha
All rights reserved.

SPDX-License-Identifier: AGPL-3.0-only OR Commercial

This software is dual-licensed:
- AGPL-3.0: Free for personal use, education, research, and internal use.
  Any modifications or derivative works must remain open-source under AGPL.
- Commercial License: Required for closed-source products, commercial distribution,
  SaaS deployment, or use in proprietary systems.

You MAY use this project at your company internally at no cost.
You MAY NOT sell, sublicense, or redistribute it as a proprietary product
without a commercial agreement.

For commercial licensing, contact: sheafraidh@gmail.com
See LICENSE file for full terms.
"""

import sys
import os
import warnings
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.k2_designer.views.main_window import MainWindow

# Suppress macOS NSOpenPanel warnings
if sys.platform == "darwin":  # macOS
    os.environ["OBJC_SILENCE_GC_DEPRECATIONS"] = "YES"
    # Filter out specific macOS PyQt6 warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, 
                          message=".*NSOpenPanel.*overrides.*identifier.*")


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to show detailed error information for debugging."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow Ctrl+C to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Print detailed exception information to console
    print("\n" + "="*80)
    print("🚨 UNHANDLED EXCEPTION OCCURRED 🚨")
    print("="*80)
    print(f"Exception Type: {exc_type.__name__}")
    print(f"Exception Message: {exc_value}")
    print("\nFull Traceback:")
    print("-" * 40)
    
    # Print the full traceback
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    print("-" * 40)
    print("🔍 Debug Information:")
    print(f"   - Python Version: {sys.version}")
    print(f"   - Platform: {sys.platform}")
    print(f"   - Working Directory: {os.getcwd()}")
    
    # Show local variables in the failing frame if available
    if exc_traceback:
        tb = exc_traceback
        while tb.tb_next:
            tb = tb.tb_next  # Get the innermost frame
        
        frame = tb.tb_frame
        print(f"   - Failing Function: {frame.f_code.co_name}")
        print(f"   - Failing File: {frame.f_code.co_filename}:{tb.tb_lineno}")
        
        # Show local variables (be careful not to show sensitive data)
        if frame.f_locals:
            print("\n🔧 Local Variables in Failing Frame:")
            for name, value in frame.f_locals.items():
                try:
                    # Limit output length and avoid showing large objects
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."
                    print(f"   {name} = {value_str}")
                except:
                    print(f"   {name} = <unable to display>")
    
    print("="*80)
    print("💡 This detailed error information is shown for debugging purposes.")
    print("   In production, you may want to disable this by removing the")
    print("   sys.excepthook assignment in main.py")
    print("="*80 + "\n")


def main():
    """Main application entry point."""
    # Install global exception handler for debugging
    sys.excepthook = handle_exception
    
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