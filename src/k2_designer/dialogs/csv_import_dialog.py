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


import csv
from io import StringIO
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QComboBox, QCheckBox,
                             QGroupBox, QFormLayout, QFileDialog, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CSVImportDialog(QDialog):
    """Dialog for importing columns from CSV data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Columns from CSV")
        self.setMinimumSize(800, 600)
        self.imported_columns = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Import Columns from CSV")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Instructions
        info_label = QLabel(
            "Paste CSV data below or load from a file. "
            "Expected format: column_name, data_type, nullable, default, comment"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)

        # Options group
        options_group = QGroupBox("Import Options")
        options_layout = QFormLayout()

        # Delimiter
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItem("Comma (,)", ",")
        self.delimiter_combo.addItem("Tab", "\t")
        self.delimiter_combo.addItem("Semicolon (;)", ";")
        self.delimiter_combo.addItem("Pipe (|)", "|")
        self.delimiter_combo.currentIndexChanged.connect(self._preview_data)
        options_layout.addRow("Delimiter:", self.delimiter_combo)

        # Quote character
        self.quote_combo = QComboBox()
        self.quote_combo.addItem('Double quote (")', '"')
        self.quote_combo.addItem("Single quote (')", "'")
        self.quote_combo.addItem("None", "")
        self.quote_combo.currentIndexChanged.connect(self._preview_data)
        options_layout.addRow("Quote character:", self.quote_combo)

        # Has header row
        self.header_check = QCheckBox("First row contains headers")
        self.header_check.setChecked(True)
        self.header_check.stateChanged.connect(self._preview_data)
        options_layout.addRow("", self.header_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Input area
        input_group = QGroupBox("CSV Data")
        input_layout = QVBoxLayout()

        # Buttons for input
        button_row = QHBoxLayout()
        self.paste_btn = QPushButton("Paste from Clipboard")
        self.paste_btn.clicked.connect(self._paste_from_clipboard)
        self.load_btn = QPushButton("Load from File...")
        self.load_btn.clicked.connect(self._load_from_file)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_input)

        button_row.addWidget(self.paste_btn)
        button_row.addWidget(self.load_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addStretch()
        input_layout.addLayout(button_row)

        # Text area
        self.csv_text = QTextEdit()
        self.csv_text.setPlaceholderText(
            "Paste or type CSV data here...\n\n"
            "Example with headers:\n"
            "name,data_type,nullable,default,comment\n"
            "ID,NUMBER(10),NO,,Primary key\n"
            "NAME,VARCHAR2(100),NO,,Employee name\n"
            "EMAIL,VARCHAR2(100),YES,,Email address\n\n"
            "Or without headers (assumes: name, data_type, nullable, default, comment):\n"
            "ID,NUMBER(10),NO,,Primary key\n"
            "NAME,VARCHAR2(100),NO,,Employee name"
        )
        self.csv_text.textChanged.connect(self._preview_data)
        input_layout.addWidget(self.csv_text)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(5)
        self.preview_table.setHorizontalHeaderLabels([
            "Column Name", "Data Type", "Nullable", "Default", "Comment"
        ])
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.setAlternatingRowColors(True)
        preview_layout.addWidget(self.preview_table)

        self.preview_status = QLabel("")
        self.preview_status.setStyleSheet("color: #666; font-style: italic;")
        preview_layout.addWidget(self.preview_status)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _paste_from_clipboard(self):
        """Paste data from clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if text:
            self.csv_text.setPlainText(text)
            self.preview_status.setText("✓ Data pasted from clipboard")
        else:
            QMessageBox.warning(self, "Clipboard Empty", "No text data found in clipboard.")

    def _load_from_file(self):
        """Load data from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load CSV File",
            "",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.csv_text.setPlainText(content)
                self.preview_status.setText(f"✓ Data loaded from: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def _clear_input(self):
        """Clear the input text."""
        self.csv_text.clear()
        self.preview_status.setText("")

    def _preview_data(self):
        """Preview the parsed CSV data."""
        text = self.csv_text.toPlainText().strip()

        if not text:
            self.preview_table.setRowCount(0)
            self.preview_status.setText("")
            return

        try:
            delimiter = self.delimiter_combo.currentData()
            quote_char = self.quote_combo.currentData()
            has_header = self.header_check.isChecked()

            # Parse CSV
            if quote_char:
                reader = csv.reader(StringIO(text), delimiter=delimiter, quotechar=quote_char)
            else:
                reader = csv.reader(StringIO(text), delimiter=delimiter, quoting=csv.QUOTE_NONE)

            rows = list(reader)

            if not rows:
                self.preview_table.setRowCount(0)
                self.preview_status.setText("No data to preview")
                return

            # Skip header if present
            data_rows = rows[1:] if has_header else rows

            # Update preview table
            self.preview_table.setRowCount(len(data_rows))

            for row_idx, row in enumerate(data_rows):
                # Pad row to have 5 columns
                while len(row) < 5:
                    row.append("")

                for col_idx in range(5):
                    value = row[col_idx].strip() if col_idx < len(row) else ""
                    item = QTableWidgetItem(value)
                    self.preview_table.setItem(row_idx, col_idx, item)

            self.preview_status.setText(f"✓ Preview: {len(data_rows)} columns will be imported")

        except Exception as e:
            self.preview_table.setRowCount(0)
            self.preview_status.setText(f"✗ Parse error: {str(e)}")

    def _on_accept(self):
        """Validate and accept the import."""
        text = self.csv_text.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "No Data", "Please enter or paste CSV data.")
            return

        try:
            delimiter = self.delimiter_combo.currentData()
            quote_char = self.quote_combo.currentData()
            has_header = self.header_check.isChecked()

            # Parse CSV
            if quote_char:
                reader = csv.reader(StringIO(text), delimiter=delimiter, quotechar=quote_char)
            else:
                reader = csv.reader(StringIO(text), delimiter=delimiter, quoting=csv.QUOTE_NONE)

            rows = list(reader)

            # Skip header if present
            data_rows = rows[1:] if has_header else rows

            if not data_rows:
                QMessageBox.warning(self, "No Data", "No data rows found to import.")
                return

            # Convert to column data
            self.imported_columns = []
            for row in data_rows:
                if not row or not row[0].strip():
                    continue  # Skip empty rows

                # Pad row to have at least 5 columns
                while len(row) < 5:
                    row.append("")

                column_data = {
                    'name': row[0].strip(),
                    'data_type': row[1].strip() if len(row) > 1 else 'VARCHAR2(50)',
                    'nullable': self._parse_nullable(row[2].strip() if len(row) > 2 else 'YES'),
                    'default': row[3].strip() if len(row) > 3 else '',
                    'comment': row[4].strip() if len(row) > 4 else ''
                }

                # Validate required fields
                if not column_data['name']:
                    continue  # Skip rows without name
                if not column_data['data_type']:
                    column_data['data_type'] = 'VARCHAR2(50)'  # Default type

                self.imported_columns.append(column_data)

            if not self.imported_columns:
                QMessageBox.warning(self, "Invalid Data", "No valid columns found to import.")
                return

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to parse CSV data:\n{str(e)}")

    def _parse_nullable(self, value):
        """Parse nullable value from string."""
        if not value:
            return True

        value_upper = value.upper()

        # Check for "NO" values
        if value_upper in ('NO', 'N', 'FALSE', 'F', '0', 'NOT NULL'):
            return False

        # Check for "YES" values
        if value_upper in ('YES', 'Y', 'TRUE', 'T', '1', 'NULL'):
            return True

        # Default to True (nullable)
        return True

    def get_columns(self):
        """Get the imported column data."""
        return self.imported_columns

