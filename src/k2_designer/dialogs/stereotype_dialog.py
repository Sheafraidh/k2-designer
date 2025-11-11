"""
Dialog for managing stereotypes (table and column).
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
                             QMessageBox, QColorDialog, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ..models.base import Stereotype, StereotypeType


class StereotypeDialog(QDialog):
    """Dialog for managing stereotypes."""
    
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.table_stereotypes = []
        self.column_stereotypes = []
        
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Manage Stereotypes")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Table stereotypes tab
        table_tab = QWidget()
        self._setup_table_tab(table_tab)
        self.tab_widget.addTab(table_tab, "Table Stereotypes")
        
        # Column stereotypes tab
        column_tab = QWidget()
        self._setup_column_tab(column_tab)
        self.tab_widget.addTab(column_tab, "Column Stereotypes")
        
        layout.addWidget(self.tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _setup_table_tab(self, tab_widget):
        """Setup the table stereotypes tab."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Table stereotypes list
        self.table_stereotypes_table = QTableWidget()
        self.table_stereotypes_table.setColumnCount(4)
        self.table_stereotypes_table.setHorizontalHeaderLabels([
            "Name", "Description", "Background Color", "Preview"
        ])
        
        # Set column widths
        header = self.table_stereotypes_table.horizontalHeader()
        self.table_stereotypes_table.setColumnWidth(0, 120)  # Name
        self.table_stereotypes_table.setColumnWidth(1, 200)  # Description
        self.table_stereotypes_table.setColumnWidth(2, 120)  # Background Color
        self.table_stereotypes_table.setColumnWidth(3, 100)  # Preview
        header.setStretchLastSection(False)
        
        layout.addWidget(self.table_stereotypes_table)
        
        # Table buttons
        table_buttons = QHBoxLayout()
        self.add_table_stereotype_btn = QPushButton("Add Table Stereotype")
        self.edit_table_stereotype_btn = QPushButton("Edit")
        self.remove_table_stereotype_btn = QPushButton("Remove")
        
        table_buttons.addWidget(self.add_table_stereotype_btn)
        table_buttons.addWidget(self.edit_table_stereotype_btn)
        table_buttons.addWidget(self.remove_table_stereotype_btn)
        table_buttons.addStretch()
        
        layout.addLayout(table_buttons)
    
    def _setup_column_tab(self, tab_widget):
        """Setup the column stereotypes tab."""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Column stereotypes list
        self.column_stereotypes_table = QTableWidget()
        self.column_stereotypes_table.setColumnCount(4)
        self.column_stereotypes_table.setHorizontalHeaderLabels([
            "Name", "Description", "Background Color", "Preview"
        ])
        
        # Set column widths
        header = self.column_stereotypes_table.horizontalHeader()
        self.column_stereotypes_table.setColumnWidth(0, 120)  # Name
        self.column_stereotypes_table.setColumnWidth(1, 200)  # Description
        self.column_stereotypes_table.setColumnWidth(2, 120)  # Background Color
        self.column_stereotypes_table.setColumnWidth(3, 100)  # Preview
        header.setStretchLastSection(False)
        
        layout.addWidget(self.column_stereotypes_table)
        
        # Column buttons
        column_buttons = QHBoxLayout()
        self.add_column_stereotype_btn = QPushButton("Add Column Stereotype")
        self.edit_column_stereotype_btn = QPushButton("Edit")
        self.remove_column_stereotype_btn = QPushButton("Remove")
        
        column_buttons.addWidget(self.add_column_stereotype_btn)
        column_buttons.addWidget(self.edit_column_stereotype_btn)
        column_buttons.addWidget(self.remove_column_stereotype_btn)
        column_buttons.addStretch()
        
        layout.addLayout(column_buttons)
    
    def _load_data(self):
        """Load stereotype data from project."""
        if self.project and hasattr(self.project, 'stereotypes'):
            for stereotype in self.project.stereotypes:
                if stereotype.stereotype_type == StereotypeType.TABLE:
                    self.table_stereotypes.append(stereotype)
                else:
                    self.column_stereotypes.append(stereotype)
        
        self._refresh_table_stereotypes()
        self._refresh_column_stereotypes()
    
    def _refresh_table_stereotypes(self):
        """Refresh the table stereotypes list."""
        self.table_stereotypes_table.setRowCount(len(self.table_stereotypes))
        
        for row, stereotype in enumerate(self.table_stereotypes):
            # Name
            self.table_stereotypes_table.setItem(row, 0, QTableWidgetItem(stereotype.name))
            
            # Description
            description = stereotype.description or ""
            self.table_stereotypes_table.setItem(row, 1, QTableWidgetItem(description))
            
            # Background Color
            color_item = QTableWidgetItem(stereotype.background_color)
            color_item.setBackground(QColor(stereotype.background_color))
            self.table_stereotypes_table.setItem(row, 2, color_item)
            
            # Preview
            preview_item = QTableWidgetItem(stereotype.name)
            preview_item.setBackground(QColor(stereotype.background_color))
            # Set text color to contrast with background
            if self._is_dark_color(stereotype.background_color):
                preview_item.setForeground(QColor("#FFFFFF"))
            else:
                preview_item.setForeground(QColor("#000000"))
            self.table_stereotypes_table.setItem(row, 3, preview_item)
    
    def _refresh_column_stereotypes(self):
        """Refresh the column stereotypes list."""
        self.column_stereotypes_table.setRowCount(len(self.column_stereotypes))
        
        for row, stereotype in enumerate(self.column_stereotypes):
            # Name
            self.column_stereotypes_table.setItem(row, 0, QTableWidgetItem(stereotype.name))
            
            # Description
            description = stereotype.description or ""
            self.column_stereotypes_table.setItem(row, 1, QTableWidgetItem(description))
            
            # Background Color
            color_item = QTableWidgetItem(stereotype.background_color)
            color_item.setBackground(QColor(stereotype.background_color))
            self.column_stereotypes_table.setItem(row, 2, color_item)
            
            # Preview
            preview_item = QTableWidgetItem(stereotype.name)
            preview_item.setBackground(QColor(stereotype.background_color))
            # Set text color to contrast with background
            if self._is_dark_color(stereotype.background_color):
                preview_item.setForeground(QColor("#FFFFFF"))
            else:
                preview_item.setForeground(QColor("#000000"))
            self.column_stereotypes_table.setItem(row, 3, preview_item)
    
    def _is_dark_color(self, color_hex: str) -> bool:
        """Check if a color is dark (to determine text color)."""
        try:
            color = QColor(color_hex)
            # Calculate perceived brightness
            brightness = (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114)
            return brightness < 128
        except:
            return False
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        
        # Table stereotype buttons
        self.add_table_stereotype_btn.clicked.connect(self._add_table_stereotype)
        self.edit_table_stereotype_btn.clicked.connect(self._edit_table_stereotype)
        self.remove_table_stereotype_btn.clicked.connect(self._remove_table_stereotype)
        
        # Column stereotype buttons
        self.add_column_stereotype_btn.clicked.connect(self._add_column_stereotype)
        self.edit_column_stereotype_btn.clicked.connect(self._edit_column_stereotype)
        self.remove_column_stereotype_btn.clicked.connect(self._remove_column_stereotype)
        
        # Double-click to edit
        self.table_stereotypes_table.itemDoubleClicked.connect(self._edit_table_stereotype)
        self.column_stereotypes_table.itemDoubleClicked.connect(self._edit_column_stereotype)
    
    def _add_table_stereotype(self):
        """Add a new table stereotype."""
        dialog = StereotypeEditDialog(StereotypeType.TABLE, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            stereotype = dialog.get_stereotype()
            self.table_stereotypes.append(stereotype)
            self._refresh_table_stereotypes()
    
    def _edit_table_stereotype(self):
        """Edit the selected table stereotype."""
        current_row = self.table_stereotypes_table.currentRow()
        if current_row >= 0 and current_row < len(self.table_stereotypes):
            stereotype = self.table_stereotypes[current_row]
            dialog = StereotypeEditDialog(StereotypeType.TABLE, stereotype, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_stereotype = dialog.get_stereotype()
                self.table_stereotypes[current_row] = updated_stereotype
                self._refresh_table_stereotypes()
    
    def _remove_table_stereotype(self):
        """Remove the selected table stereotype."""
        current_row = self.table_stereotypes_table.currentRow()
        if current_row >= 0 and current_row < len(self.table_stereotypes):
            stereotype = self.table_stereotypes[current_row]
            reply = QMessageBox.question(
                self, "Remove Stereotype",
                f"Are you sure you want to remove the table stereotype '{stereotype.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.table_stereotypes[current_row]
                self._refresh_table_stereotypes()
    
    def _add_column_stereotype(self):
        """Add a new column stereotype."""
        dialog = StereotypeEditDialog(StereotypeType.COLUMN, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            stereotype = dialog.get_stereotype()
            self.column_stereotypes.append(stereotype)
            self._refresh_column_stereotypes()
    
    def _edit_column_stereotype(self):
        """Edit the selected column stereotype."""
        current_row = self.column_stereotypes_table.currentRow()
        if current_row >= 0 and current_row < len(self.column_stereotypes):
            stereotype = self.column_stereotypes[current_row]
            dialog = StereotypeEditDialog(StereotypeType.COLUMN, stereotype, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_stereotype = dialog.get_stereotype()
                self.column_stereotypes[current_row] = updated_stereotype
                self._refresh_column_stereotypes()
    
    def _remove_column_stereotype(self):
        """Remove the selected column stereotype."""
        current_row = self.column_stereotypes_table.currentRow()
        if current_row >= 0 and current_row < len(self.column_stereotypes):
            stereotype = self.column_stereotypes[current_row]
            reply = QMessageBox.question(
                self, "Remove Stereotype",
                f"Are you sure you want to remove the column stereotype '{stereotype.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self.column_stereotypes[current_row]
                self._refresh_column_stereotypes()
    
    def _on_ok(self):
        """Handle OK button click."""
        # Update project stereotypes
        if self.project:
            all_stereotypes = self.table_stereotypes + self.column_stereotypes
            self.project.stereotypes = all_stereotypes
        
        self.accept()
    
    def get_stereotypes(self):
        """Get all stereotypes."""
        return self.table_stereotypes + self.column_stereotypes


class StereotypeEditDialog(QDialog):
    """Dialog for editing a single stereotype."""
    
    def __init__(self, stereotype_type: StereotypeType, stereotype: Stereotype = None, parent=None):
        super().__init__(parent)
        self.stereotype_type = stereotype_type
        self.stereotype = stereotype
        self.is_edit_mode = stereotype is not None
        
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        type_name = "Table" if self.stereotype_type == StereotypeType.TABLE else "Column"
        title = f"Edit {type_name} Stereotype" if self.is_edit_mode else f"Add {type_name} Stereotype"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        form_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        form_layout.addRow("Name *:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)
        
        # Background Color
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("Choose Color")
        self.color_button.setFixedWidth(100)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(50, 30)
        self.color_preview.setStyleSheet("border: 1px solid black; background-color: #4C4C4C;")
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        
        color_widget = QWidget()
        color_widget.setLayout(color_layout)
        form_layout.addRow("Background Color:", color_widget)
        
        layout.addLayout(form_layout)
        
        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)
        
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Default color
        default_color = "#4C4C4C" if self.stereotype_type == StereotypeType.TABLE else "#808080"
        self.current_color = default_color
        self._set_color_preview(default_color)
    
    def _load_data(self):
        """Load data if in edit mode."""
        if self.is_edit_mode and self.stereotype:
            self.name_edit.setText(self.stereotype.name)
            if self.stereotype.description:
                self.description_edit.setPlainText(self.stereotype.description)
            self.current_color = self.stereotype.background_color
            self._set_color_preview(self.current_color)
    
    def _set_color_preview(self, color_hex: str):
        """Set the color preview."""
        self.color_preview.setStyleSheet(f"border: 1px solid black; background-color: {color_hex};")
        self.color_preview.setToolTip(f"Color: {color_hex}")
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        self.color_button.clicked.connect(self._choose_color)
    
    def _choose_color(self):
        """Open color picker dialog."""
        current_color = QColor(self.current_color)
        color = QColorDialog.getColor(current_color, self, "Choose Stereotype Color")
        
        if color.isValid():
            self.current_color = color.name()
            self._set_color_preview(self.current_color)
    
    def _on_ok(self):
        """Handle OK button click."""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Stereotype name is required.")
            self.name_edit.setFocus()
            return
        
        description = self.description_edit.toPlainText().strip() or None
        
        self.accept()
    
    def get_stereotype(self) -> Stereotype:
        """Get the stereotype object."""
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip() or None
        
        return Stereotype(
            name=name,
            stereotype_type=self.stereotype_type,
            description=description,
            background_color=self.current_color
        )