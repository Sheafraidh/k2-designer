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
                             QCheckBox, QComboBox, QHeaderView, QMessageBox,
                             QTabWidget, QWidget, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..models import Table, Column
from ..models.base import Stereotype, StereotypeType
from ..widgets import DataGridWidget, ColumnConfig




class TableDialog(QDialog):
    """Dialog for creating and editing table objects."""
    
    def __init__(self, table: Table = None, owners: list = None, selected_owner: str = None, 
                 project=None, parent=None):
        super().__init__(parent)
        self.table = table
        self.owners = owners or []
        self.selected_owner = selected_owner
        self.project = project
        self.is_edit_mode = table is not None
        
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Edit Table" if self.is_edit_mode else "Add Table")
        self.setModal(True)
        self.resize(750, 500)  # Increased width to accommodate all columns including domain
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins around dialog
        layout.setSpacing(5)  # Reduced spacing between elements
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Basic properties tab
        basic_tab = QWidget()
        self._setup_basic_tab(basic_tab)
        self.tab_widget.addTab(basic_tab, "Basic Properties")
        
        # Columns tab
        columns_tab = QWidget()
        self._setup_columns_tab(columns_tab)
        self.tab_widget.addTab(columns_tab, "Columns")
        
        # Keys tab
        keys_tab = QWidget()
        self._setup_keys_tab(keys_tab)
        self.tab_widget.addTab(keys_tab, "Keys")

        # Indexes tab
        indexes_tab = QWidget()
        self._setup_indexes_tab(indexes_tab)
        self.tab_widget.addTab(indexes_tab, "Indexes")

        layout.addWidget(self.tab_widget)
        
        # Move tips to the bottom
        self.tips_label = QLabel("Tips: • Multi-select: Ctrl+click to toggle, Shift+click for range • Navigation: Enter moves to next row, Tab moves to next column • Filtering: Use filter controls above to find specific columns")
        self.tips_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        self.tips_label.setWordWrap(True)
        layout.addWidget(self.tips_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 5, 0, 0)  # Small margin only on top
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _setup_basic_tab(self, tab_widget):
        """Setup the basic properties tab."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins within tab
        layout.setSpacing(5)  # Reduced spacing between elements
        
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)  # Reduced vertical spacing between form rows
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        form_layout.addRow("Name *:", self.name_edit)
        
        self.owner_combo = QComboBox()
        self.owner_combo.addItems([owner.name for owner in self.owners])
        form_layout.addRow("Owner *:", self.owner_combo)
        
        self.tablespace_edit = QLineEdit()
        self.tablespace_edit.setMaxLength(100)
        form_layout.addRow("Tablespace:", self.tablespace_edit)
        
        self.stereotype_combo = QComboBox()
        self._populate_stereotypes()
        form_layout.addRow("Stereotype:", self.stereotype_combo)
        
        # Color picker setup
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("Choose Color")
        self.color_button.setFixedWidth(100)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(50, 30)
        self.color_preview.setStyleSheet("border: 1px solid black; background-color: #FFFFFF;")
        self.color_preview.setToolTip("Current color")
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        
        # Store current color value
        self.current_color = "#4C4C4C"
        self._color_manually_set = False
        
        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        form_layout.addRow("Color:", color_widget)
        
        self.editionable_check = QCheckBox()
        form_layout.addRow("Editionable:", self.editionable_check)
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(60)  # Reduced height for more compact design
        form_layout.addRow("Comment:", self.comment_edit)
        
        layout.addLayout(form_layout)
        
        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)
        
        layout.addStretch()
    
    def _setup_columns_tab(self, tab_widget):
        """Setup the columns tab using DataGridWidget."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create the columns grid widget
        self.columns_grid = DataGridWidget()

        # Define columns - will be configured after we have project data
        # This is done in _configure_columns_grid() which is called from _load_data()

        layout.addWidget(self.columns_grid)

        # Bottom button - Import from CSV
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        bottom_layout.setSpacing(5)

        self.import_csv_btn = QPushButton("Import from CSV...")
        self.import_csv_btn.clicked.connect(self._import_from_csv)
        bottom_layout.addWidget(self.import_csv_btn)
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

    def _configure_columns_grid(self):
        """Configure the columns grid with column definitions."""
        # Get available domains
        domain_items = [""]
        domain_items_data = [""]
        if self.project and hasattr(self.project, 'domains'):
            for domain in self.project.domains:
                domain_items.append(domain.name)
                domain_items_data.append(domain.name)

        # Get available stereotypes
        stereotype_items = [""]
        stereotype_items_data = [""]
        if self.project and hasattr(self.project, 'stereotypes'):
            for stereotype in self.project.stereotypes:
                if stereotype.stereotype_type.value == 'column':
                    stereotype_items.append(stereotype.name)
                    stereotype_items_data.append(stereotype.name)

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
                editor_type="checkbox_centered",
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
                editor_type="combobox_data",
                editor_options={'items': domain_items, 'items_data': domain_items_data},
                filter_type="combobox",
                filter_options={'items': ['All', 'No Domain'] + domain_items[1:], 'editable': True}
            ),
            ColumnConfig(
                name="Stereotype",
                width=120,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="combobox_data",
                editor_options={'items': stereotype_items, 'items_data': stereotype_items_data},
                filter_type="combobox",
                filter_options={'items': ['All', 'No Stereotype'] + stereotype_items[1:], 'editable': True}
            ),
        ]

        # Configure the grid
        self.columns_grid.configure(
            columns=columns,
            show_filters=True,
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=True
        )

        # Set custom cell setup callback for domain-related functionality
        self.columns_grid.set_cell_setup_callback(self._setup_column_cell)

        # Connect signals
        self.columns_grid.data_changed.connect(self._on_columns_changed)

        # Store reference to the table for compatibility
        self.columns_table = self.columns_grid.table

    def _setup_column_cell(self, row: int, col: int, value):
        """Custom cell setup for columns grid."""
        # Column 5 is Domain - set up domain change handler
        if col == 5:
            domain_combo = self.columns_grid.get_cell_widget(row, col)
            if domain_combo and isinstance(domain_combo, QComboBox):
                # Disconnect any existing connections
                try:
                    domain_combo.currentTextChanged.disconnect()
                except:
                    pass
                # Connect to domain change handler
                domain_combo.currentTextChanged.connect(
                    lambda text, r=row: self._on_domain_changed(r, text)
                )
                # Update data type editability based on current domain
                self._update_data_type_editability(row, value)

        # Column 6 is Stereotype - set up stereotype change handler
        elif col == 6:
            stereotype_combo = self.columns_grid.get_cell_widget(row, col)
            if stereotype_combo and isinstance(stereotype_combo, QComboBox):
                # Disconnect any existing connections
                try:
                    stereotype_combo.currentTextChanged.disconnect()
                except:
                    pass
                # Connect to stereotype change handler
                stereotype_combo.currentTextChanged.connect(
                    lambda text, r=row: self._on_stereotype_changed(r, text)
                )

    def _on_columns_changed(self):
        """Handle columns data change."""
        # This could be used for tracking modifications
        pass

    def _setup_keys_tab(self, tab_widget):
        """Setup the keys tab with DataGridWidget."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create DataGridWidget for keys
        from ..widgets import DataGridWidget, ColumnConfig
        from ..models.base import Key

        self.keys_grid = DataGridWidget()

        # Define columns for keys grid
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
                editor_type="combobox_data",
                editor_options={
                    'items': ['PRIMARY', 'FOREIGN', 'UNIQUE'],
                    'items_data': [Key.PRIMARY, Key.FOREIGN, Key.UNIQUE]
                },
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
        self.keys_grid.configure(
            columns=columns,
            show_filters=True,  # Enable filters for keys
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=True
        )

        layout.addWidget(self.keys_grid)

        # Info label
        info_label = QLabel("Tips: • Type: PRIMARY, FOREIGN, or UNIQUE • Columns: comma-separated list • For Foreign Keys: specify Referenced Table and Columns")
        info_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def _setup_indexes_tab(self, tab_widget):
        """Setup the indexes tab with DataGridWidget."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create DataGridWidget for indexes
        from ..widgets import DataGridWidget, ColumnConfig

        self.indexes_grid = DataGridWidget()

        # Get all unique tablespaces from owners
        tablespace_items = [""]  # Empty option
        if self.owners:
            tablespaces = set()
            for owner in self.owners:
                if owner.default_tablespace:
                    tablespaces.add(owner.default_tablespace)
                if owner.temp_tablespace:
                    tablespaces.add(owner.temp_tablespace)
                if owner.default_index_tablespace:
                    tablespaces.add(owner.default_index_tablespace)
            tablespace_items.extend(sorted(tablespaces))

        # Define columns for indexes grid
        columns = [
            ColumnConfig(
                name="Name",
                width=200,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Columns",
                width=300,
                resize_mode=QHeaderView.ResizeMode.Stretch,
                editor_type="text",
                filter_type="text"
            ),
            ColumnConfig(
                name="Tablespace",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="combobox",
                editor_options={'items': tablespace_items},
                filter_type="combobox",
                filter_options={'items': ['All'] + tablespace_items}
            ),
        ]

        # Configure the grid
        self.indexes_grid.configure(
            columns=columns,
            show_filters=True,  # Enable filters for indexes
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=True
        )

        # Set custom callback to default tablespace for new rows
        self.indexes_grid.set_cell_setup_callback(self._setup_index_cell)

        layout.addWidget(self.indexes_grid)

        # Info label
        info_label = QLabel("Tips: • Name: Index name • Columns: comma-separated list of columns • Tablespace: Defaults to owner's index tablespace")
        info_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def _populate_stereotypes(self):
        """Populate stereotype combo with project stereotypes."""
        self.stereotype_combo.clear()
        self.stereotype_combo.addItem("")  # Empty option
        
        if self.project and hasattr(self.project, 'stereotypes'):
            table_stereotypes = [s for s in self.project.stereotypes 
                               if s.stereotype_type == StereotypeType.TABLE]
            for stereotype in table_stereotypes:
                self.stereotype_combo.addItem(stereotype.name)
    
    def _load_data(self):
        """Load data if in edit mode."""
        # Configure columns grid first (needs project data for domains/stereotypes)
        self._configure_columns_grid()

        if self.is_edit_mode and self.table:
            self.name_edit.setText(self.table.name)
            
            # Set owner
            owner_index = self.owner_combo.findText(self.table.owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)
            
            self.tablespace_edit.setText(self.table.tablespace or "")
            self.stereotype_combo.setCurrentText(self.table.stereotype or "")
            self._set_color(self.table.color or "#FFFFFF")
            self._color_manually_set = bool(self.table.color)  # Mark as manually set if table has a specific color
            self.editionable_check.setChecked(self.table.editionable)
            self.comment_edit.setPlainText(self.table.comment or "")
            
            # Load columns
            self._load_columns()
            
            # Load keys
            self._load_keys()

            # Load indexes
            self._load_indexes()

            # Name is now editable in edit mode (removed read-only restriction)
        elif self.selected_owner:
            # Pre-select owner in add mode
            owner_index = self.owner_combo.findText(self.selected_owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)

    def _load_columns(self):
        """Load columns into the grid."""
        if not self.table:
            return
        
        self.columns_grid.clear_data()

        for column in self.table.columns:
            # Add row with column data
            self.columns_grid.add_row([
                column.name,
                column.data_type,
                column.nullable,
                column.default or "",
                column.comment or "",
                column.domain or "",
                column.stereotype or ""
            ])

    def _load_keys(self):
        """Load keys into the keys grid."""
        if not self.table:
            return

        # Clear existing rows
        self.keys_grid.clear_data()

        # Add keys from table
        for key in self.table.keys:
            # Convert key to row data
            columns_str = ", ".join(key.columns) if key.columns else ""
            ref_columns_str = ", ".join(key.referenced_columns) if key.referenced_columns else ""

            row_data = [
                key.name,
                key.key_type,  # Will match the data value in combobox
                columns_str,
                key.referenced_table or "",
                ref_columns_str,
                key.on_delete or ""
            ]

            self.keys_grid.add_row(row_data)

    def _load_indexes(self):
        """Load indexes into the indexes grid."""
        if not self.table:
            return

        # Clear existing rows
        self.indexes_grid.clear_data()

        # Add indexes from table
        for index in self.table.indexes:
            # Convert index to row data
            columns_str = ", ".join(index.columns) if index.columns else ""

            row_data = [
                index.name,
                columns_str,
                index.tablespace or ""
            ]

            self.indexes_grid.add_row(row_data)

    def _on_domain_changed(self, row, domain_name):
        """Handle domain selection change for a column."""
        if not domain_name:  # Empty domain selected
            # Make data type editable
            self._update_data_type_editability(row, "")
            return
        
        # Find the domain and set its data type
        if self.project and hasattr(self.project, 'domains'):
            domain = next((d for d in self.project.domains if d.name == domain_name), None)
            if domain:
                # Set data type from domain
                data_type_item = self.columns_grid.get_cell_item(row, 1)
                if data_type_item:
                    data_type_item.setText(domain.data_type)
                
                # Make data type non-editable
                self._update_data_type_editability(row, domain_name)
    
    def _update_data_type_editability(self, row, domain_name):
        """Update whether the data type cell is editable based on domain selection."""
        data_type_item = self.columns_grid.get_cell_item(row, 1)
        if data_type_item:
            if domain_name:  # Domain selected
                # Make non-editable with gray text
                data_type_item.setFlags(data_type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                data_type_item.setForeground(QColor(128, 128, 128))  # Gray text color
            else:  # No domain selected
                # Make editable with default system text color
                data_type_item.setFlags(data_type_item.flags() | Qt.ItemFlag.ItemIsEditable)
                # Reset to default text color (matches other columns automatically)
                data_type_item.setData(Qt.ItemDataRole.ForegroundRole, None)
    
    def _on_stereotype_changed(self, row, stereotype_name):
        """Handle stereotype selection change for a single row."""
        # Stereotype doesn't affect other columns, just store the selection
        # The value will be read when saving the table
        pass
    
    def _setup_index_cell(self, row: int, col: int, value):
        """Custom cell setup for indexes grid."""
        # Column 2 is Tablespace - set default from owner's index tablespace for new rows
        if col == 2 and not value:  # Only set default if value is empty
            tablespace_combo = self.indexes_grid.get_cell_widget(row, col)
            if tablespace_combo and isinstance(tablespace_combo, QComboBox):
                # Get current owner's default index tablespace
                current_owner = self.owner_combo.currentText()
                if current_owner and self.owners:
                    owner = next((o for o in self.owners if o.name == current_owner), None)
                    if owner and owner.default_index_tablespace:
                        # Set to owner's default index tablespace
                        index = tablespace_combo.findText(owner.default_index_tablespace)
                        if index >= 0:
                            tablespace_combo.setCurrentIndex(index)

    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        
        self.color_button.clicked.connect(self._choose_color)
        self.stereotype_combo.currentTextChanged.connect(self._on_table_stereotype_changed)

        # Import CSV button (not part of grid widget)
        # (already connected in _setup_columns_tab)

    def _import_from_csv(self):
        """Import columns from CSV data."""
        from .csv_import_dialog import CSVImportDialog

        dialog = CSVImportDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            columns = dialog.get_columns()

            if columns:
                # Ask if user wants to append or replace
                current_row_count = self.columns_grid.table.rowCount()
                if current_row_count > 0:
                    reply = QMessageBox.question(
                        self,
                        "Import Columns",
                        f"You have {current_row_count} existing columns.\n\n"
                        "Do you want to:\n"
                        "- Yes: Append imported columns to existing ones\n"
                        "- No: Replace all existing columns\n"
                        "- Cancel: Cancel import",
                        QMessageBox.StandardButton.Yes |
                        QMessageBox.StandardButton.No |
                        QMessageBox.StandardButton.Cancel,
                        QMessageBox.StandardButton.Yes
                    )

                    if reply == QMessageBox.StandardButton.Cancel:
                        return
                    elif reply == QMessageBox.StandardButton.No:
                        # Clear existing columns
                        self.columns_grid.clear_data()

                # Import the columns
                for col_data in columns:
                    # col_data has: name, data_type, nullable, default, comment
                    self.columns_grid.add_row([
                        col_data.get('name', ''),
                        col_data.get('data_type', ''),
                        col_data.get('nullable', True),
                        col_data.get('default', ''),
                        col_data.get('comment', ''),
                        '',  # domain
                        ''   # stereotype
                    ])

                # Show success message
                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Successfully imported {len(columns)} columns."
                )

    
    def _choose_color(self):
        """Open color picker dialog."""
        current_color = QColor(self.current_color)
        color = QColorDialog.getColor(current_color, self, "Choose Table Color")
        
        if color.isValid():
            self._set_color(color.name())
            self._color_manually_set = True
    
    def _set_color(self, color_hex: str):
        """Set the current color and update the preview."""
        self.current_color = color_hex
        self.color_preview.setStyleSheet(f"border: 1px solid black; background-color: {color_hex};")
        self.color_preview.setToolTip(f"Current color: {color_hex}")
    
    def _on_table_stereotype_changed(self, text=None):
        """Handle table stereotype change to update default color."""
        # Auto-update color based on stereotype if color hasn't been manually set
        if not self.is_edit_mode or not hasattr(self, '_color_manually_set'):
            # Only auto-update color if not in edit mode or color hasn't been manually set
            stereotype_name = text if text is not None else self.stereotype_combo.currentText()

            if stereotype_name and self.project and hasattr(self.project, 'stereotypes'):
                # Find the stereotype in project stereotypes
                stereotype = None
                for s in self.project.stereotypes:
                    if s.name == stereotype_name and s.stereotype_type == StereotypeType.TABLE:
                        stereotype = s
                        break
                
                if stereotype:
                    self._set_color(stereotype.background_color)
                else:
                    # Default color if stereotype not found
                    self._set_color("#464646")
            else:
                # Default color for empty stereotype
                self._set_color("#464646")
    
    def _on_ok(self):
        """Handle OK button click."""
        if not self._validate_form():
            return
        
        name = self.name_edit.text().strip()
        owner = self.owner_combo.currentText()
        tablespace = self.tablespace_edit.text().strip() or None
        stereotype = self.stereotype_combo.currentText() or None
        color = self.current_color if self.current_color != "#FFFFFF" else None
        editionable = self.editionable_check.isChecked()
        comment = self.comment_edit.toPlainText().strip() or None
        
        if self.is_edit_mode:
            # Update existing table
            self.table.name = name  # Allow name changes
            self.table.owner = owner  # Allow owner changes
            self.table.tablespace = tablespace
            self.table.stereotype = stereotype
            self.table.color = color
            self.table.editionable = editionable
            self.table.comment = comment
            
            # Update columns
            self._update_table_columns()
        else:
            # Create new table
            self.table = Table(
                name=name,
                owner=owner,
                tablespace=tablespace,
                stereotype=stereotype,
                color=color,
                editionable=editionable,
                comment=comment
            )
            
            # Add columns
            self._update_table_columns()
        
        # Refresh active diagram if it exists
        self._refresh_active_diagram()

        self.accept()
    
    def _update_table_columns(self):
        """Update table columns from the grid widget."""
        if not self.table:
            return
        
        # Commit any active editor before reading data
        self.columns_grid.commit_active_editor()

        # Clear existing columns
        self.table.columns.clear()
        
        # Add columns from grid widget
        for row_data in self.columns_grid.get_all_data():
            name, data_type, nullable, default, comment, domain, stereotype = row_data

            # Skip empty rows
            name = name.strip() if isinstance(name, str) else str(name)
            data_type = data_type.strip() if isinstance(data_type, str) else str(data_type)

            if name and data_type:
                column = Column(
                    name=name,
                    data_type=data_type,
                    nullable=bool(nullable),
                    default=default.strip() if default and isinstance(default, str) and default.strip() else None,
                    comment=comment.strip() if comment and isinstance(comment, str) and comment.strip() else None,
                    domain=domain if domain else None,
                    stereotype=stereotype if stereotype else None
                )
                self.table.add_column(column)

        # Update keys
        self._update_table_keys()

        # Update indexes
        self._update_table_indexes()

    def _update_table_keys(self):
        """Update table keys from the keys grid widget."""
        from ..models.base import Key

        if not self.table:
            return

        # Commit any active editor before reading data
        self.keys_grid.commit_active_editor()

        # Clear existing keys
        self.table.keys.clear()

        # Add keys from grid widget
        for row_data in self.keys_grid.get_all_data():
            name, key_type, columns_str, ref_table, ref_columns_str, on_delete = row_data

            # Convert to strings first
            name = str(name) if name else ""
            columns_str = str(columns_str) if columns_str else ""
            ref_table = str(ref_table) if ref_table else ""
            ref_columns_str = str(ref_columns_str) if ref_columns_str else ""
            on_delete = str(on_delete) if on_delete else ""

            # Parse columns
            columns = [c.strip() for c in columns_str.split(",") if c.strip()] if columns_str else []

            # Parse referenced columns
            ref_columns = [c.strip() for c in ref_columns_str.split(",") if c.strip()] if ref_columns_str else []

            # Clean up empty strings - keep value if it has content after stripping
            ref_table = ref_table.strip() if ref_table and ref_table.strip() else None
            ref_columns = ref_columns if ref_columns else None
            on_delete = on_delete.strip() if on_delete and on_delete.strip() else None

            # Only add keys with name and columns
            if name.strip() and columns:
                key = Key(
                    name=name.strip(),
                    columns=columns,
                    key_type=key_type,
                    referenced_table=ref_table,
                    referenced_columns=ref_columns,
                    on_delete=on_delete
                )
                self.table.add_key(key)

    def _update_table_indexes(self):
        """Update table indexes from the indexes grid widget."""
        from ..models.base import Index

        if not self.table:
            return

        # Commit any active editor before reading data
        self.indexes_grid.commit_active_editor()

        # Clear existing indexes
        self.table.indexes.clear()

        # Add indexes from grid widget
        for row_data in self.indexes_grid.get_all_data():
            name, columns_str, tablespace = row_data

            # Convert to strings and parse columns
            name = str(name) if name else ""
            columns_str = str(columns_str) if columns_str else ""
            tablespace = str(tablespace) if tablespace else ""

            # Parse columns
            columns = [c.strip() for c in columns_str.split(",") if c.strip()] if columns_str else []

            # Clean up tablespace - keep it if it has content, otherwise None
            tablespace = tablespace.strip() if tablespace and tablespace.strip() else None

            # Only add indexes with name and columns
            if name.strip() and columns:
                index = Index(
                    name=name.strip(),
                    columns=columns,
                    tablespace=tablespace
                )
                self.table.add_index(index)

    def _refresh_active_diagram(self):
        """Refresh the active diagram to show updated table structure."""
        # Find the main window
        main_window = self.parent()
        while main_window and main_window.__class__.__name__ != 'MainWindow':
            main_window = main_window.parent()

        if main_window and hasattr(main_window, 'tab_widget'):
            # Get the current active tab
            current_tab = main_window.tab_widget.currentWidget()

            # Check if it's a diagram view
            if current_tab and hasattr(current_tab, 'refresh_diagram'):
                # Refresh the diagram to show changes
                current_tab.refresh_diagram()

    def _validate_form(self) -> bool:
        """Validate the form data."""
        name = self.name_edit.text().strip()
        owner = self.owner_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Table name is required.")
            self.name_edit.setFocus()
            return False
        
        if not owner:
            QMessageBox.warning(self, "Validation Error", "Owner is required.")
            self.owner_combo.setFocus()
            return False
        
        # Validate columns
        for row in range(self.columns_table.rowCount()):
            name_item = self.columns_table.item(row, 0)
            data_type_item = self.columns_table.item(row, 1)
            
            if name_item and name_item.text().strip():
                if not data_type_item or not data_type_item.text().strip():
                    QMessageBox.warning(
                        self, "Validation Error", 
                        f"Data type is required for column '{name_item.text().strip()}'."
                    )
                    return False
        
        return True
    
    def update_table(self):
        """Update the table object and notify parent of changes."""
        # Find the main window to emit object modification signal
        main_window = self.parent()
        while main_window and main_window.__class__.__name__ != 'MainWindow':
            main_window = main_window.parent()
        
        if main_window and hasattr(main_window, '_on_object_modified'):
            # Notify main window that the table was modified
            main_window._on_object_modified(self.table)
    
    def get_table(self) -> Table:
        """Get the table object."""
        return self.table

