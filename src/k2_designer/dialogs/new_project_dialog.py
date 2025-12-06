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


from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class NewProjectDialog(QDialog):
    """Dialog for creating new projects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        self._setup_ui()
        self._connect_signals()
        
        # Set focus to name field
        self.name_edit.setFocus()
        self.name_edit.selectAll()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Create New Project")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Project details group
        project_group = QGroupBox("Project Details")
        project_layout = QFormLayout(project_group)
        
        # Project name
        self.name_edit = QLineEdit("Untitled Project")
        self.name_edit.setMaxLength(100)
        self.name_edit.setPlaceholderText("Enter project name...")
        project_layout.addRow("Project Name:", self.name_edit)
        
        # Project description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Optional project description...")
        project_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(project_group)
        
        # Future enhancements section (placeholder)
        # future_group = QGroupBox("Database Connection")
        # future_layout = QFormLayout(future_group)
        # 
        # self.connection_combo = QComboBox()
        # self.connection_combo.addItem("Local SQLite (Default)", "sqlite")
        # self.connection_combo.setEnabled(False)  # Disabled for now
        # future_layout.addRow("Connection Type:", self.connection_combo)
        # 
        # layout.addWidget(future_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Create Project")
        self.ok_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        
        # Enable/disable OK button based on name field
        self.name_edit.textChanged.connect(self._on_name_changed)
    
    def _on_name_changed(self, text):
        """Handle name field changes."""
        # Enable OK button only if name is not empty
        self.ok_button.setEnabled(bool(text.strip()))
    
    def _on_ok(self):
        """Handle OK button click."""
        if not self._validate_form():
            return
        
        self.accept()
    
    def _validate_form(self):
        """Validate form data."""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(
                self, "Validation Error",
                "Project name is required."
            )
            self.name_edit.setFocus()
            return False
        
        return True
    
    def get_project_name(self) -> str:
        """Get the entered project name."""
        return self.name_edit.text().strip()
    
    def get_project_description(self) -> str:
        """Get the entered project description."""
        description = self.description_edit.toPlainText().strip()
        return description if description else None