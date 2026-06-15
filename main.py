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

import logging
import logging.handlers
import os
import sys
import traceback
import warnings
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from k2gui.views.main_window import MainWindow

# Suppress macOS NSOpenPanel warnings
if sys.platform == "darwin":  # macOS
    os.environ["OBJC_SILENCE_GC_DEPRECATIONS"] = "YES"
    # Filter out specific macOS PySide6 warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning,
                          message=".*NSOpenPanel.*overrides.*identifier.*")


def setup_logging() -> logging.Logger:
    """Configure application-wide logging to console and rotating log file."""
    log_dir = Path.home() / '.k2designer'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'k2designer.log'

    dev_mode = os.environ.get('K2_DEV', '').lower() in ('1', 'true', 'yes')
    level = logging.DEBUG if dev_mode else logging.INFO

    fmt = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(name)s — %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    root = logging.getLogger()
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8',
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    return logging.getLogger(__name__)


logger = logging.getLogger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler — logs unhandled exceptions with full context."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical(
        "Unhandled exception: %s — %s\nPython %s | platform %s | cwd %s",
        exc_type.__name__, exc_value,
        sys.version, sys.platform, os.getcwd(),
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    if exc_traceback:
        tb = exc_traceback
        while tb.tb_next:
            tb = tb.tb_next
        frame = tb.tb_frame
        logger.critical(
            "Failing location: %s in %s:%d",
            frame.f_code.co_name, frame.f_code.co_filename, tb.tb_lineno,
        )
        if frame.f_locals:
            vars_lines = []
            for name, value in frame.f_locals.items():
                try:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:97] + "..."
                    vars_lines.append(f"  {name} = {value_str}")
                except Exception:
                    vars_lines.append(f"  {name} = <unable to display>")
            logger.debug("Local variables in failing frame:\n%s", "\n".join(vars_lines))


def main():
    """Main application entry point."""
    setup_logging()
    sys.excepthook = handle_exception

    # Suppress macOS-specific warnings on stderr
    if sys.platform == "darwin":

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

    # Set application icon
    from PySide6.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(__file__), 'k2gui', 'resources', 'k2_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Create the main window (but don't initialize content yet)
    main_window = MainWindow()

    # Show the main window to establish its position
    main_window.show()
    app.processEvents()  # Process events to get proper window geometry

    # Show splash screen (now parent window is properly positioned)
    from k2gui.dialogs.about_dialog import SplashScreen
    splash = SplashScreen(parent=main_window)
    splash.show()
    app.processEvents()  # Process events to ensure splash is shown

    # Now initialize the main window content "behind" the splash screen
    # This includes loading the last project, setting up UI, etc.
    main_window.initialize_content()
    app.processEvents()  # Process any UI updates

    # Close splash screen (will wait for minimum display time)
    splash.finish()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
