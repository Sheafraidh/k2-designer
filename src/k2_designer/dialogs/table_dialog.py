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
import copy

from ..models import Table, Column
from ..models.base import Stereotype, StereotypeType
from ..controllers.naming_rules_engine import NamingRulesEngine
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
        
        # Initialize naming rules engine
        self.naming_engine = NamingRulesEngine()

        # Backup original state for Cancel functionality
        self._original_table_state = None
        if self.table:
            self._backup_table_state()

        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _get_available_tables(self):
        """Get list of available tables from the project."""
        tables = []
        if self.project and hasattr(self.project, 'tables'):
            for table in self.project.tables:
                tables.append(f"{table.owner}.{table.name}")
        return tables

    def _get_available_columns(self):
        """Get list of columns from current table."""
        columns = []
        # Check if columns_grid is configured (table widget exists)
        if not hasattr(self, 'columns_grid') or not hasattr(self.columns_grid, 'table') or self.columns_grid.table is None:
            return columns

        # Get columns from the grid (includes unsaved changes)
        for row in range(self.columns_grid.table.rowCount()):
            name_item = self.columns_grid.get_cell_item(row, 0)
            if name_item:
                col_name = name_item.text().strip()
                if col_name:
                    columns.append(col_name)
        return columns

    def _backup_table_state(self):
        """Backup the original table state for Cancel functionality."""
        if not self.table:
            return

        # Deep copy all table attributes to preserve original state
        self._original_table_state = {
            'name': self.table.name,
            'owner': self.table.owner,
            'tablespace': self.table.tablespace,
            'stereotype': self.table.stereotype,
            'color': self.table.color,
            'editionable': self.table.editionable,
            'comment': self.table.comment,
            'columns': copy.deepcopy(self.table.columns),
            'keys': copy.deepcopy(self.table.keys),
            'indexes': copy.deepcopy(self.table.indexes)
        }

    def _restore_table_state(self):
        """Restore the original table state when Cancel is clicked."""
        if not self.table or not self._original_table_state:
            return

        # Restore all attributes from backup
        self.table.name = self._original_table_state['name']
        self.table.owner = self._original_table_state['owner']
        self.table.tablespace = self._original_table_state['tablespace']
        self.table.stereotype = self._original_table_state['stereotype']
        self.table.color = self._original_table_state['color']
        self.table.editionable = self._original_table_state['editionable']
        self.table.comment = self._original_table_state['comment']
        self.table.columns = copy.deepcopy(self._original_table_state['columns'])
        self.table.keys = copy.deepcopy(self._original_table_state['keys'])
        self.table.indexes = copy.deepcopy(self._original_table_state['indexes'])

    def _get_columns_for_table(self, table_name: str):
        """Get list of columns from a specific table in the project."""
        columns = []
        if not self.project or not hasattr(self.project, 'tables'):
            return columns

        # Find the table in the project
        for table in self.project.tables:
            table_full_name = f"{table.owner}.{table.name}"
            # Match by full name or just table name
            if table_full_name == table_name or table.name == table_name:
                # Get columns from the table
                for col in table.columns:
                    columns.append(col.name)
                break

        return columns

    def _connect_ref_table_signals(self):
        """Connect Referenced Table combobox signals to update Referenced Columns."""
        from PyQt6.QtWidgets import QComboBox
        from ..models.base import Key

        if not hasattr(self, 'keys_grid') or not hasattr(self.keys_grid, 'table') or not self.keys_grid.table:
            return

        for row in range(self.keys_grid.table.rowCount()):
            # Get widgets for this row
            key_type_widget = self.keys_grid.get_cell_widget(row, 1)
            ref_table_widget = self.keys_grid.get_cell_widget(row, 3)
            ref_cols_widget = self.keys_grid.get_cell_widget(row, 4)

            # Check current key type and clear Referenced fields if not FOREIGN
            if isinstance(key_type_widget, QComboBox):
                key_type = key_type_widget.currentData()

                # For PRIMARY and UNIQUE keys, ensure Referenced fields are empty
                if key_type != Key.FOREIGN:
                    if isinstance(ref_table_widget, QComboBox):
                        # Only clear if it has a value
                        if ref_table_widget.currentText():
                            ref_table_widget.setCurrentText("")

                    if isinstance(ref_cols_widget, QComboBox):
                        # Only clear if it has a value
                        if ref_cols_widget.currentText():
                            ref_cols_widget.setCurrentText("")

                # Disconnect any existing key type change connections
                try:
                    key_type_widget.currentIndexChanged.disconnect()
                except:
                    pass

                # Connect to clear Referenced fields when changing to non-FK type
                if isinstance(ref_table_widget, QComboBox) and isinstance(ref_cols_widget, QComboBox):
                    key_type_widget.currentIndexChanged.connect(
                        lambda idx, r=row, rt=ref_table_widget, rc=ref_cols_widget: (
                            rt.setCurrentText("") if self.keys_grid.get_cell_widget(r, 1).currentData() != Key.FOREIGN else None,
                            rc.setCurrentText("") if self.keys_grid.get_cell_widget(r, 1).currentData() != Key.FOREIGN else None
                        )
                    )

            # Connect Referenced Table changes for FK keys
            if isinstance(ref_table_widget, QComboBox) and isinstance(ref_cols_widget, QComboBox):
                # Disconnect any existing connections
                try:
                    ref_table_widget.currentTextChanged.disconnect()
                except:
                    pass

                # Connect signal to update Referenced Columns
                def make_handler(ref_cols_combo):
                    def handler(text):
                        if text:
                            ref_columns = self._get_columns_for_table(text)
                            current_value = ref_cols_combo.currentText()
                            ref_cols_combo.clear()
                            ref_cols_combo.addItems(ref_columns)
                            # Clear the selection since we're changing tables
                            ref_cols_combo.setCurrentText("")
                    return handler

                ref_table_widget.currentTextChanged.connect(make_handler(ref_cols_widget))

    def _setup_ui(self):
        """Setup the UI components."""
        if self.is_edit_mode:
            title = f"Edit Table - {self.table.owner}.{self.table.name}"
        else:
            title = "Add Table"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(1000, 600)  # Larger size to accommodate all columns comfortably

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

        # Track previous tab for smart syncing
        self._previous_tab_index = 0

        # Connect tab change signal to refresh indexes when switching tabs
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

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

        # Get available tables and columns for autocomplete
        available_tables = self._get_available_tables()

        # Get columns from the table object if in edit mode, otherwise empty list
        available_columns = []
        if self.table and hasattr(self.table, 'columns'):
            available_columns = [col.name for col in self.table.columns]


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
                editor_type="combobox",
                editor_options={'items': available_columns, 'editable': True},
                filter_type="text"
            ),
            ColumnConfig(
                name="Referenced Table",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="combobox",
                editor_options={'items': available_tables, 'editable': True},
                filter_type="text"
            ),
            ColumnConfig(
                name="Referenced Columns",
                width=150,
                resize_mode=QHeaderView.ResizeMode.Interactive,
                editor_type="combobox",
                editor_options={'items': available_columns, 'editable': True},
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
            ColumnConfig(
                name="Index",
                width=60,
                resize_mode=QHeaderView.ResizeMode.Fixed,
                editor_type="checkbox_centered",
                filter_type="combobox",
                filter_options={'items': ['All', 'Has Index', 'No Index']}
            ),
        ]

        # Configure the grid
        self.keys_grid.configure(
            columns=columns,
            show_filters=True,  # Enable filters for keys
            show_add_button=True,
            show_edit_button=True,
            show_remove_button=True,
            show_move_buttons=True,
            custom_buttons=[
                {
                    'text': 'Add FK',
                    'tooltip': 'Add Foreign Key',
                    'callback': self._add_foreign_key,
                    'style': 'font-size: 12px; padding: 4px 8px;'
                },
                {
                    'text': 'Add UQ',
                    'tooltip': 'Add Unique Key',
                    'callback': self._add_unique_key,
                    'style': 'font-size: 12px; padding: 4px 8px;'
                }
            ]
        )

        # Set callback to auto-generate key names
        self.keys_grid.set_cell_setup_callback(self._setup_key_cell)

        # Connect when rows are added
        self.keys_grid.row_added.connect(lambda: self._connect_ref_table_signals())

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

        # Get columns from the table object if in edit mode, otherwise empty list
        available_columns = []
        if self.table and hasattr(self.table, 'columns'):
            available_columns = [col.name for col in self.table.columns]

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
                editor_type="combobox",
                editor_options={'items': available_columns, 'editable': True},
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

            # Calculate has_index based on associated_index_guid
            # The GUID is the single source of truth - don't automatically re-link by columns
            has_index = False
            if key.associated_index_guid:
                # Check if the associated index still exists
                for idx in self.table.indexes:
                    if idx.guid == key.associated_index_guid:
                        has_index = True
                        break

                # If index doesn't exist anymore, clear the stale GUID
                if not has_index:
                    key.associated_index_guid = None

            row_data = [
                key.name,
                key.key_type,  # Will match the data value in combobox
                columns_str,
                key.referenced_table or "",
                ref_columns_str,
                key.on_delete or "",
                has_index  # Calculated from existing indexes
            ]

            self.keys_grid.add_row(row_data)

        # After loading all keys, update the Columns comboboxes with current table's columns
        available_columns = self._get_available_columns()

        from ..models.base import Key

        for row in range(self.keys_grid.table.rowCount()):
            # Update Columns combobox (col 2)
            columns_widget = self.keys_grid.get_cell_widget(row, 2)
            if isinstance(columns_widget, QComboBox):
                current_value = columns_widget.currentText()
                columns_widget.clear()
                columns_widget.addItems(available_columns)
                if current_value:
                    columns_widget.setCurrentText(current_value)

            # Get the key type for this row
            key_type_widget = self.keys_grid.get_cell_widget(row, 1)
            key_type = key_type_widget.currentData() if isinstance(key_type_widget, QComboBox) else None

            # Only update Referenced Table and Referenced Columns for FOREIGN keys
            if key_type == Key.FOREIGN:
                # Update Referenced Columns combobox (col 4)
                ref_cols_widget = self.keys_grid.get_cell_widget(row, 4)
                if isinstance(ref_cols_widget, QComboBox):
                    # Get the referenced table
                    ref_table_widget = self.keys_grid.get_cell_widget(row, 3)
                    if isinstance(ref_table_widget, QComboBox):
                        ref_table = ref_table_widget.currentText()
                        if ref_table:
                            ref_columns = self._get_columns_for_table(ref_table)
                            current_value = ref_cols_widget.currentText()
                            ref_cols_widget.clear()
                            ref_cols_widget.addItems(ref_columns)
                            if current_value:
                                ref_cols_widget.setCurrentText(current_value)
            else:
                # For PRIMARY and UNIQUE keys, clear Referenced Table and Referenced Columns
                ref_table_widget = self.keys_grid.get_cell_widget(row, 3)
                if isinstance(ref_table_widget, QComboBox):
                    ref_table_widget.setCurrentText("")

                ref_cols_widget = self.keys_grid.get_cell_widget(row, 4)
                if isinstance(ref_cols_widget, QComboBox):
                    ref_cols_widget.setCurrentText("")


        # Connect Referenced Table signals after loading all keys
        self._connect_ref_table_signals()

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

        # After loading all indexes, update the Columns comboboxes with current table's columns
        available_columns = self._get_available_columns()

        for row in range(self.indexes_grid.table.rowCount()):
            # Update Columns combobox (col 1)
            columns_widget = self.indexes_grid.get_cell_widget(row, 1)
            if isinstance(columns_widget, QComboBox):
                current_value = columns_widget.currentText()
                columns_widget.clear()
                columns_widget.addItems(available_columns)
                if current_value:
                    columns_widget.setCurrentText(current_value)

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
    
    def _setup_key_cell(self, row: int, col: int, value):
        """Custom cell setup for keys grid to auto-generate names."""
        # Column 0 is Name - auto-generate if empty
        if col == 0 and not value:
            # Get current table name
            table_name = self.name_edit.text().strip()
            if not table_name:
                return

            # Get key type from column 1
            key_type_widget = self.keys_grid.get_cell_widget(row, 1)
            if key_type_widget and isinstance(key_type_widget, QComboBox):
                from ..models.base import Key
                key_type = key_type_widget.currentData()

                # Get columns from column 2
                columns_item = self.keys_grid.get_cell_item(row, 2)
                columns_str = columns_item.text() if columns_item else ""
                columns = [c.strip() for c in columns_str.split(',') if c.strip()]

                # Get referenced table for foreign keys
                referenced_table_item = self.keys_grid.get_cell_item(row, 3)
                referenced_table = referenced_table_item.text() if referenced_table_item else None

                # Generate name based on key type
                if key_type == Key.PRIMARY:
                    generated_name = self.naming_engine.generate_primary_key_name(
                        table_name, columns, self.table
                    )
                elif key_type == Key.FOREIGN:
                    generated_name = self.naming_engine.generate_foreign_key_name(
                        table_name, columns, referenced_table, self.table
                    )
                elif key_type == Key.UNIQUE:
                    generated_name = self.naming_engine.generate_unique_key_name(
                        table_name, columns, self.table
                    )
                else:
                    return

                # Set the generated name
                name_item = self.keys_grid.get_cell_item(row, 0)
                if name_item:
                    name_item.setText(generated_name)

    def _setup_index_cell(self, row: int, col: int, value):
        """Custom cell setup for indexes grid."""
        # Column 0 is Name - auto-generate if empty
        if col == 0 and not value:
            table_name = self.name_edit.text().strip()
            if table_name:
                # Create temporary table with existing indexes from grid to get correct count
                from ..models import Table as TempTable
                from ..models.base import Index
                temp_table = TempTable(name=table_name, owner=self.owner_combo.currentText())

                # Add existing indexes from grid to temp table for counting
                for grid_row in range(self.indexes_grid.table.rowCount()):
                    name_item = self.indexes_grid.get_cell_item(grid_row, 0)
                    name = name_item.text() if name_item else ""

                    if name.strip():
                        temp_index = Index(name=name.strip(), columns=[])
                        temp_table.add_index(temp_index)

                # Use naming engine to generate name with correct numbering
                generated_name = self.naming_engine.generate_index_name(
                    table_name, [], temp_table
                )

                # Set the generated name
                name_item = self.indexes_grid.get_cell_item(row, 0)
                if name_item:
                    name_item.setText(generated_name)

        # Column 2 is Tablespace - set default from owner's index tablespace for new rows
        elif col == 2 and not value:  # Only set default if value is empty
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

    def _add_foreign_key(self):
        """Add a new foreign key row with auto-generated name."""
        from ..models.base import Key

        # Get current table name
        table_name = self.name_edit.text().strip()
        if not table_name:
            QMessageBox.warning(self, "Table Name Required",
                              "Please enter a table name before adding keys.")
            return

        # Create temporary table with existing keys from grid to get correct count
        from ..models import Table as TempTable
        temp_table = TempTable(name=table_name, owner=self.owner_combo.currentText())

        # Add existing keys from grid to temp table for counting
        for row in range(self.keys_grid.table.rowCount()):
            key_type_widget = self.keys_grid.get_cell_widget(row, 1)
            if key_type_widget and isinstance(key_type_widget, QComboBox):
                key_type = key_type_widget.currentData()
                name_item = self.keys_grid.get_cell_item(row, 0)
                name = name_item.text() if name_item else ""

                if name and key_type:
                    temp_key = Key(name=name, columns=[], key_type=key_type)
                    temp_table.add_key(temp_key)

        # Use naming engine to generate name with correct numbering
        generated_name = self.naming_engine.generate_foreign_key_name(
            table_name, [], None, temp_table
        )

        # Add row with FK type pre-selected
        row_data = [
            generated_name,  # Name
            Key.FOREIGN,     # Type (will be matched by combobox_data)
            "",              # Columns
            "",              # Referenced Table
            "",              # Referenced Columns
            ""               # On Delete
        ]

        self.keys_grid.add_row(row_data)

    def _add_unique_key(self):
        """Add a new unique key row with auto-generated name."""
        from ..models.base import Key

        # Get current table name
        table_name = self.name_edit.text().strip()
        if not table_name:
            QMessageBox.warning(self, "Table Name Required",
                              "Please enter a table name before adding keys.")
            return

        # Create temporary table with existing keys from grid to get correct count
        from ..models import Table as TempTable
        temp_table = TempTable(name=table_name, owner=self.owner_combo.currentText())

        # Add existing keys from grid to temp table for counting
        for row in range(self.keys_grid.table.rowCount()):
            key_type_widget = self.keys_grid.get_cell_widget(row, 1)
            if key_type_widget and isinstance(key_type_widget, QComboBox):
                key_type = key_type_widget.currentData()
                name_item = self.keys_grid.get_cell_item(row, 0)
                name = name_item.text() if name_item else ""

                if name and key_type:
                    temp_key = Key(name=name, columns=[], key_type=key_type)
                    temp_table.add_key(temp_key)

        # Use naming engine to generate name with correct numbering
        generated_name = self.naming_engine.generate_unique_key_name(
            table_name, [], temp_table
        )

        # Add row with UNIQUE type pre-selected
        row_data = [
            generated_name,  # Name
            Key.UNIQUE,      # Type (will be matched by combobox_data)
            "",              # Columns
            "",              # Referenced Table (not used for UK)
            "",              # Referenced Columns (not used for UK)
            ""               # On Delete (not used for UK)
        ]

        self.keys_grid.add_row(row_data)

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
    
    def _on_tab_changed(self, index):
        """Handle tab change event to sync between Keys and Indexes tabs."""
        # Check if we're switching to the Keys tab (index 2: Basic=0, Columns=1, Keys=2, Indexes=3)
        if index == 2:  # Switching TO Keys tab
            # Always sync keys from indexes when entering Keys tab
            # This updates checkboxes based on what indexes exist
            self._sync_keys_from_indexes()
        # Check if we're switching to the Indexes tab
        elif index == 3:  # Switching TO Indexes tab
            # Only sync indexes from keys if we're coming FROM the Keys tab
            # (This prevents recreating indexes when just navigating between other tabs)
            if self._previous_tab_index == 2:  # Coming from Keys tab
                # First, commit any user changes from Keys grid to table.keys
                self._update_table_keys()
                # Then sync indexes based on updated keys
                self._sync_indexes_from_keys()

        # Remember current tab for next time
        self._previous_tab_index = index

    def _sync_indexes_from_keys(self):
        """Sync indexes grid to reflect indexes created/removed by key checkboxes."""
        if not self.table:
            return

        try:
            from ..models.base import Key, Index

            # Read directly from table.keys, not from the grid
            # This ensures we get the latest state after _sync_keys_from_indexes() runs
            expected_key_indexes = []

            for key in self.table.keys:
                # Check if this key should have an associated index
                has_index = key.associated_index_guid is not None

                if has_index and key.columns:
                    # This key should have an index
                    existing_index = None

                    # Find the index by GUID
                    if key.associated_index_guid:
                        for idx in self.table.indexes:
                            if idx.guid == key.associated_index_guid:
                                existing_index = idx
                                break

                    if existing_index:
                        # Update existing index columns to match key
                        existing_index.columns = key.columns.copy()
                        expected_key_indexes.append(existing_index)
                    else:
                        # Create new index with matching columns
                        index_name = self._generate_index_name_for_key(key)

                        new_index = Index(
                            name=index_name,
                            columns=key.columns.copy(),
                            tablespace=None
                        )
                        self.table.add_index(new_index)
                        key.associated_index_guid = new_index.guid  # Link them
                        expected_key_indexes.append(new_index)

            # Remove indexes for keys that no longer have associated_index_guid
            # (already handled by the fact that we only process keys with has_index=True above)

            # Reload the indexes grid to show current state
            self._load_indexes()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"⚠ Error syncing indexes from keys: {e}")

    def _sync_keys_from_indexes(self):
        """Sync keys grid to reflect indexes that were created/deleted manually in Indexes tab."""
        if not self.table:
            return

        try:
            # For each key, check if its associated index still exists
            # Also check if a manually created index matches the key's columns

            for key in self.table.keys:
                # Case 1: Key has associated_index_guid but index was deleted
                if key.associated_index_guid:
                    index_exists = any(idx.guid == key.associated_index_guid for idx in self.table.indexes)
                    if not index_exists:
                        # Index was deleted - clear the link
                        key.associated_index_guid = None

                # Case 2: Key has no associated index, but a matching index was created manually
                if not key.associated_index_guid and key.columns:
                    key_columns_set = set(key.columns)
                    for idx in self.table.indexes:
                        if idx.columns and set(idx.columns) == key_columns_set:
                            # Found a matching index - check if it's already linked to another key
                            is_already_linked = any(
                                k.associated_index_guid == idx.guid
                                for k in self.table.keys
                                if k != key
                            )
                            if not is_already_linked:
                                # Link this index to the key
                                key.associated_index_guid = idx.guid
                                break

            # Reload the keys grid to show updated checkbox states
            self._load_keys()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"⚠ Error syncing keys from indexes: {e}")

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

            # Update keys
            self._update_table_keys()

            # Update indexes
            self._update_table_indexes()
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

            # Add keys
            self._update_table_keys()

            # Add indexes
            self._update_table_indexes()

        # Refresh active diagram if it exists
        self._refresh_active_diagram()


        self.accept()
    
    def reject(self):
        """Handle Cancel button click - restore original table state."""
        if self.is_edit_mode:
            # Restore the original table state (undo any changes made during editing)
            self._restore_table_state()

        # Call parent's reject to close the dialog
        super().reject()

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
        try:
            from ..models.base import Key, Index

            if not self.table:
                return

            # Commit any active editor before reading data
            self.keys_grid.commit_active_editor()

            # Clear existing keys
            self.table.keys.clear()

            # Track which indexes are associated with keys (to avoid deletion later)
            key_associated_indexes = set()

            # Add keys from grid widget
            all_data = self.keys_grid.get_all_data()

            for idx, row_data in enumerate(all_data):
                name, key_type, columns_str, ref_table, ref_columns_str, on_delete, has_index = row_data

                # Convert to strings first
                name = str(name) if name else ""
                columns_str = str(columns_str) if columns_str else ""
                ref_table = str(ref_table) if ref_table else ""
                ref_columns_str = str(ref_columns_str) if ref_columns_str else ""
                on_delete = str(on_delete) if on_delete else ""
                has_index = bool(has_index)

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

                    # Manage associated index based on GUID tracking
                    if has_index:
                        existing_index = None

                        # First, try to find associated index by GUID from previous key
                        # (We need to check if this key already existed and had an associated index)
                        old_key = next((k for k in self.table.keys if k.name == key.name), None)
                        if old_key and old_key.associated_index_guid:
                            # Find the index by GUID
                            for idx in self.table.indexes:
                                if idx.guid == old_key.associated_index_guid:
                                    existing_index = idx
                                    key.associated_index_guid = idx.guid  # Preserve the link
                                    break

                        # If not found by GUID, try to find by matching columns
                        if not existing_index:
                            key_columns_set = set(columns)
                            for idx in self.table.indexes:
                                if idx.columns and set(idx.columns) == key_columns_set:
                                    existing_index = idx
                                    key.associated_index_guid = idx.guid  # Link them
                                    break

                        if existing_index:
                            # Update existing index columns to match key columns
                            existing_index.columns = columns.copy()
                            key_associated_indexes.add(existing_index.guid)
                        else:
                            # Create new index with matching columns
                            index_name = self._generate_index_name_for_key(key)

                            index = Index(
                                name=index_name,
                                columns=columns.copy(),
                                tablespace=None  # User can set this in Indexes tab if needed
                            )
                            self.table.add_index(index)
                            key.associated_index_guid = index.guid  # Store the link
                            key_associated_indexes.add(index.guid)
                    else:
                        # If has_index is False, remove associated index if it exists
                        old_key = next((k for k in self.table.keys if k.name == key.name), None)
                        if old_key and old_key.associated_index_guid:
                            # Find and remove the associated index by GUID
                            self.table.indexes = [
                                idx for idx in self.table.indexes
                                if idx.guid != old_key.associated_index_guid
                            ]
                        key.associated_index_guid = None  # Clear the link

                    self.table.add_key(key)

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _generate_index_name_for_key(self, key):
        """Generate an index name for a key based on naming rules engine."""
        from ..controllers.naming_rules_engine import NamingRulesEngine

        # Use the naming rules engine to generate an appropriate index name
        table_name = self.table.name if self.table else ""

        try:
            # Initialize naming rules engine
            naming_engine = NamingRulesEngine()

            # Generate index name using the naming rules template
            index_name = naming_engine.generate_index_name(
                table_name=table_name,
                columns=key.columns,
                table=self.table,
                owner=self.table.owner if self.table else None
            )

            return index_name

        except Exception as e:
            print(f"⚠ Error generating index name with naming engine: {e}")
            # Fallback to simple pattern if naming engine fails
            from ..models.base import Key
            if key.key_type == Key.PRIMARY:
                return f"{table_name}_PK_IDX"
            elif key.key_type == Key.FOREIGN:
                return f"{key.name}_IDX"
            else:  # UNIQUE
                return f"{key.name}_IDX"


    def _update_table_indexes(self):
        """Update table indexes from the indexes grid widget."""
        from ..models.base import Index

        if not self.table:
            return

        # Commit any active editor before reading data
        self.indexes_grid.commit_active_editor()

        # Preserve indexes that are associated with keys (by GUID)
        # These were created by _update_table_keys() and should not be removed
        key_associated_index_guids = set()
        key_associated_indexes = []

        for key in self.table.keys:
            if key.associated_index_guid:
                key_associated_index_guids.add(key.associated_index_guid)
                # Find the index by GUID
                for idx in self.table.indexes:
                    if idx.guid == key.associated_index_guid:
                        key_associated_indexes.append(idx)
                        break

        # Clear existing indexes
        self.table.indexes.clear()

        # Re-add the key-associated indexes first
        for idx in key_associated_indexes:
            self.table.indexes.append(idx)

        # Add indexes from grid widget (but skip if GUID already exists)
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
            # Skip if this index is already in the list (by checking if it's a key-associated index)
            if name.strip() and columns:
                # Check if an index with this name already exists (could be key-associated)
                index_exists = any(idx.name == name.strip() for idx in self.table.indexes)

                if not index_exists:
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

