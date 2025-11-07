"""
Dialog for adding and editing table objects.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QGroupBox, QTabWidget,
                             QWidget, QColorDialog, QStyledItemDelegate)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ..models import Table, Column, Stereotype


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
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _setup_basic_tab(self, tab_widget):
        """Setup the basic properties tab."""
        layout = QVBoxLayout(tab_widget)
        
        form_layout = QFormLayout()
        
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
        self.stereotype_combo.addItems([s.value for s in Stereotype])
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
        self.comment_edit.setMaximumHeight(80)
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
        
        # Columns table
        self.columns_table = MultiSelectTableWidget()
        self.columns_table.set_parent_dialog(self)
        self.columns_table.setColumnCount(6)
        self.columns_table.setHorizontalHeaderLabels([
            "Name", "Data Type", "Nullable", "Default", "Comment", "Domain"
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
        
        # Set resize modes for better user experience
        from PyQt6.QtWidgets import QHeaderView
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Data Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)        # Nullable (fixed size)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Default
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)      # Comment (stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # Domain
        
        layout.addWidget(self.columns_table)
        
        # Column buttons
        column_buttons = QHBoxLayout()
        self.add_column_btn = QPushButton("Add Column")
        self.edit_column_btn = QPushButton("Edit Column")
        self.remove_column_btn = QPushButton("Remove Column")
        
        column_buttons.addWidget(self.add_column_btn)
        column_buttons.addWidget(self.edit_column_btn)
        column_buttons.addWidget(self.remove_column_btn)
        column_buttons.addStretch()
        
        layout.addLayout(column_buttons)
        
        # Add multi-select info label
        self.multiselect_label = QLabel("Tips: • Multi-select: Ctrl+click to toggle, Shift+click for range • Navigation: Enter moves to next row, Tab moves to next column")
        self.multiselect_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        self.multiselect_label.setWordWrap(True)
        layout.addWidget(self.multiselect_label)
    
    def _load_data(self):
        """Load data if in edit mode."""
        if self.is_edit_mode and self.table:
            self.name_edit.setText(self.table.name)
            
            # Set owner
            owner_index = self.owner_combo.findText(self.table.owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)
            
            self.tablespace_edit.setText(self.table.tablespace or "")
            self.stereotype_combo.setCurrentText(self.table.stereotype.value)
            self._set_color(self.table.color or "#FFFFFF")
            self._color_manually_set = bool(self.table.color)  # Mark as manually set if table has a specific color
            self.editionable_check.setChecked(self.table.editionable)
            self.comment_edit.setPlainText(self.table.comment or "")
            
            # Load columns
            self._load_columns()
            
            # Make name readonly in edit mode
            self.name_edit.setReadOnly(True)
        elif self.selected_owner:
            # Pre-select owner in add mode
            owner_index = self.owner_combo.findText(self.selected_owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)
    
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
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        
        self.color_button.clicked.connect(self._choose_color)
        self.stereotype_combo.currentTextChanged.connect(self._on_stereotype_changed)
        
        self.add_column_btn.clicked.connect(self._add_column)
        self.edit_column_btn.clicked.connect(self._edit_column)
        self.remove_column_btn.clicked.connect(self._remove_column)
        
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
        """Remove the selected column."""
        current_row = self.columns_table.currentRow()
        if current_row >= 0:
            self.columns_table.removeRow(current_row)
    
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
    
    def _on_stereotype_changed(self):
        """Handle stereotype change to update default color."""
        if not self.is_edit_mode or not hasattr(self, '_color_manually_set'):
            # Only auto-update color if not in edit mode or color hasn't been manually set
            stereotype_text = self.stereotype_combo.currentText()
            stereotype = Stereotype(stereotype_text)
            
            # Get default color for stereotype (similar to Table model logic)
            color_map = {
                Stereotype.BUSINESS: "#081B2A",  # Light blue
                Stereotype.TECHNICAL: "#360A3C"  # Light purple
            }
            default_color = color_map.get(stereotype, "#464646")
            self._set_color(default_color)
    
    def _on_ok(self):
        """Handle OK button click."""
        if not self._validate_form():
            return
        
        name = self.name_edit.text().strip()
        owner = self.owner_combo.currentText()
        tablespace = self.tablespace_edit.text().strip() or None
        stereotype = Stereotype(self.stereotype_combo.currentText())
        color = self.current_color if self.current_color != "#FFFFFF" else None
        editionable = self.editionable_check.isChecked()
        comment = self.comment_edit.toPlainText().strip() or None
        
        if self.is_edit_mode:
            # Update existing table
            self.table.tablespace = tablespace
            self.table.stereotype = stereotype
            self.table.color = color or self.table._get_default_color(stereotype)
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
                        domain=domain
                    )
                    self.table.add_column(column)
    
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