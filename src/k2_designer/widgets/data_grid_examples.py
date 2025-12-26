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

"""
Example demonstrating how to use DataGridWidget for different use cases.

This file shows how to:
1. Use DataGridWidget for managing database keys
2. Use DataGridWidget for managing indexes
3. Customize the widget with callbacks and custom buttons
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QHeaderView, QMessageBox)
from .data_grid_widget import DataGridWidget, ColumnConfig


class KeysGridExample(QDialog):
    """Example dialog using DataGridWidget for managing database keys."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Keys")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Create and configure the grid
        self.grid = DataGridWidget()

        # Define columns for keys
        columns = [
            ColumnConfig(
                name="Name",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Type",
                width=120,
                resize_mode=QHeaderView.ResizeMode.Fixed,
                editor_type="combobox",
                editor_options={'items': ['PRIMARY', 'FOREIGN', 'UNIQUE']},
                filter_type="combobox",
                filter_options={'items': ['All', 'PRIMARY', 'FOREIGN', 'UNIQUE']}
            ),
            ColumnConfig(
                name="Columns",
                width=200,
                resize_mode=QHeaderView.ResizeMode.Stretch,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Referenced Table",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Referenced Columns",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="On Delete",
                width=120,
                resize_mode=QHeaderView.ResizeMode.Fixed,
                editor_type="combobox",
                editor_options={'items': ['', 'CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']},
                filter_type="combobox",
                filter_options={'items': ['All', 'CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']}
            ),
        ]

        # Configure the grid
        self.grid.configure(
            columns=columns,
            show_filters=True,
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=False  # Keys usually don't need ordering
        )

        # Connect to signals
        self.grid.data_changed.connect(self._on_data_changed)
        self.grid.row_added.connect(self._on_row_added)

        layout.addWidget(self.grid)

        # Add some sample data
        self._add_sample_data()

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _add_sample_data(self):
        """Add sample key data."""
        self.grid.add_row(["PK_EMPLOYEES", "PRIMARY", "EMPLOYEE_ID", "", "", ""])
        self.grid.add_row(["FK_DEPT", "FOREIGN", "DEPARTMENT_ID", "DEPARTMENTS", "DEPARTMENT_ID", "CASCADE"])
        self.grid.add_row(["UK_EMAIL", "UNIQUE", "EMAIL", "", "", ""])

    def _on_data_changed(self):
        """Handle data changes."""
        print("Keys data changed!")

    def _on_row_added(self, row):
        """Handle row addition."""
        print(f"Key added at row {row}")

    def get_keys(self):
        """Get all keys data."""
        return self.grid.get_all_data()


class IndexesGridExample(QDialog):
    """Example dialog using DataGridWidget for managing database indexes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Indexes")
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        # Create and configure the grid
        self.grid = DataGridWidget()

        # Define columns for indexes
        columns = [
            ColumnConfig(
                name="Name",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Columns",
                width=200,
                resize_mode=QHeaderView.ResizeMode.Stretch,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Unique",
                width=80,
                resize_mode=QHeaderView.ResizeMode.Fixed,
                editor_type="checkbox",
                filter_type="combobox",
                filter_options={'items': ['All', 'Yes', 'No']}
            ),
            ColumnConfig(
                name="Tablespace",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
        ]

        # Add a custom button for index analysis
        custom_buttons = [
            {
                'text': '📊',
                'tooltip': 'Analyze Index',
                'callback': self._analyze_index,
                'style': 'font-size: 14px;'
            }
        ]

        # Configure the grid
        self.grid.configure(
            columns=columns,
            show_filters=True,
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=True,  # Indexes might need ordering
            custom_buttons=custom_buttons
        )

        layout.addWidget(self.grid)

        # Add some sample data
        self._add_sample_data()

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _add_sample_data(self):
        """Add sample index data."""
        self.grid.add_row(["IDX_EMP_NAME", "LAST_NAME, FIRST_NAME", False, "USERS"])
        self.grid.add_row(["IDX_EMP_DEPT", "DEPARTMENT_ID", False, "USERS"])
        self.grid.add_row(["IDX_EMP_EMAIL", "EMAIL", True, "USERS"])

    def _analyze_index(self):
        """Custom callback for analyzing an index."""
        current_row = self.grid.table.currentRow()
        if current_row >= 0:
            data = self.grid.get_row_data(current_row)
            QMessageBox.information(
                self,
                "Index Analysis",
                f"Analyzing index:\n\nName: {data[0]}\nColumns: {data[1]}\nUnique: {data[2]}\nTablespace: {data[3]}"
            )
        else:
            QMessageBox.warning(self, "No Selection", "Please select an index to analyze.")

    def get_indexes(self):
        """Get all indexes data."""
        return self.grid.get_all_data()


class ColumnsGridExample(QDialog):
    """Example dialog using DataGridWidget for managing table columns with advanced features."""

    def __init__(self, available_domains=None, available_stereotypes=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Columns")
        self.resize(900, 600)

        self.available_domains = available_domains or []
        self.available_stereotypes = available_stereotypes or []

        layout = QVBoxLayout(self)

        # Create and configure the grid
        self.grid = DataGridWidget()

        # Define columns
        columns = [
            ColumnConfig(
                name="Name",
                width=120,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Data Type",
                width=130,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Nullable",
                width=80,
                resize_mode=QHeaderView.ResizeMode.Fixed,
                editor_type="checkbox",
                filter_type="combobox",
                filter_options={'items': ['All', 'Nullable', 'Not Nullable']}
            ),
            ColumnConfig(
                name="Default",
                width=100,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Comment",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Stretch,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Domain",
                width=120,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="combobox",
                editor_options={'items': [''] + self.available_domains},
                filter_type="combobox",
                filter_options={
                    'items': ['All', 'No Domain'] + self.available_domains,
                    'editable': True
                }
            ),
            ColumnConfig(
                name="Stereotype",
                width=120,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="combobox",
                editor_options={'items': [''] + self.available_stereotypes},
                filter_type="combobox",
                filter_options={
                    'items': ['All', 'No Stereotype'] + self.available_stereotypes,
                    'editable': True
                }
            ),
        ]

        # Add custom button for CSV import
        custom_buttons = [
            {
                'text': 'Import CSV...',
                'tooltip': 'Import Columns from CSV',
                'callback': self._import_csv,
                'style': 'min-width: 80px; height: 28px;'
            }
        ]

        # Configure the grid
        self.grid.configure(
            columns=columns,
            show_filters=True,
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=True,
            custom_buttons=custom_buttons
        )

        # Set custom cell setup for handling domain/stereotype widgets
        self.grid.set_cell_setup_callback(self._setup_custom_cell)

        layout.addWidget(self.grid)

        # Add some sample data
        self._add_sample_data()

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _setup_custom_cell(self, row: int, col: int, value):
        """Custom cell setup callback."""
        # Can add custom logic here if needed
        pass

    def _add_sample_data(self):
        """Add sample column data."""
        self.grid.add_row(["ID", "NUMBER(18,0)", False, "", "Primary key", "", ""])
        self.grid.add_row(["NAME", "VARCHAR2(100)", False, "", "Entity name", "", ""])
        self.grid.add_row(["DESCRIPTION", "VARCHAR2(4000)", True, "NULL", "Description", "", ""])
        self.grid.add_row(["CREATED_DATE", "DATE", False, "SYSDATE", "Creation timestamp", "", ""])

    def _import_csv(self):
        """Custom callback for CSV import."""
        QMessageBox.information(
            self,
            "Import CSV",
            "This would open a CSV import dialog.\n\nSee csv_import_dialog.py for full implementation."
        )

    def get_columns(self):
        """Get all columns data."""
        return self.grid.get_all_data()


# Example usage in code:
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Example 1: Keys grid
    # keys_dialog = KeysGridExample()
    # keys_dialog.exec()

    # Example 2: Indexes grid
    # indexes_dialog = IndexesGridExample()
    # indexes_dialog.exec()

    # Example 3: Columns grid
    columns_dialog = ColumnsGridExample(
        available_domains=["ID_DOMAIN", "NAME_DOMAIN", "DATE_DOMAIN"],
        available_stereotypes=["PK", "FK", "AUDIT"]
    )
    columns_dialog.exec()

    sys.exit(0)

