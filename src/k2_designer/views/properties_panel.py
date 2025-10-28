"""
Properties panel for displaying and editing object properties.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                             QLineEdit, QTextEdit, QComboBox, QCheckBox,
                             QScrollArea, QGroupBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton,
                             QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal

from ..models import Owner, Table, Sequence, Domain, Column, Key, Index, Stereotype


class PropertiesPanel(QWidget):
    """Panel for displaying and editing properties of selected objects."""
    
    # Signals
    object_modified = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_object = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Scroll area to handle large forms
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Initially show empty state
        self._show_empty_state()
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Save button (initially hidden)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("Save Changes")
        self.save_button.setVisible(False)
        self.save_button.clicked.connect(self._save_changes)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
    
    def _show_empty_state(self):
        """Show empty state when no object is selected."""
        self._clear_layout()
        label = QLabel("Select an object to view its properties")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: gray; font-style: italic;")
        self.content_layout.addWidget(label)
    
    def _show_multiple_selection_properties(self, objects):
        """Show properties for multiple selected objects."""
        self._clear_layout()
        
        if not objects:
            self._show_empty_state()
            return
        
        # Summary information
        summary_group = QGroupBox("Multiple Selection Summary")
        summary_layout = QFormLayout(summary_group)
        
        # Count objects by type
        type_counts = {}
        for obj in objects:
            obj_type = type(obj).__name__
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        # Total count
        total_label = QLabel(f"<b>{len(objects)}</b> objects selected")
        summary_layout.addRow("Total:", total_label)
        
        # Breakdown by type
        for obj_type, count in sorted(type_counts.items()):
            type_label = QLabel(f"<b>{count}</b> {obj_type}{'s' if count > 1 else ''}")
            summary_layout.addRow(f"{obj_type}s:", type_label)
        
        self.content_layout.addWidget(summary_group)
        
        # If all objects are of the same type, show common properties
        if len(type_counts) == 1:
            obj_type = list(type_counts.keys())[0]
            if obj_type == "Table":
                self._show_multiple_table_properties(objects)
            elif obj_type == "Sequence":
                self._show_multiple_sequence_properties(objects)
            elif obj_type == "Owner":
                self._show_multiple_owner_properties(objects)
            elif obj_type == "Domain":
                self._show_multiple_domain_properties(objects)
        
        # List of selected objects
        objects_group = QGroupBox("Selected Objects")
        objects_layout = QVBoxLayout(objects_group)
        
        objects_table = QTableWidget()
        objects_table.setColumnCount(3)
        objects_table.setHorizontalHeaderLabels(["Type", "Name", "Owner"])
        objects_table.horizontalHeader().setStretchLastSection(True)
        
        objects_table.setRowCount(len(objects))
        for row, obj in enumerate(objects):
            objects_table.setItem(row, 0, QTableWidgetItem(type(obj).__name__))
            objects_table.setItem(row, 1, QTableWidgetItem(obj.name))
            if hasattr(obj, 'owner'):
                objects_table.setItem(row, 2, QTableWidgetItem(obj.owner))
            else:
                objects_table.setItem(row, 2, QTableWidgetItem("-"))
        
        objects_layout.addWidget(objects_table)
        self.content_layout.addWidget(objects_group)
        
        self.content_layout.addStretch()
        
        # Tip for users
        tip_label = QLabel("💡 <i>Tip: Click on a single object to edit its properties</i>")
        tip_label.setStyleSheet("color: #666; font-size: 10px; padding: 10px;")
        tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(tip_label)
    
    def _show_multiple_table_properties(self, tables):
        """Show common properties for multiple selected tables."""
        common_group = QGroupBox("Common Table Properties")
        common_layout = QFormLayout(common_group)
        
        # Find common stereotype
        stereotypes = set(table.stereotype for table in tables)
        if len(stereotypes) == 1:
            stereotype_label = QLabel(list(stereotypes)[0].value)
            common_layout.addRow("Stereotype:", stereotype_label)
        else:
            common_layout.addRow("Stereotype:", QLabel(f"<i>Mixed ({len(stereotypes)} different)</i>"))
        
        # Find common owners
        owners = set(table.owner for table in tables)
        if len(owners) == 1:
            owner_label = QLabel(list(owners)[0])
            common_layout.addRow("Owner:", owner_label)
        else:
            common_layout.addRow("Owner:", QLabel(f"<i>Mixed ({len(owners)} different)</i>"))
        
        # Total column count
        total_columns = sum(len(table.columns) for table in tables)
        common_layout.addRow("Total Columns:", QLabel(f"<b>{total_columns}</b>"))
        
        self.content_layout.addWidget(common_group)
    
    def _show_multiple_sequence_properties(self, sequences):
        """Show common properties for multiple selected sequences."""
        common_group = QGroupBox("Common Sequence Properties")
        common_layout = QFormLayout(common_group)
        
        # Find common owners
        owners = set(seq.owner for seq in sequences)
        if len(owners) == 1:
            owner_label = QLabel(list(owners)[0])
            common_layout.addRow("Owner:", owner_label)
        else:
            common_layout.addRow("Owner:", QLabel(f"<i>Mixed ({len(owners)} different)</i>"))
        
        # Find common increment values
        increments = set(seq.increment_by for seq in sequences)
        if len(increments) == 1:
            increment_label = QLabel(str(list(increments)[0]))
            common_layout.addRow("Increment By:", increment_label)
        else:
            common_layout.addRow("Increment By:", QLabel(f"<i>Mixed ({len(increments)} different)</i>"))
        
        self.content_layout.addWidget(common_group)
    
    def _show_multiple_owner_properties(self, owners):
        """Show common properties for multiple selected owners."""
        common_group = QGroupBox("Common Owner Properties")
        common_layout = QFormLayout(common_group)
        
        # Find common tablespaces
        tablespaces = set(owner.default_tablespace for owner in owners if owner.default_tablespace)
        if tablespaces and len(tablespaces) == 1:
            ts_label = QLabel(list(tablespaces)[0])
            common_layout.addRow("Default Tablespace:", ts_label)
        elif tablespaces:
            common_layout.addRow("Default Tablespace:", QLabel(f"<i>Mixed ({len(tablespaces)} different)</i>"))
        
        self.content_layout.addWidget(common_group)
    
    def _show_multiple_domain_properties(self, domains):
        """Show common properties for multiple selected domains."""
        common_group = QGroupBox("Common Domain Properties")
        common_layout = QFormLayout(common_group)
        
        # Find common data types
        data_types = set(domain.data_type for domain in domains)
        if len(data_types) == 1:
            dt_label = QLabel(list(data_types)[0])
            common_layout.addRow("Data Type:", dt_label)
        else:
            common_layout.addRow("Data Type:", QLabel(f"<i>Mixed ({len(data_types)} different)</i>"))
        
        self.content_layout.addWidget(common_group)
    
    def _save_changes(self):
        """Save changes made in the properties panel."""
        if not self.current_object:
            return
        
        try:
            if isinstance(self.current_object, Owner):
                self._save_owner_changes()
            elif isinstance(self.current_object, Table):
                self._save_table_changes()
            elif isinstance(self.current_object, Sequence):
                self._save_sequence_changes()
            elif isinstance(self.current_object, Domain):
                self._save_domain_changes()
            
            # Emit signal that object was modified
            self.object_modified.emit(self.current_object)
            
            # Show success message briefly
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", "Changes saved successfully!")
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save changes:\n{str(e)}")
    
    def _save_owner_changes(self):
        """Save changes to an Owner object."""
        if not hasattr(self, 'owner_widgets'):
            return
        
        # Update owner properties from widgets
        self.current_object.comment = self.owner_widgets['comment'].toPlainText().strip() or None
        self.current_object.default_tablespace = self.owner_widgets['default_tablespace'].text().strip() or None
        self.current_object.temp_tablespace = self.owner_widgets['temp_tablespace'].text().strip() or None
        self.current_object.default_index_tablespace = self.owner_widgets['index_tablespace'].text().strip() or None
        self.current_object.editionable = self.owner_widgets['editionable'].isChecked()
    
    def _save_table_changes(self):
        """Save changes to a Table object."""
        # We'll implement this when we make the table properties editable
        pass
    
    def _save_sequence_changes(self):
        """Save changes to a Sequence object."""
        # We'll implement this when we make the sequence properties editable
        pass
    
    def _save_domain_changes(self):
        """Save changes to a Domain object."""
        if not hasattr(self, 'domain_widgets'):
            return
        
        # Validate data type is not empty
        data_type = self.domain_widgets['data_type'].text().strip()
        if not data_type:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "Data type cannot be empty.")
            return
        
        # Update domain properties from widgets
        self.current_object.data_type = data_type
        self.current_object.comment = self.domain_widgets['comment'].toPlainText().strip() or None
    
    def _clear_layout(self):
        """Clear all widgets from the content layout."""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_object(self, obj):
        """Set the object(s) to display properties for.
        
        Args:
            obj: Single object, list of objects, or None
        """
        self.current_object = obj
        
        if obj is None:
            self._show_empty_state()
            self.save_button.setVisible(False)
        elif isinstance(obj, list):
            # Multiple objects selected
            self._show_multiple_selection_properties(obj)
            self.save_button.setVisible(False)  # No bulk editing for now
        elif isinstance(obj, Owner):
            self._show_owner_properties(obj)
            self.save_button.setVisible(True)
        elif isinstance(obj, Table):
            self._show_table_properties(obj)
            self.save_button.setVisible(True)
        elif isinstance(obj, Sequence):
            self._show_sequence_properties(obj)
            self.save_button.setVisible(True)
        elif isinstance(obj, Domain):
            self._show_domain_properties(obj)
            self.save_button.setVisible(True)
        else:
            self._show_empty_state()
            self.save_button.setVisible(False)
    
    def _show_owner_properties(self, owner: Owner):
        """Show properties for an Owner object."""
        self._clear_layout()
        
        # Store widget references for saving
        self.owner_widgets = {}
        
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        name_edit = QLineEdit(owner.name)
        name_edit.setReadOnly(True)  # Name should not be editable here
        basic_layout.addRow("Name:", name_edit)
        
        self.owner_widgets['comment'] = QTextEdit(owner.comment or "")
        self.owner_widgets['comment'].setMaximumHeight(80)
        basic_layout.addRow("Comment:", self.owner_widgets['comment'])
        
        self.content_layout.addWidget(basic_group)
        
        # Tablespace properties
        tablespace_group = QGroupBox("Tablespace Properties")
        tablespace_layout = QFormLayout(tablespace_group)
        
        self.owner_widgets['default_tablespace'] = QLineEdit(owner.default_tablespace or "")
        tablespace_layout.addRow("Default Tablespace:", self.owner_widgets['default_tablespace'])
        
        self.owner_widgets['temp_tablespace'] = QLineEdit(owner.temp_tablespace or "")
        tablespace_layout.addRow("Temporary Tablespace:", self.owner_widgets['temp_tablespace'])
        
        self.owner_widgets['index_tablespace'] = QLineEdit(owner.default_index_tablespace or "")
        tablespace_layout.addRow("Default Index Tablespace:", self.owner_widgets['index_tablespace'])
        
        self.content_layout.addWidget(tablespace_group)
        
        # Other properties
        other_group = QGroupBox("Other Properties")
        other_layout = QFormLayout(other_group)
        
        self.owner_widgets['editionable'] = QCheckBox()
        self.owner_widgets['editionable'].setChecked(owner.editionable)
        other_layout.addRow("Editionable:", self.owner_widgets['editionable'])
        
        self.content_layout.addWidget(other_group)
        self.content_layout.addStretch()
    
    def _show_table_properties(self, table: Table):
        """Show properties for a Table object."""
        self._clear_layout()
        
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        name_edit = QLineEdit(table.name)
        name_edit.setReadOnly(True)
        basic_layout.addRow("Name:", name_edit)
        
        owner_edit = QLineEdit(table.owner)
        owner_edit.setReadOnly(True)
        basic_layout.addRow("Owner:", owner_edit)
        
        tablespace_edit = QLineEdit(table.tablespace or "")
        basic_layout.addRow("Tablespace:", tablespace_edit)
        
        stereotype_combo = QComboBox()
        stereotype_combo.addItems([s.value for s in Stereotype])
        stereotype_combo.setCurrentText(table.stereotype.value)
        basic_layout.addRow("Stereotype:", stereotype_combo)
        
        color_edit = QLineEdit(table.color or "")
        basic_layout.addRow("Color:", color_edit)
        
        domain_edit = QLineEdit(table.domain or "")
        basic_layout.addRow("Domain:", domain_edit)
        
        editionable_check = QCheckBox()
        editionable_check.setChecked(table.editionable)
        basic_layout.addRow("Editionable:", editionable_check)
        
        comment_edit = QTextEdit(table.comment or "")
        comment_edit.setMaximumHeight(80)
        basic_layout.addRow("Comment:", comment_edit)
        
        self.content_layout.addWidget(basic_group)
        
        # Columns
        columns_group = QGroupBox("Columns")
        columns_layout = QVBoxLayout(columns_group)
        
        columns_table = QTableWidget()
        columns_table.setColumnCount(5)
        columns_table.setHorizontalHeaderLabels([
            "Name", "Data Type", "Nullable", "Default", "Comment"
        ])
        columns_table.horizontalHeader().setStretchLastSection(True)
        
        columns_table.setRowCount(len(table.columns))
        for row, column in enumerate(table.columns):
            columns_table.setItem(row, 0, QTableWidgetItem(column.name))
            columns_table.setItem(row, 1, QTableWidgetItem(column.data_type))
            columns_table.setItem(row, 2, QTableWidgetItem("Yes" if column.nullable else "No"))
            columns_table.setItem(row, 3, QTableWidgetItem(column.default or ""))
            columns_table.setItem(row, 4, QTableWidgetItem(column.comment or ""))
        
        columns_layout.addWidget(columns_table)
        
        # Column buttons
        column_buttons = QHBoxLayout()
        add_column_btn = QPushButton("Add Column")
        edit_column_btn = QPushButton("Edit Column")
        remove_column_btn = QPushButton("Remove Column")
        column_buttons.addWidget(add_column_btn)
        column_buttons.addWidget(edit_column_btn)
        column_buttons.addWidget(remove_column_btn)
        column_buttons.addStretch()
        columns_layout.addLayout(column_buttons)
        
        self.content_layout.addWidget(columns_group)
        
        # Keys
        if table.keys:
            keys_group = QGroupBox("Keys")
            keys_layout = QVBoxLayout(keys_group)
            
            keys_table = QTableWidget()
            keys_table.setColumnCount(2)
            keys_table.setHorizontalHeaderLabels(["Key Name", "Columns"])
            keys_table.horizontalHeader().setStretchLastSection(True)
            
            keys_table.setRowCount(len(table.keys))
            for row, key in enumerate(table.keys):
                keys_table.setItem(row, 0, QTableWidgetItem(key.name))
                keys_table.setItem(row, 1, QTableWidgetItem(", ".join(key.columns)))
            
            keys_layout.addWidget(keys_table)
            self.content_layout.addWidget(keys_group)
        
        # Indexes
        if table.indexes:
            indexes_group = QGroupBox("Indexes")
            indexes_layout = QVBoxLayout(indexes_group)
            
            indexes_table = QTableWidget()
            indexes_table.setColumnCount(3)
            indexes_table.setHorizontalHeaderLabels(["Index Name", "Columns", "Tablespace"])
            indexes_table.horizontalHeader().setStretchLastSection(True)
            
            indexes_table.setRowCount(len(table.indexes))
            for row, index in enumerate(table.indexes):
                indexes_table.setItem(row, 0, QTableWidgetItem(index.name))
                indexes_table.setItem(row, 1, QTableWidgetItem(", ".join(index.columns)))
                indexes_table.setItem(row, 2, QTableWidgetItem(index.tablespace or ""))
            
            indexes_layout.addWidget(indexes_table)
            self.content_layout.addWidget(indexes_group)
        
        self.content_layout.addStretch()
    
    def _show_sequence_properties(self, sequence: Sequence):
        """Show properties for a Sequence object."""
        self._clear_layout()
        
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        name_edit = QLineEdit(sequence.name)
        name_edit.setReadOnly(True)
        basic_layout.addRow("Name:", name_edit)
        
        owner_edit = QLineEdit(sequence.owner)
        owner_edit.setReadOnly(True)
        basic_layout.addRow("Owner:", owner_edit)
        
        comment_edit = QTextEdit(sequence.comment or "")
        comment_edit.setMaximumHeight(80)
        basic_layout.addRow("Comment:", comment_edit)
        
        self.content_layout.addWidget(basic_group)
        
        # Sequence attributes
        attrs_group = QGroupBox("Sequence Attributes")
        attrs_layout = QFormLayout(attrs_group)
        
        start_edit = QLineEdit(str(sequence.start_with))
        attrs_layout.addRow("Start With:", start_edit)
        
        increment_edit = QLineEdit(str(sequence.increment_by))
        attrs_layout.addRow("Increment By:", increment_edit)
        
        min_edit = QLineEdit(str(sequence.min_value) if sequence.min_value is not None else "")
        attrs_layout.addRow("Minimum Value:", min_edit)
        
        max_edit = QLineEdit(str(sequence.max_value) if sequence.max_value is not None else "")
        attrs_layout.addRow("Maximum Value:", max_edit)
        
        cache_edit = QLineEdit(str(sequence.cache_size))
        attrs_layout.addRow("Cache Size:", cache_edit)
        
        cycle_check = QCheckBox()
        cycle_check.setChecked(sequence.cycle)
        attrs_layout.addRow("Cycle:", cycle_check)
        
        self.content_layout.addWidget(attrs_group)
        self.content_layout.addStretch()
    
    def _show_domain_properties(self, domain: Domain):
        """Show properties for a Domain object."""
        self._clear_layout()
        
        # Store widget references for saving
        self.domain_widgets = {}
        
        # Basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        name_edit = QLineEdit(domain.name)
        name_edit.setReadOnly(True)
        basic_layout.addRow("Name:", name_edit)
        
        self.domain_widgets['data_type'] = QLineEdit(domain.data_type)
        basic_layout.addRow("Data Type:", self.domain_widgets['data_type'])
        
        self.domain_widgets['comment'] = QTextEdit(domain.comment or "")
        self.domain_widgets['comment'].setMaximumHeight(80)
        basic_layout.addRow("Comment:", self.domain_widgets['comment'])
        
        self.content_layout.addWidget(basic_group)
        self.content_layout.addStretch()