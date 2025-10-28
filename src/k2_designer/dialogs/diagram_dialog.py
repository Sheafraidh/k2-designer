"""
Dialog for creating and editing diagrams.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QDialogButtonBox, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

from ..models import Diagram


class DiagramDialog(QDialog):
    """Dialog for creating and editing diagrams."""
    
    def __init__(self, diagram: Diagram = None, existing_names: list = None, parent=None):
        super().__init__(parent)
        self.diagram = diagram
        self.existing_names = existing_names or []
        self.is_edit_mode = diagram is not None
        
        self.setWindowTitle("Edit Diagram" if self.is_edit_mode else "New Diagram")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Form layout for input fields
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter diagram name...")
        form_layout.addRow("Name:", self.name_edit)
        
        # Description field
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter diagram description (optional)...")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Information label
        info_label = QLabel("Diagrams are used to visualize your database schema. "
                           "You can drag tables and sequences onto diagrams to create ER diagrams.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._accept)
        self.button_box.rejected.connect(self.reject)
        
        layout.addWidget(self.button_box)
        
        # Set focus to name field
        self.name_edit.setFocus()
    
    def _load_data(self):
        """Load data into the form fields."""
        if self.diagram:
            self.name_edit.setText(self.diagram.name)
            self.description_edit.setPlainText(self.diagram.description)
    
    def _accept(self):
        """Handle the OK button click."""
        name = self.name_edit.text().strip()
        
        # Validate name
        if not name:
            QMessageBox.warning(self, "Validation Error", "Diagram name is required.")
            self.name_edit.setFocus()
            return
        
        # Check for duplicate names (only if creating new or name changed)
        if name in self.existing_names and (not self.is_edit_mode or self.diagram.name != name):
            QMessageBox.warning(self, "Validation Error", 
                              f"A diagram named '{name}' already exists.")
            self.name_edit.setFocus()
            return
        
        # Validate name format (basic validation)
        if not name.replace('_', '').replace(' ', '').replace('-', '').isalnum():
            QMessageBox.warning(self, "Validation Error", 
                              "Diagram name can only contain letters, numbers, spaces, hyphens, and underscores.")
            self.name_edit.setFocus()
            return
        
        self.accept()
    
    def get_data(self) -> dict:
        """Get the dialog data."""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip()
        }
    
    def create_diagram(self) -> Diagram:
        """Create a new diagram from the dialog data."""
        data = self.get_data()
        return Diagram(data['name'], data['description'])
    
    def update_diagram(self) -> None:
        """Update the existing diagram with dialog data."""
        if self.diagram:
            data = self.get_data()
            self.diagram.name = data['name']
            self.diagram.description = data['description']