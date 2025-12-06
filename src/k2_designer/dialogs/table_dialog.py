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
                             QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QGroupBox, QTabWidget,
                             QWidget, QColorDialog, QStyledItemDelegate)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ..models import Table, Column
from ..models.base import Stereotype, StereotypeType


class MultiSelectDelegate(QStyledItemDelegate):
    """Custom delegate that handles multi-row editing."""
    
    # Signal emitted when editing is about to start
    editingStarted = pyqtSignal(int, int)  # row, column
    
    def setEditorData(self, editor, index):
        """Override to capture when editing starts."""
        # Emit signal that editing started
        self.editingStarted.emit(index.row(), index.column())
        # Call parent implementation
        super().setEditorData(editor, index)


class MultiSelectTableWidget(QTableWidget):
    """Custom table widget that preserves selection during editing for multi-row updates."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._captured_selection = set()
        self._parent_dialog = None
        
        # Install custom delegate
        self._delegate = MultiSelectDelegate()
        self.setItemDelegate(self._delegate)
        
        # Connect delegate signal
        self._delegate.editingStarted.connect(self._on_editing_started)
        
    def set_parent_dialog(self, dialog):
        """Set reference to parent dialog for multi-select updates."""
        self._parent_dialog = dialog
    
    def _on_editing_started(self, row, column):
        """Capture selection when editing starts."""
        self._captured_selection = set()
        for item in self.selectedItems():
            self._captured_selection.add(item.row())
        
    def get_captured_selection(self):
        """Get the selection captured when editing started."""
        return self._captured_selection


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
        """Setup the columns tab."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins within tab
        layout.setSpacing(5)  # Reduced spacing between elements
        
        # Filter controls
        filter_group = QGroupBox("Filter Columns")
        filter_layout = QVBoxLayout(filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)  # Compact filter group
        filter_layout.setSpacing(3)  # Minimal spacing between label and input rows
        
        # Create labels row
        labels_layout = QHBoxLayout()
        
        # Create labels with fixed widths to match inputs
        name_label = QLabel("Name")
        name_label.setFixedWidth(120)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        datatype_label = QLabel("Data Type") 
        datatype_label.setFixedWidth(130)
        datatype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nullable_label = QLabel("Nullable")
        nullable_label.setFixedWidth(80)
        nullable_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        default_label = QLabel("Default")
        default_label.setFixedWidth(100)
        default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        comment_label = QLabel("Comment")
        comment_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        domain_label = QLabel("Domain")
        domain_label.setFixedWidth(120)
        domain_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        stereotype_label = QLabel("Stereotype")
        stereotype_label.setFixedWidth(120)
        stereotype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        clear_label = QLabel("")  # Empty space for clear button
        clear_label.setFixedWidth(100)
        
        labels_layout.addWidget(name_label)
        labels_layout.addWidget(datatype_label)
        labels_layout.addWidget(nullable_label)
        labels_layout.addWidget(default_label)
        labels_layout.addWidget(comment_label)
        labels_layout.addWidget(domain_label)
        labels_layout.addWidget(stereotype_label)
        labels_layout.addWidget(clear_label)
        
        # Create filter inputs row with matching widths
        inputs_layout = QHBoxLayout()
        
        # Create filter inputs for each column
        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("Filter Name...")
        self.filter_name.setFixedWidth(120)
        self.filter_name.textChanged.connect(self._apply_filters)
        
        self.filter_datatype = QLineEdit()
        self.filter_datatype.setPlaceholderText("Filter Data Type...")
        self.filter_datatype.setFixedWidth(130)
        self.filter_datatype.textChanged.connect(self._apply_filters)
        
        self.filter_nullable = QComboBox()
        self.filter_nullable.addItems(["All", "Nullable", "Not Nullable"])
        self.filter_nullable.setFixedWidth(80)
        self.filter_nullable.currentTextChanged.connect(self._apply_filters)
        
        self.filter_default = QLineEdit()
        self.filter_default.setPlaceholderText("Filter Default...")
        self.filter_default.setFixedWidth(100)
        self.filter_default.textChanged.connect(self._apply_filters)
        
        self.filter_comment = QLineEdit()
        self.filter_comment.setPlaceholderText("Filter Comment...")
        self.filter_comment.textChanged.connect(self._apply_filters)
        
        self.filter_domain = QComboBox()
        self.filter_domain.setEditable(True)
        self.filter_domain.setFixedWidth(120)
        self.filter_domain.lineEdit().setPlaceholderText("Filter Domain...")
        self.filter_domain.currentTextChanged.connect(self._apply_filters)
        self.filter_domain.lineEdit().textChanged.connect(self._apply_filters)
        
        self.filter_stereotype = QComboBox()
        self.filter_stereotype.setEditable(True)
        self.filter_stereotype.setFixedWidth(120)
        self.filter_stereotype.lineEdit().setPlaceholderText("Filter Stereotype...")
        self.filter_stereotype.currentTextChanged.connect(self._apply_filters)
        self.filter_stereotype.lineEdit().textChanged.connect(self._apply_filters)
        
        # Clear filters button
        self.clear_filters_btn = QPushButton("Clear Filters")
        self.clear_filters_btn.setFixedWidth(100)
        self.clear_filters_btn.clicked.connect(self._clear_filters)
        
        # Add widgets to inputs layout
        inputs_layout.addWidget(self.filter_name)
        inputs_layout.addWidget(self.filter_datatype)
        inputs_layout.addWidget(self.filter_nullable)
        inputs_layout.addWidget(self.filter_default)
        inputs_layout.addWidget(self.filter_comment)
        inputs_layout.addWidget(self.filter_domain)
        inputs_layout.addWidget(self.filter_stereotype)
        inputs_layout.addWidget(self.clear_filters_btn)
        
        # Add both layouts to filter group
        filter_layout.addLayout(labels_layout)
        filter_layout.addLayout(inputs_layout)
        
        layout.addWidget(filter_group)
        
        # Toolbar with small icon buttons between filter and grid
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 3, 0, 3)
        toolbar_layout.setSpacing(2)

        # Create small icon-only buttons
        self.add_column_btn = QPushButton("+")
        self.add_column_btn.setToolTip("Add Column")
        self.add_column_btn.setFixedSize(28, 28)
        self.add_column_btn.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.edit_column_btn = QPushButton("✎")
        self.edit_column_btn.setToolTip("Edit Column")
        self.edit_column_btn.setFixedSize(28, 28)
        self.edit_column_btn.setStyleSheet("font-size: 14px;")

        self.remove_column_btn = QPushButton("✕")
        self.remove_column_btn.setToolTip("Remove Columns")
        self.remove_column_btn.setFixedSize(28, 28)
        self.remove_column_btn.setStyleSheet("font-weight: bold; font-size: 14px; color: #c44;")

        self.move_up_btn = QPushButton("↑")
        self.move_up_btn.setToolTip("Move Up")
        self.move_up_btn.setFixedSize(28, 28)
        self.move_up_btn.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.move_down_btn = QPushButton("↓")
        self.move_down_btn.setToolTip("Move Down")
        self.move_down_btn.setFixedSize(28, 28)
        self.move_down_btn.setStyleSheet("font-weight: bold; font-size: 16px;")

        toolbar_layout.addWidget(self.add_column_btn)
        toolbar_layout.addWidget(self.edit_column_btn)
        toolbar_layout.addWidget(self.remove_column_btn)
        toolbar_layout.addWidget(QLabel("|"))  # Separator
        toolbar_layout.addWidget(self.move_up_btn)
        toolbar_layout.addWidget(self.move_down_btn)
        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Columns table
        self.columns_table = MultiSelectTableWidget()
        self.columns_table.set_parent_dialog(self)
        self.columns_table.setColumnCount(7)
        self.columns_table.setHorizontalHeaderLabels([
            "Name", "Data Type", "Nullable", "Default", "Comment", "Domain", "Stereotype"
        ])
        
        # Enable extended selection (standard Shift+click range selection, Ctrl+click toggle)
        self.columns_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.columns_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        
        # Set up column sizing
        header = self.columns_table.horizontalHeader()
        header.setStretchLastSection(False)  # Don't stretch last section
        
        # Set specific column widths
        self.columns_table.setColumnWidth(0, 120)  # Name
        self.columns_table.setColumnWidth(1, 130)  # Data Type
        self.columns_table.setColumnWidth(2, 80)   # Nullable
        self.columns_table.setColumnWidth(3, 100)  # Default
        self.columns_table.setColumnWidth(4, 150)  # Comment
        self.columns_table.setColumnWidth(5, 120)  # Domain
        self.columns_table.setColumnWidth(6, 120)  # Stereotype
        
        # Set resize modes for better user experience
        from PyQt6.QtWidgets import QHeaderView
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Data Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)        # Nullable (fixed size)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Default
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)      # Comment (stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # Domain
        
        layout.addWidget(self.columns_table)
        
        # Bottom button - only Import from CSV
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        bottom_layout.setSpacing(5)

        self.import_csv_btn = QPushButton("Import from CSV...")
        bottom_layout.addWidget(self.import_csv_btn)
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

    def _setup_filter_domains(self):
        """Setup the domain filter combobox with available domains."""
        self.filter_domain.clear()
        self.filter_domain.addItem("All")
        self.filter_domain.addItem("No Domain")
        
        # Add available domains
        if self.project and hasattr(self.project, 'domains'):
            for domain in self.project.domains:
                self.filter_domain.addItem(domain.name)
    
    def _setup_filter_stereotypes(self):
        """Setup the stereotype filter combobox with available stereotypes."""
        self.filter_stereotype.clear()
        self.filter_stereotype.addItem("All")
        self.filter_stereotype.addItem("No Stereotype")
        
        # Add available column stereotypes
        if self.project and hasattr(self.project, 'stereotypes'):
            for stereotype in self.project.stereotypes:
                if stereotype.stereotype_type.value == 'column':
                    self.filter_stereotype.addItem(stereotype.name)
    
    def _apply_filters(self):
        """Apply filters to show/hide rows based on filter criteria."""
        name_filter = self.filter_name.text().lower()
        datatype_filter = self.filter_datatype.text().lower()
        nullable_filter = self.filter_nullable.currentText()
        default_filter = self.filter_default.text().lower()
        comment_filter = self.filter_comment.text().lower()
        domain_filter = self.filter_domain.currentText()
        stereotype_filter = self.filter_stereotype.currentText()
        
        for row in range(self.columns_table.rowCount()):
            show_row = True
            
            # Check name filter
            if name_filter:
                name_item = self.columns_table.item(row, 0)
                if not name_item or name_filter not in name_item.text().lower():
                    show_row = False
            
            # Check data type filter
            if show_row and datatype_filter:
                datatype_item = self.columns_table.item(row, 1)
                if not datatype_item or datatype_filter not in datatype_item.text().lower():
                    show_row = False
            
            # Check nullable filter
            if show_row and nullable_filter != "All":
                nullable_widget = self.columns_table.cellWidget(row, 2)
                if nullable_widget and hasattr(nullable_widget, 'checkbox'):
                    is_nullable = nullable_widget.checkbox.isChecked()
                    if nullable_filter == "Nullable" and not is_nullable:
                        show_row = False
                    elif nullable_filter == "Not Nullable" and is_nullable:
                        show_row = False
            
            # Check default filter
            if show_row and default_filter:
                default_item = self.columns_table.item(row, 3)
                if not default_item or default_filter not in default_item.text().lower():
                    show_row = False
            
            # Check comment filter
            if show_row and comment_filter:
                comment_item = self.columns_table.item(row, 4)
                if not comment_item or comment_filter not in comment_item.text().lower():
                    show_row = False
            
            # Check domain filter
            if show_row and domain_filter not in ["All", ""]:
                domain_combo = self.columns_table.cellWidget(row, 5)
                if domain_combo and isinstance(domain_combo, QComboBox):
                    current_domain = domain_combo.currentText()
                    if domain_filter == "No Domain":
                        if current_domain:  # Has a domain selected
                            show_row = False
                    else:
                        if current_domain != domain_filter:
                            show_row = False
                else:
                    # No domain widget, treat as "No Domain"
                    if domain_filter != "No Domain":
                        show_row = False
            
            # Check stereotype filter
            if show_row and stereotype_filter not in ["All", ""]:
                stereotype_combo = self.columns_table.cellWidget(row, 6)
                if stereotype_combo and isinstance(stereotype_combo, QComboBox):
                    current_stereotype = stereotype_combo.currentText()
                    if stereotype_filter == "No Stereotype":
                        if current_stereotype:  # Has a stereotype selected
                            show_row = False
                    else:
                        if current_stereotype != stereotype_filter:
                            show_row = False
                else:
                    # No stereotype widget, treat as "No Stereotype"
                    if stereotype_filter != "No Stereotype":
                        show_row = False
            
            # Show or hide the row
            self.columns_table.setRowHidden(row, not show_row)
    
    def _clear_filters(self):
        """Clear all filters and show all rows."""
        self.filter_name.clear()
        self.filter_datatype.clear()
        self.filter_nullable.setCurrentIndex(0)  # "All"
        self.filter_default.clear()
        self.filter_comment.clear()
        self.filter_domain.setCurrentIndex(0)  # "All"
        self.filter_stereotype.setCurrentIndex(0)  # "All"
        
        # Show all rows
        for row in range(self.columns_table.rowCount()):
            self.columns_table.setRowHidden(row, False)
    
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
            
            # Setup filter domains
            self._setup_filter_domains()
            
            # Setup filter stereotypes
            self._setup_filter_stereotypes()
            
            # Name is now editable in edit mode (removed read-only restriction)
        elif self.selected_owner:
            # Pre-select owner in add mode
            owner_index = self.owner_combo.findText(self.selected_owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)
            
            # Setup filter domains even in add mode
            self._setup_filter_domains()
            
            # Setup filter stereotypes even in add mode
            self._setup_filter_stereotypes()
    
    def _load_columns(self):
        """Load columns into the table."""
        if not self.table:
            return
        
        self.columns_table.setRowCount(len(self.table.columns))
        
        for row, column in enumerate(self.table.columns):
            self.columns_table.setItem(row, 0, QTableWidgetItem(column.name))
            
            # Data type item
            data_type_item = QTableWidgetItem(column.data_type)
            self.columns_table.setItem(row, 1, data_type_item)
            
            # Nullable checkbox
            self._setup_nullable_cell(row, column.nullable)
            
            self.columns_table.setItem(row, 3, QTableWidgetItem(column.default or ""))
            self.columns_table.setItem(row, 4, QTableWidgetItem(column.comment or ""))
            
            # Domain column with combobox
            self._setup_domain_cell(row, column.domain or "")
            
            # Stereotype column with combobox
            self._setup_stereotype_cell(row, column.stereotype or "")
    
    def _setup_nullable_cell(self, row, nullable=True):
        """Setup nullable checkbox for a specific cell."""
        # Create a widget to center the checkbox
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        checkbox = QCheckBox()
        checkbox.setChecked(nullable)
        
        # Connect to multi-select handler
        checkbox.toggled.connect(
            lambda checked, r=row: self._on_nullable_changed(r, checked)
        )
        
        # Center the checkbox
        layout.addStretch()
        layout.addWidget(checkbox)
        layout.addStretch()
        
        # Set the widget as the cell widget
        self.columns_table.setCellWidget(row, 2, widget)
        
        # Store checkbox reference for easy access
        widget.checkbox = checkbox
    
    def _setup_domain_cell(self, row, selected_domain=""):
        """Setup domain combobox for a specific cell."""
        domain_combo = QComboBox()
        domain_combo.setEditable(False)
        
        # Add empty option
        domain_combo.addItem("", "")  # Text, data
        
        # Add available domains
        if self.project and hasattr(self.project, 'domains'):
            for domain in self.project.domains:
                domain_combo.addItem(domain.name, domain.name)
        
        # Set current selection
        if selected_domain:
            index = domain_combo.findData(selected_domain)
            if index >= 0:
                domain_combo.setCurrentIndex(index)
        
        # Connect signal for domain change (use multi-select handler)
        domain_combo.currentTextChanged.connect(
            lambda text, r=row: self._on_domain_changed_multi(r, text)
        )
        
        # Set the combobox as the cell widget
        self.columns_table.setCellWidget(row, 5, domain_combo)
        
        # Update data type editability based on current domain
        self._update_data_type_editability(row, selected_domain)
    
    def _setup_stereotype_cell(self, row, selected_stereotype=""):
        """Setup stereotype combobox for a specific cell."""
        stereotype_combo = QComboBox()
        stereotype_combo.setEditable(False)
        
        # Add empty option
        stereotype_combo.addItem("", "")  # Text, data
        
        # Add available column stereotypes
        if self.project and hasattr(self.project, 'stereotypes'):
            for stereotype in self.project.stereotypes:
                if stereotype.stereotype_type.value == 'column':
                    stereotype_combo.addItem(stereotype.name, stereotype.name)
        
        # Set current selection
        if selected_stereotype:
            index = stereotype_combo.findData(selected_stereotype)
            if index >= 0:
                stereotype_combo.setCurrentIndex(index)
        
        # Connect signal for stereotype change (use multi-select handler)
        stereotype_combo.currentTextChanged.connect(
            lambda text, r=row: self._on_stereotype_changed_multi(r, text)
        )
        
        # Set the combobox as the cell widget
        self.columns_table.setCellWidget(row, 6, stereotype_combo)
    
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
                data_type_item = self.columns_table.item(row, 1)
                if data_type_item:
                    data_type_item.setText(domain.data_type)
                
                # Make data type non-editable
                self._update_data_type_editability(row, domain_name)
    
    def _update_data_type_editability(self, row, domain_name):
        """Update whether the data type cell is editable based on domain selection."""
        data_type_item = self.columns_table.item(row, 1)
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
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        
        self.color_button.clicked.connect(self._choose_color)
        self.stereotype_combo.currentTextChanged.connect(self._on_table_stereotype_changed)

        self.add_column_btn.clicked.connect(self._add_column)
        self.edit_column_btn.clicked.connect(self._edit_column)
        self.remove_column_btn.clicked.connect(self._remove_column)
        self.import_csv_btn.clicked.connect(self._import_from_csv)
        self.move_up_btn.clicked.connect(self._move_row_up)
        self.move_down_btn.clicked.connect(self._move_row_down)

        # Connect table item changes for multi-select updates
        self.columns_table.itemChanged.connect(self._on_item_changed)
        
        # Connect key press event for Excel-like navigation
        self.columns_table.keyPressEvent = self._table_key_press_event
    
    def _add_column(self):
        """Add a new column."""
        # Simple column addition for now
        row = self.columns_table.rowCount()
        self.columns_table.insertRow(row)
        
        self.columns_table.setItem(row, 0, QTableWidgetItem(""))
        self.columns_table.setItem(row, 1, QTableWidgetItem(""))
        
        # Setup nullable checkbox for new row (default to True/nullable)
        self._setup_nullable_cell(row, True)
        
        self.columns_table.setItem(row, 3, QTableWidgetItem(""))
        self.columns_table.setItem(row, 4, QTableWidgetItem(""))
        
        # Setup domain cell for new row
        self._setup_domain_cell(row, "")
        
        # Setup stereotype cell for new row
        self._setup_stereotype_cell(row, "")
        
        # Refresh filters to show the new row
        self._apply_filters()
        
        # Focus on the new row
        self.columns_table.setCurrentCell(row, 0)
        self.columns_table.editItem(self.columns_table.item(row, 0))
    
    def _edit_column(self):
        """Edit the selected column."""
        current_row = self.columns_table.currentRow()
        if current_row >= 0:
            # Focus on the current cell for editing
            current_col = self.columns_table.currentColumn()
            if current_col >= 0:
                self.columns_table.editItem(self.columns_table.item(current_row, current_col))
    
    def _remove_column(self):
        """Remove all selected columns."""
        # Get all selected rows (unique row numbers)
        selected_rows = set()
        for item in self.columns_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            # No selection, try current row
            current_row = self.columns_table.currentRow()
            if current_row >= 0:
                selected_rows.add(current_row)

        if selected_rows:
            # Confirm if removing multiple rows
            if len(selected_rows) > 1:
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Remove Columns",
                    f"Remove {len(selected_rows)} selected columns?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            # Remove rows in reverse order to maintain indices
            for row in sorted(selected_rows, reverse=True):
                self.columns_table.removeRow(row)

            # Refresh filters after removing rows
            self._apply_filters()
    
    def _import_from_csv(self):
        """Import columns from CSV data."""
        from .csv_import_dialog import CSVImportDialog

        dialog = CSVImportDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            columns = dialog.get_columns()

            if columns:
                # Ask if user wants to append or replace
                from PyQt6.QtWidgets import QMessageBox

                current_row_count = self.columns_table.rowCount()
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
                        self.columns_table.setRowCount(0)
                    # If Yes, we keep existing and append

                # Import the columns
                for col_data in columns:
                    self._add_imported_column(col_data)

                # Refresh filters
                self._apply_filters()

                # Show success message
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Successfully imported {len(columns)} columns."
                )

    def _move_row_up(self):
        """Move the selected row(s) up."""
        # Get selected rows
        selected_rows = sorted(set(item.row() for item in self.columns_table.selectedItems()))

        if not selected_rows:
            # No selection, try current row
            current_row = self.columns_table.currentRow()
            if current_row >= 0:
                selected_rows = [current_row]

        if not selected_rows:
            return

        # Can't move up if first row is selected
        if selected_rows[0] == 0:
            return

        # Block signals during the move to prevent flickering
        self.columns_table.blockSignals(True)

        try:
            # Check if rows are contiguous
            is_contiguous = all(selected_rows[i] + 1 == selected_rows[i + 1]
                               for i in range(len(selected_rows) - 1))

            if is_contiguous:
                # Move contiguous block up by swapping with the row above the block
                first_row = selected_rows[0]
                self._swap_rows(first_row - 1, first_row)

                # If there are more rows in the block, move them up too
                for i in range(1, len(selected_rows)):
                    self._swap_rows(selected_rows[i] - 1, selected_rows[i])

                moved_rows = [row - 1 for row in selected_rows]
            else:
                # For non-contiguous selection, move each row individually
                moved_rows = []
                for row in selected_rows:
                    if row > 0:
                        self._swap_rows(row, row - 1)
                        moved_rows.append(row - 1)

            # Clear and restore selection efficiently
            self.columns_table.clearSelection()

            # Select all moved rows - use item selection to maintain multi-selection
            for row in moved_rows:
                for col in range(self.columns_table.columnCount()):
                    item = self.columns_table.item(row, col)
                    if item:
                        item.setSelected(True)

            # Set current cell to first moved row
            if moved_rows:
                self.columns_table.setCurrentCell(moved_rows[0], self.columns_table.currentColumn())

        finally:
            # Unblock signals
            self.columns_table.blockSignals(False)

    def _move_row_down(self):
        """Move the selected row(s) down."""
        # Get selected rows
        selected_rows = sorted(set(item.row() for item in self.columns_table.selectedItems()), reverse=True)

        if not selected_rows:
            # No selection, try current row
            current_row = self.columns_table.currentRow()
            if current_row >= 0:
                selected_rows = [current_row]

        if not selected_rows:
            return

        # Can't move down if last row is selected
        if selected_rows[0] >= self.columns_table.rowCount() - 1:
            return

        # Block signals during the move to prevent flickering
        self.columns_table.blockSignals(True)

        try:
            # Check if rows are contiguous (remember list is reversed)
            forward_rows = sorted(selected_rows)
            is_contiguous = all(forward_rows[i] + 1 == forward_rows[i + 1]
                               for i in range(len(forward_rows) - 1))

            if is_contiguous:
                # Move contiguous block down by swapping with the row below the block
                # Process in reverse order to avoid index issues
                last_row = selected_rows[0]  # This is the highest row (list is reversed)
                self._swap_rows(last_row, last_row + 1)

                # If there are more rows in the block, move them down too
                for i in range(1, len(selected_rows)):
                    self._swap_rows(selected_rows[i], selected_rows[i] + 1)

                moved_rows = [row + 1 for row in forward_rows]
            else:
                # For non-contiguous selection, move each row individually (already in reverse order)
                moved_rows = []
                for row in selected_rows:
                    if row < self.columns_table.rowCount() - 1:
                        self._swap_rows(row, row + 1)
                        moved_rows.append(row + 1)

            # Clear and restore selection efficiently
            self.columns_table.clearSelection()

            # Select all moved rows - use item selection to maintain multi-selection
            for row in sorted(moved_rows):
                for col in range(self.columns_table.columnCount()):
                    item = self.columns_table.item(row, col)
                    if item:
                        item.setSelected(True)

            # Set current cell to first moved row
            if moved_rows:
                self.columns_table.setCurrentCell(sorted(moved_rows)[0], self.columns_table.currentColumn())

        finally:
            # Unblock signals
            self.columns_table.blockSignals(False)

    def _swap_rows(self, row1, row2):
        """Swap two rows in the columns table."""
        # Temporarily disconnect itemChanged signal to avoid triggering updates
        self.columns_table.itemChanged.disconnect(self._on_item_changed)

        try:
            # First, extract all data from both rows
            row1_data = self._extract_row_data(row1)
            row2_data = self._extract_row_data(row2)

            # Then, set the data to swapped positions
            self._set_row_data(row1, row2_data)
            self._set_row_data(row2, row1_data)

        finally:
            # Reconnect the signal
            self.columns_table.itemChanged.connect(self._on_item_changed)

    def _extract_row_data(self, row):
        """Extract all data from a row including widgets."""
        data = {}

        # Extract regular items (0=Name, 1=DataType, 3=Default, 4=Comment)
        data['name'] = self.columns_table.item(row, 0).text() if self.columns_table.item(row, 0) else ""
        data['data_type'] = self.columns_table.item(row, 1).text() if self.columns_table.item(row, 1) else ""
        data['default'] = self.columns_table.item(row, 3).text() if self.columns_table.item(row, 3) else ""
        data['comment'] = self.columns_table.item(row, 4).text() if self.columns_table.item(row, 4) else ""

        # Extract data type editability (for domain-controlled fields)
        data_type_item = self.columns_table.item(row, 1)
        if data_type_item:
            data['data_type_editable'] = bool(data_type_item.flags() & Qt.ItemFlag.ItemIsEditable)
        else:
            data['data_type_editable'] = True

        # Extract nullable checkbox state (column 2)
        nullable_widget = self.columns_table.cellWidget(row, 2)
        if nullable_widget and hasattr(nullable_widget, 'checkbox'):
            data['nullable'] = nullable_widget.checkbox.isChecked()
        else:
            data['nullable'] = True

        # Extract domain selection (column 5)
        domain_combo = self.columns_table.cellWidget(row, 5)
        if domain_combo and isinstance(domain_combo, QComboBox):
            data['domain'] = domain_combo.currentData() or ""
        else:
            data['domain'] = ""

        # Extract stereotype selection (column 6)
        stereotype_combo = self.columns_table.cellWidget(row, 6)
        if stereotype_combo and isinstance(stereotype_combo, QComboBox):
            data['stereotype'] = stereotype_combo.currentData() or ""
        else:
            data['stereotype'] = ""

        return data

    def _set_row_data(self, row, data):
        """Set all data for a row including recreating widgets."""
        # Set regular items
        self.columns_table.setItem(row, 0, QTableWidgetItem(data['name']))

        data_type_item = QTableWidgetItem(data['data_type'])
        self.columns_table.setItem(row, 1, data_type_item)

        # Set data type editability
        if data['data_type_editable']:
            data_type_item.setFlags(data_type_item.flags() | Qt.ItemFlag.ItemIsEditable)
            data_type_item.setData(Qt.ItemDataRole.ForegroundRole, None)
        else:
            data_type_item.setFlags(data_type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            data_type_item.setForeground(QColor(128, 128, 128))

        self.columns_table.setItem(row, 3, QTableWidgetItem(data['default']))
        self.columns_table.setItem(row, 4, QTableWidgetItem(data['comment']))

        # Recreate nullable checkbox (column 2)
        self._setup_nullable_cell(row, data['nullable'])

        # Recreate domain combobox (column 5)
        self._setup_domain_cell(row, data['domain'])

        # Recreate stereotype combobox (column 6)
        self._setup_stereotype_cell(row, data['stereotype'])

    def _add_imported_column(self, col_data):
        """Add an imported column to the table."""
        row = self.columns_table.rowCount()
        self.columns_table.insertRow(row)

        # Name
        name_item = QTableWidgetItem(col_data['name'])
        self.columns_table.setItem(row, 0, name_item)

        # Data Type
        data_type_item = QTableWidgetItem(col_data['data_type'])
        self.columns_table.setItem(row, 1, data_type_item)

        # Nullable (checkbox)
        nullable_widget = QWidget()
        nullable_layout = QHBoxLayout(nullable_widget)
        nullable_layout.setContentsMargins(0, 0, 0, 0)
        nullable_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nullable_checkbox = QCheckBox()
        nullable_checkbox.setChecked(col_data['nullable'])
        nullable_widget.checkbox = nullable_checkbox  # Store reference
        nullable_layout.addWidget(nullable_checkbox)
        self.columns_table.setCellWidget(row, 2, nullable_widget)

        # Default
        default_item = QTableWidgetItem(col_data['default'])
        self.columns_table.setItem(row, 3, default_item)

        # Comment
        comment_item = QTableWidgetItem(col_data['comment'])
        self.columns_table.setItem(row, 4, comment_item)

        # Domain (combobox) - set to empty/None
        domain_combo = QComboBox()
        domain_combo.addItem("", None)
        if self.project and hasattr(self.project, 'domains'):
            for domain in self.project.domains:
                domain_combo.addItem(domain.name, domain.name)
        self.columns_table.setCellWidget(row, 5, domain_combo)

        # Stereotype (combobox) - set to empty/None
        stereotype_combo = QComboBox()
        stereotype_combo.addItem("", None)
        if self.project and hasattr(self.project, 'stereotypes'):
            for stereotype in self.project.stereotypes:
                if stereotype.stereotype_type.value == 'column':
                    stereotype_combo.addItem(stereotype.name, stereotype.name)
        self.columns_table.setCellWidget(row, 6, stereotype_combo)

    def _on_item_changed(self, item):
        """Handle item change in columns table for multi-select updates."""
        # Skip if item change was triggered programmatically (to prevent recursion)
        if hasattr(self, '_updating_multiselect') and self._updating_multiselect:
            return
        
        # Get the captured selection from delegate
        captured_selection = self.columns_table.get_captured_selection()
            
        # Use captured selection if it was multi-row and includes current row
        if len(captured_selection) > 1 and item.row() in captured_selection:
            self._apply_change_to_selected_rows(item, captured_selection)
        else:
            # Fall back to current selection
            current_selection = set()
            for selected_item in self.columns_table.selectedItems():
                current_selection.add(selected_item.row())
            
            if len(current_selection) > 1 and item.row() in current_selection:
                self._apply_change_to_selected_rows(item, current_selection)
    
    def _apply_change_to_selected_rows(self, changed_item, selected_rows=None):
        """Apply the change from one item to all selected rows."""
        column = changed_item.column()
        new_value = changed_item.text()
        changed_row = changed_item.row()
        
        # Use provided selection or get current selection
        if selected_rows is None:
            selected_rows = set()
            for selected_item in self.columns_table.selectedItems():
                selected_rows.add(selected_item.row())
        
        # Set flag to prevent recursive updates
        self._updating_multiselect = True
        
        try:
            for row in selected_rows:
                if row != changed_row:  # Don't update the row that triggered the change
                    if column in [0, 1, 3, 4]:  # Name, Data Type, Default, Comment
                        # Only update if the cell exists and the column allows editing
                        existing_item = self.columns_table.item(row, column)
                        if existing_item:
                            # For data type, check if it's editable (not controlled by domain)
                            if column == 1:  # Data Type column
                                domain_combo = self.columns_table.cellWidget(row, 5)
                                if domain_combo and domain_combo.currentData():
                                    # Skip updating data type if domain is selected
                                    continue
                            existing_item.setText(new_value)
        finally:
            # Reset flag
            self._updating_multiselect = False
            # Refresh filters after changes
            self._apply_filters()
    
    def _on_nullable_changed(self, row, checked):
        """Handle nullable checkbox change for multi-select updates."""
        # Skip if change was triggered programmatically
        if hasattr(self, '_updating_multiselect') and self._updating_multiselect:
            return
            
        # Get current selection for nullable changes (they don't go through editing capture)
        selected_rows = set()
        for selected_item in self.columns_table.selectedItems():
            selected_rows.add(selected_item.row())
        
        # Only apply to multiple rows if more than one is selected and current row is in selection
        if len(selected_rows) > 1 and row in selected_rows:
            self._updating_multiselect = True
            try:
                for selected_row in selected_rows:
                    if selected_row != row:  # Don't update the row that triggered the change
                        nullable_widget = self.columns_table.cellWidget(selected_row, 2)
                        if nullable_widget and hasattr(nullable_widget, 'checkbox'):
                            nullable_widget.checkbox.setChecked(checked)
            finally:
                self._updating_multiselect = False
    
    def _on_domain_changed_multi(self, row, domain_name):
        """Handle domain selection change for multi-select updates."""
        # Skip if change was triggered programmatically
        if hasattr(self, '_updating_multiselect') and self._updating_multiselect:
            return
            
        # Get current selection for domain changes (they don't go through editing capture)
        selected_rows = set()
        for selected_item in self.columns_table.selectedItems():
            selected_rows.add(selected_item.row())
        
        # Apply domain change to the current row first
        self._on_domain_changed(row, domain_name)
        
        # Only apply to multiple rows if more than one is selected and current row is in selection
        if len(selected_rows) > 1 and row in selected_rows:
            self._updating_multiselect = True
            try:
                for selected_row in selected_rows:
                    if selected_row != row:  # Don't update the row that triggered the change
                        domain_combo = self.columns_table.cellWidget(selected_row, 5)
                        if domain_combo:
                            # Find and set the domain
                            index = domain_combo.findData(domain_name)
                            if index >= 0:
                                domain_combo.setCurrentIndex(index)
                            
                            # Apply the domain change logic to this row too
                            self._on_domain_changed(selected_row, domain_name)
            finally:
                self._updating_multiselect = False
                # Refresh filters after domain changes
                self._apply_filters()
    
    def _on_stereotype_changed_multi(self, row, stereotype_name):
        """Handle stereotype selection change for multi-select updates."""
        # Skip if change was triggered programmatically
        if hasattr(self, '_updating_multiselect') and self._updating_multiselect:
            return
            
        # Get current selection for stereotype changes
        selected_rows = set()
        for selected_item in self.columns_table.selectedItems():
            selected_rows.add(selected_item.row())
        
        # Apply stereotype change to the current row first
        self._on_stereotype_changed(row, stereotype_name)
        
        # Only apply to multiple rows if more than one is selected and current row is in selection
        if len(selected_rows) > 1 and row in selected_rows:
            self._updating_multiselect = True
            try:
                for selected_row in selected_rows:
                    if selected_row != row:  # Don't update the row that triggered the change
                        stereotype_combo = self.columns_table.cellWidget(selected_row, 6)
                        if stereotype_combo:
                            # Find and set the stereotype
                            index = stereotype_combo.findData(stereotype_name)
                            if index >= 0:
                                stereotype_combo.setCurrentIndex(index)
                            
                            # Apply the stereotype change logic to this row too
                            self._on_stereotype_changed(selected_row, stereotype_name)
            finally:
                self._updating_multiselect = False
                # Refresh filters after stereotype changes
                self._apply_filters()
    
    def _table_key_press_event(self, event):
        """Handle key press events in the columns table for Excel-like navigation."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QKeyEvent
        
        # Check if multiple rows are selected
        selected_rows = set()
        for selected_item in self.columns_table.selectedItems():
            selected_rows.add(selected_item.row())
        
        # For multi-selection, handle Enter key differently
        if len(selected_rows) > 1:
            # In multi-select mode, Enter should just commit the edit without navigation
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                # Just call the default handler to commit the edit, no navigation
                QTableWidget.keyPressEvent(self.columns_table, event)
                return
            else:
                # For other keys in multi-select, use default behavior
                QTableWidget.keyPressEvent(self.columns_table, event)
                return
        
        # Single selection mode - use Excel-like navigation
        # Handle Enter key for navigation (single selection only)
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_row = self.columns_table.currentRow()
            current_col = self.columns_table.currentColumn()
            
            # Move to next row in the same column
            if current_row < self.columns_table.rowCount() - 1:
                next_row = current_row + 1
                self.columns_table.setCurrentCell(next_row, current_col)
                
                # Start editing the cell if it's editable
                next_item = self.columns_table.item(next_row, current_col)
                if next_item and (next_item.flags() & Qt.ItemFlag.ItemIsEditable):
                    self.columns_table.editItem(next_item)
                elif current_col == 2:  # Nullable column (checkbox)
                    # For checkbox column, just focus on the widget
                    nullable_widget = self.columns_table.cellWidget(next_row, 2)
                    if nullable_widget and hasattr(nullable_widget, 'checkbox'):
                        nullable_widget.checkbox.setFocus()
                elif current_col == 5:  # Domain column (combobox)
                    # For combobox column, focus and open dropdown
                    domain_combo = self.columns_table.cellWidget(next_row, 5)
                    if domain_combo:
                        domain_combo.setFocus()
                        domain_combo.showPopup()
            else:
                # At the last row, add a new row and move to it
                self._add_column()
                if self.columns_table.rowCount() > current_row + 1:
                    self.columns_table.setCurrentCell(current_row + 1, current_col)
                    # Start editing the new cell if it's editable
                    new_item = self.columns_table.item(current_row + 1, current_col)
                    if new_item and (new_item.flags() & Qt.ItemFlag.ItemIsEditable):
                        self.columns_table.editItem(new_item)
            
            return  # Don't call the default handler
        
        # Handle Tab key for moving to next column
        elif event.key() == Qt.Key.Key_Tab:
            current_row = self.columns_table.currentRow()
            current_col = self.columns_table.currentColumn()
            
            # Move to next column, wrapping to next row if needed
            if current_col < self.columns_table.columnCount() - 1:
                next_col = current_col + 1
                self.columns_table.setCurrentCell(current_row, next_col)
            else:
                # Wrap to next row, first column
                if current_row < self.columns_table.rowCount() - 1:
                    self.columns_table.setCurrentCell(current_row + 1, 0)
                else:
                    # Add new row if at the end
                    self._add_column()
                    if self.columns_table.rowCount() > current_row + 1:
                        self.columns_table.setCurrentCell(current_row + 1, 0)
            
            # Start editing the new cell
            new_row = self.columns_table.currentRow()
            new_col = self.columns_table.currentColumn()
            new_item = self.columns_table.item(new_row, new_col)
            if new_item and (new_item.flags() & Qt.ItemFlag.ItemIsEditable):
                self.columns_table.editItem(new_item)
            elif new_col == 2:  # Nullable column
                nullable_widget = self.columns_table.cellWidget(new_row, 2)
                if nullable_widget and hasattr(nullable_widget, 'checkbox'):
                    nullable_widget.checkbox.setFocus()
            elif new_col == 5:  # Domain column
                domain_combo = self.columns_table.cellWidget(new_row, 5)
                if domain_combo:
                    domain_combo.setFocus()
            elif new_col == 6:  # Stereotype column
                stereotype_combo = self.columns_table.cellWidget(new_row, 6)
                if stereotype_combo:
                    stereotype_combo.setFocus()
            
            return  # Don't call the default handler
        
        # Handle Shift+Tab for moving to previous column
        elif event.key() == Qt.Key.Key_Backtab or (event.key() == Qt.Key.Key_Tab and event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            current_row = self.columns_table.currentRow()
            current_col = self.columns_table.currentColumn()
            
            # Move to previous column, wrapping to previous row if needed
            if current_col > 0:
                prev_col = current_col - 1
                self.columns_table.setCurrentCell(current_row, prev_col)
            else:
                # Wrap to previous row, last column
                if current_row > 0:
                    self.columns_table.setCurrentCell(current_row - 1, self.columns_table.columnCount() - 1)
            
            # Start editing the new cell
            new_row = self.columns_table.currentRow()
            new_col = self.columns_table.currentColumn()
            new_item = self.columns_table.item(new_row, new_col)
            if new_item and (new_item.flags() & Qt.ItemFlag.ItemIsEditable):
                self.columns_table.editItem(new_item)
            elif new_col == 2:  # Nullable column
                nullable_widget = self.columns_table.cellWidget(new_row, 2)
                if nullable_widget and hasattr(nullable_widget, 'checkbox'):
                    nullable_widget.checkbox.setFocus()
            elif new_col == 5:  # Domain column
                domain_combo = self.columns_table.cellWidget(new_row, 5)
                if domain_combo:
                    domain_combo.setFocus()
            elif new_col == 6:  # Stereotype column
                stereotype_combo = self.columns_table.cellWidget(new_row, 6)
                if stereotype_combo:
                    stereotype_combo.setFocus()
            
            return  # Don't call the default handler
        
        # For all other keys, call the default QTableWidget keyPressEvent
        else:
            # Call the original keyPressEvent method
            QTableWidget.keyPressEvent(self.columns_table, event)
    
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
        """Update table columns from the table widget."""
        if not self.table:
            return
        
        # Clear existing columns
        self.table.columns.clear()
        
        # Add columns from table widget
        for row in range(self.columns_table.rowCount()):
            name_item = self.columns_table.item(row, 0)
            data_type_item = self.columns_table.item(row, 1)
            default_item = self.columns_table.item(row, 3)
            comment_item = self.columns_table.item(row, 4)
            
            # Get nullable value from checkbox widget
            nullable_widget = self.columns_table.cellWidget(row, 2)
            nullable = True  # Default value
            if nullable_widget and hasattr(nullable_widget, 'checkbox'):
                nullable = nullable_widget.checkbox.isChecked()
            
            # Get domain from combobox widget
            domain_combo = self.columns_table.cellWidget(row, 5)
            domain = None
            if domain_combo and isinstance(domain_combo, QComboBox):
                domain = domain_combo.currentData() or None
            
            # Get stereotype from combobox widget
            stereotype_combo = self.columns_table.cellWidget(row, 6)
            stereotype = None
            if stereotype_combo and isinstance(stereotype_combo, QComboBox):
                stereotype = stereotype_combo.currentData() or None
            
            if name_item and data_type_item:
                name = name_item.text().strip()
                data_type = data_type_item.text().strip()
                
                if name and data_type:
                    default = default_item.text().strip() if default_item else None
                    comment = comment_item.text().strip() if comment_item else None
                    
                    column = Column(
                        name=name,
                        data_type=data_type,
                        nullable=nullable,
                        default=default or None,
                        comment=comment or None,
                        domain=domain,
                        stereotype=stereotype
                    )
                    self.table.add_column(column)
    
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

