"""
Dialog for adding and editing domain objects.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QMessageBox)
from PyQt6.QtCore import Qt

from ..models import Domain


class DomainDialog(QDialog):
    """Dialog for creating and editing domain objects."""
    
    def __init__(self, domain: Domain = None, parent=None):
        super().__init__(parent)
        self.domain = domain
        self.is_edit_mode = domain is not None
        
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Edit Domain" if self.is_edit_mode else "Add Domain")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        form_layout.addRow("Name *:", self.name_edit)
        
        self.data_type_edit = QLineEdit()
        self.data_type_edit.setMaxLength(100)
        form_layout.addRow("Data Type *:", self.data_type_edit)
        
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(80)
        form_layout.addRow("Comment:", self.comment_edit)
        
        layout.addLayout(form_layout)
        
        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _load_data(self):
        """Load data if in edit mode."""
        if self.is_edit_mode and self.domain:
            self.name_edit.setText(self.domain.name)
            self.data_type_edit.setText(self.domain.data_type)
            self.comment_edit.setPlainText(self.domain.comment or "")
            
            # Make name readonly in edit mode
            self.name_edit.setReadOnly(True)
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_ok(self):
        """Handle OK button click."""
        if not self._validate_form():
            return
        
        name = self.name_edit.text().strip()
        data_type = self.data_type_edit.text().strip()
        comment = self.comment_edit.toPlainText().strip() or None
        
        if self.is_edit_mode:
            # Update existing domain
            self.domain.data_type = data_type
            self.domain.comment = comment
        else:
            # Create new domain
            self.domain = Domain(name, data_type, comment)
        
        self.accept()
    
    def _validate_form(self) -> bool:
        """Validate the form data."""
        name = self.name_edit.text().strip()
        data_type = self.data_type_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Domain name is required.")
            self.name_edit.setFocus()
            return False
        
        if not data_type:
            QMessageBox.warning(self, "Validation Error", "Data type is required.")
            self.data_type_edit.setFocus()
            return False
        
        return True
    
    def get_domain(self) -> Domain:
        """Get the domain object."""
        return self.domain