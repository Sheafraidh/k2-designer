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
                             QLineEdit, QPushButton, QLabel, QComboBox,
                             QListWidget, QMessageBox, QGroupBox, QAbstractItemView)
from PyQt6.QtCore import Qt

from ..models.base import Key


class KeyDialog(QDialog):
    """Dialog for creating and editing table keys (Primary, Foreign, Unique)."""

    def __init__(self, key: Key = None, available_columns: list = None,
                 available_tables: list = None, project=None, parent=None):
        super().__init__(parent)
        self.key = key
        self.available_columns = available_columns or []
        self.available_tables = available_tables or []
        self.project = project
        self.is_edit_mode = key is not None

        self._setup_ui()
        self._load_data()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Edit Key" if self.is_edit_mode else "Add Key")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Basic properties
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)

        # Key name
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        form_layout.addRow("Name *:", self.name_edit)

        # Key type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Primary Key", Key.PRIMARY)
        self.type_combo.addItem("Foreign Key", Key.FOREIGN)
        self.type_combo.addItem("Unique", Key.UNIQUE)
        form_layout.addRow("Type *:", self.type_combo)

        layout.addLayout(form_layout)

        # Columns selection
        columns_group = QGroupBox("Columns *")
        columns_layout = QVBoxLayout(columns_group)

        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.columns_list.addItems(self.available_columns)
        columns_layout.addWidget(self.columns_list)

        hint_label = QLabel("Select one or more columns for this key")
        hint_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        columns_layout.addWidget(hint_label)

        layout.addWidget(columns_group)

        # Foreign key specific fields
        self.fk_group = QGroupBox("Foreign Key Properties")
        fk_layout = QFormLayout(self.fk_group)
        fk_layout.setVerticalSpacing(8)

        # Referenced table
        self.ref_table_combo = QComboBox()
        self.ref_table_combo.setEditable(True)
        self.ref_table_combo.addItem("")  # Empty option
        self.ref_table_combo.addItems(self.available_tables)
        fk_layout.addRow("Referenced Table:", self.ref_table_combo)

        # Referenced columns
        self.ref_columns_edit = QLineEdit()
        self.ref_columns_edit.setPlaceholderText("e.g., ID or COL1, COL2")
        fk_layout.addRow("Referenced Columns:", self.ref_columns_edit)

        # On Delete action
        self.on_delete_combo = QComboBox()
        self.on_delete_combo.addItem("")  # Empty/default
        self.on_delete_combo.addItems(["CASCADE", "SET NULL", "NO ACTION", "RESTRICT"])
        fk_layout.addRow("On Delete:", self.on_delete_combo)

        # On Update action (optional, some databases support this)
        self.on_update_combo = QComboBox()
        self.on_update_combo.addItem("")  # Empty/default
        self.on_update_combo.addItems(["CASCADE", "SET NULL", "NO ACTION", "RESTRICT"])
        fk_layout.addRow("On Update:", self.on_update_combo)

        layout.addWidget(self.fk_group)

        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_data(self):
        """Load data if in edit mode."""
        if self.is_edit_mode and self.key:
            self.name_edit.setText(self.key.name)

            # Set key type
            index = self.type_combo.findData(self.key.key_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

            # Select columns
            for i in range(self.columns_list.count()):
                item = self.columns_list.item(i)
                if item.text() in self.key.columns:
                    item.setSelected(True)

            # Load foreign key properties if applicable
            if self.key.key_type == Key.FOREIGN:
                if self.key.referenced_table:
                    index = self.ref_table_combo.findText(self.key.referenced_table)
                    if index >= 0:
                        self.ref_table_combo.setCurrentIndex(index)
                    else:
                        # Set as custom text if not in list
                        self.ref_table_combo.setCurrentText(self.key.referenced_table)

                if self.key.referenced_columns:
                    self.ref_columns_edit.setText(", ".join(self.key.referenced_columns))

                if self.key.on_delete:
                    index = self.on_delete_combo.findText(self.key.on_delete)
                    if index >= 0:
                        self.on_delete_combo.setCurrentIndex(index)

                if self.key.on_update:
                    index = self.on_update_combo.findText(self.key.on_update)
                    if index >= 0:
                        self.on_update_combo.setCurrentIndex(index)

        # Update FK group visibility
        self._update_fk_visibility()

    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        self.type_combo.currentIndexChanged.connect(self._update_fk_visibility)

    def _update_fk_visibility(self):
        """Show/hide foreign key fields based on key type."""
        key_type = self.type_combo.currentData()
        self.fk_group.setVisible(key_type == Key.FOREIGN)

    def _on_ok(self):
        """Handle OK button click."""
        if not self._validate_form():
            return

        name = self.name_edit.text().strip()
        key_type = self.type_combo.currentData()

        # Get selected columns
        columns = []
        for item in self.columns_list.selectedItems():
            columns.append(item.text())

        # Get foreign key properties
        ref_table = None
        ref_columns = []
        on_delete = None
        on_update = None

        if key_type == Key.FOREIGN:
            ref_table = self.ref_table_combo.currentText().strip() or None
            ref_columns_str = self.ref_columns_edit.text().strip()
            if ref_columns_str:
                ref_columns = [c.strip() for c in ref_columns_str.split(",") if c.strip()]
            on_delete = self.on_delete_combo.currentText() or None
            on_update = self.on_update_combo.currentText() or None

        # Create or update key
        self.key = Key(
            name=name,
            columns=columns,
            key_type=key_type,
            referenced_table=ref_table,
            referenced_columns=ref_columns,
            on_delete=on_delete,
            on_update=on_update
        )

        self.accept()

    def _validate_form(self) -> bool:
        """Validate the form data."""
        name = self.name_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Key name is required.")
            self.name_edit.setFocus()
            return False

        # Check if at least one column is selected
        if not self.columns_list.selectedItems():
            QMessageBox.warning(self, "Validation Error", "Please select at least one column for the key.")
            return False

        # Validate foreign key specific fields
        key_type = self.type_combo.currentData()
        if key_type == Key.FOREIGN:
            ref_table = self.ref_table_combo.currentText().strip()
            ref_columns = self.ref_columns_edit.text().strip()

            if not ref_table:
                QMessageBox.warning(self, "Validation Error", "Referenced table is required for foreign keys.")
                self.ref_table_combo.setFocus()
                return False

            if not ref_columns:
                QMessageBox.warning(self, "Validation Error", "Referenced columns are required for foreign keys.")
                self.ref_columns_edit.setFocus()
                return False

        return True

    def get_key(self) -> Key:
        """Get the key object."""
        return self.key

