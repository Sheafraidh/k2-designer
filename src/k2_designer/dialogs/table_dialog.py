"""
Dialog for adding and editing table objects.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QGroupBox, QTabWidget,
                             QWidget, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..models import Table, Column, Stereotype


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
        self.current_color = "#FFFFFF"
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
        self.columns_table = QTableWidget()
        self.columns_table.setColumnCount(6)
        self.columns_table.setHorizontalHeaderLabels([
            "Name", "Data Type", "Nullable", "Default", "Comment", "Domain"
        ])
        
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
            
            self.columns_table.setItem(row, 2, QTableWidgetItem("Yes" if column.nullable else "No"))
            self.columns_table.setItem(row, 3, QTableWidgetItem(column.default or ""))
            self.columns_table.setItem(row, 4, QTableWidgetItem(column.comment or ""))
            
            # Domain column with combobox
            self._setup_domain_cell(row, column.domain or "")
    
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
        
        # Connect signal for domain change
        domain_combo.currentTextChanged.connect(
            lambda text, r=row: self._on_domain_changed(r, text)
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
                # Make non-editable
                data_type_item.setFlags(data_type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                data_type_item.setBackground(QColor(240, 240, 240))  # Light gray background
            else:  # No domain selected
                # Make editable
                data_type_item.setFlags(data_type_item.flags() | Qt.ItemFlag.ItemIsEditable)
                data_type_item.setBackground(QColor(255, 255, 255))  # White background
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        
        self.color_button.clicked.connect(self._choose_color)
        self.stereotype_combo.currentTextChanged.connect(self._on_stereotype_changed)
        
        self.add_column_btn.clicked.connect(self._add_column)
        self.edit_column_btn.clicked.connect(self._edit_column)
        self.remove_column_btn.clicked.connect(self._remove_column)
    
    def _add_column(self):
        """Add a new column."""
        # Simple column addition for now
        row = self.columns_table.rowCount()
        self.columns_table.insertRow(row)
        
        self.columns_table.setItem(row, 0, QTableWidgetItem(""))
        self.columns_table.setItem(row, 1, QTableWidgetItem(""))
        self.columns_table.setItem(row, 2, QTableWidgetItem("Yes"))
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
                Stereotype.BUSINESS: "#E3F2FD",  # Light blue
                Stereotype.TECHNICAL: "#F3E5F5"  # Light purple
            }
            default_color = color_map.get(stereotype, "#FFFFFF")
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
            nullable_item = self.columns_table.item(row, 2)
            default_item = self.columns_table.item(row, 3)
            comment_item = self.columns_table.item(row, 4)
            
            # Get domain from combobox widget
            domain_combo = self.columns_table.cellWidget(row, 5)
            domain = None
            if domain_combo and isinstance(domain_combo, QComboBox):
                domain = domain_combo.currentData() or None
            
            if name_item and data_type_item:
                name = name_item.text().strip()
                data_type = data_type_item.text().strip()
                
                if name and data_type:
                    nullable = nullable_item.text().lower() == "yes" if nullable_item else True
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
    
    def get_table(self) -> Table:
        """Get the table object."""
        return self.table