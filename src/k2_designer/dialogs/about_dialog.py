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

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap
import os


class AboutDialog(QDialog):
    """About dialog showing copyright, license, and application information."""

    def __init__(self, parent=None, as_splash=False):
        """
        Initialize the About dialog.

        Args:
            parent: Parent widget
            as_splash: If True, dialog behaves as a splash screen (no close button, frameless)
        """
        super().__init__(parent)
        self.as_splash = as_splash
        self._can_close = False
        self._setup_ui()

        if as_splash:
            # Remove window decorations for splash screen
            self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
            # Set minimum display time - allow closing after 1.5 seconds
            QTimer.singleShot(1500, self._allow_close)


    def _allow_close(self):
        """Mark that splash can be closed (after minimum display time)."""
        self._can_close = True

    def _center_on_parent(self):
        """Center the dialog on the parent window, or screen if no parent."""
        if self.parent():
            # Get parent window geometry
            parent_geometry = self.parent().geometry()
            # Calculate center position
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            # No parent, center on screen
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)

    def finish(self):
        """Close the splash screen (will wait for minimum display time if needed)."""
        if self._can_close:
            self.close()
        else:
            # Wait a bit and try again
            QTimer.singleShot(100, self.finish)

    def showEvent(self, event):
        """Override showEvent to center dialog when shown (parent is properly positioned by then)."""
        super().showEvent(event)
        # Center on parent after dialog is shown and parent is properly positioned
        QTimer.singleShot(0, self._center_on_parent)

    def _setup_ui(self):
        """Setup the UI components."""
        if self.as_splash:
            self.setWindowTitle("K2 Designer")
        else:
            self.setWindowTitle("About K2 Designer")

        # Set window icon
        from PyQt6.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'k2_icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Main content layout (image on left, text on right)
        content_layout = QHBoxLayout()

        # Left side - Image
        image_label = QLabel()
        # Get the path to the splash image
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
        image_path = os.path.join(resources_dir, 'k2_splash.png')

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Scale image to reasonable size if needed
            if pixmap.width() > 300:
                pixmap = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        else:
            # Fallback if image not found
            image_label.setText("K2\nDesigner")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(36)
            font.setBold(True)
            image_label.setFont(font)

        content_layout.addWidget(image_label)

        # Right side - Text content
        text_layout = QVBoxLayout()

        # Header with title
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Application name
        app_name_label = QLabel("K2 Designer")
        app_name_font = QFont()
        app_name_font.setPointSize(24)
        app_name_font.setBold(True)
        app_name_label.setFont(app_name_font)
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(app_name_label)

        # Version
        version_label = QLabel("Version 1.0.0")
        version_font = QFont()
        version_font.setPointSize(12)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(version_label)

        # Subtitle
        subtitle_label = QLabel("Visual Database Design Tool")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)

        text_layout.addLayout(header_layout)
        text_layout.addSpacing(10)

        # Copyright and brief info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(120)
        info_text.setHtml("""
        <p style="text-align: center;"><b>Copyright © 2025 Karel Švejnoha</b><br>
        All rights reserved.</p>
        
        <p style="text-align: center;">A powerful visual database design tool for creating ER diagrams 
        and managing database schemas.</p>
        """)
        text_layout.addWidget(info_text)

        # License toggle link
        self.license_link = QLabel('<a href="#" style="text-decoration: none;">▶ Show License Information</a>')
        self.license_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.license_link.setTextFormat(Qt.TextFormat.RichText)
        self.license_link.setOpenExternalLinks(False)
        self.license_link.linkActivated.connect(self._toggle_license)
        self.license_link.setCursor(Qt.CursorShape.PointingHandCursor)
        text_layout.addWidget(self.license_link)

        # License information (initially hidden)
        self.license_text = QTextEdit()
        self.license_text.setReadOnly(True)
        self.license_text.setVisible(False)
        self.license_text.setHtml("""
        <h3>Dual License</h3>
        
        <p>This software is Copyright © 2025 Karel Švejnoha. All rights reserved.</p>
        
        <p>This project is available under a dual-license model:</p>
        
        <h4>1. Open Source License: GNU Affero General Public License v3.0 (AGPL-3.0)</h4>
        
        <p>You are free to use, study, modify, and distribute this software under the 
        terms of the AGPL-3.0. Any derivative work or software incorporating this 
        project must also be released under the AGPL-3.0 license and its complete 
        source code must be made publicly available.</p>
        
        <p><b>You MAY:</b></p>
        <ul>
            <li>Use this software for personal use, education, and research</li>
            <li>Use this software internally at your company at no cost</li>
            <li>Modify and study the source code</li>
            <li>Distribute modifications under AGPL-3.0</li>
        </ul>
        
        <p><b>You MAY NOT (without a commercial license):</b></p>
        <ul>
            <li>Sell, sublicense, or redistribute as a proprietary product</li>
            <li>Use in closed-source commercial products</li>
            <li>Offer as a SaaS service</li>
            <li>Include in proprietary systems without releasing source code</li>
        </ul>
        
        <p>Full AGPL-3.0 text: <a href="https://www.gnu.org/licenses/agpl-3.0.en.html">
        https://www.gnu.org/licenses/agpl-3.0.en.html</a></p>
        
        <h4>2. Commercial License</h4>
        
        <p>A separate closed-source commercial license is available for companies or 
        individuals who wish to use this software:</p>
        <ul>
            <li>Without releasing derivative source code</li>
            <li>As part of a proprietary/commercial product</li>
            <li>For resale, SaaS hosting, or redistribution</li>
            <li>With additional support or custom terms</li>
        </ul>
        
        <p><b>To obtain a commercial license, please contact:</b><br>
        Email: <a href="mailto:sheafraidh@gmail.com">sheafraidh@gmail.com</a></p>
        
        <p><i>Unless expressly stated otherwise in writing, no other rights are granted. 
        If you obtained this software under the AGPL-3.0 license, you must comply 
        with all of its terms.</i></p>
        
        <p><b>This project remains the intellectual property of the original author.</b></p>
        """)

        text_layout.addWidget(self.license_text)

        content_layout.addLayout(text_layout)
        layout.addLayout(content_layout)

        # Button layout
        if not self.as_splash:
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            close_button = QPushButton("Close")
            close_button.clicked.connect(self.accept)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

    def _toggle_license(self):
        """Toggle the visibility of the license information."""
        if self.license_text.isVisible():
            # Hide license
            self.license_text.setVisible(False)
            self.license_link.setText('<a href="#" style="text-decoration: none;">▶ Show License Information</a>')
            # Resize dialog to smaller size
            self.resize(700, 400)
        else:
            # Show license
            self.license_text.setVisible(True)
            self.license_link.setText('<a href="#" style="text-decoration: none;">▼ Hide License Information</a>')
            # Resize dialog to larger size
            self.resize(700, 700)

        # Re-center after resize
        self._center_on_parent()

    def mousePressEvent(self, event):
        """Allow clicking to close splash screen."""
        if self.as_splash:
            self.accept()
        else:
            super().mousePressEvent(event)


class SplashScreen(AboutDialog):
    """Splash screen variant of the About dialog."""

    def __init__(self, parent=None):
        """Initialize the splash screen."""
        super().__init__(parent, as_splash=True)

