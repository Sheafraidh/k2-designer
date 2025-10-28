"""
Dialog for adding and editing owner/user objects.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt

from ..models import Owner


class OwnerDialog(QDialog):
    """Dialog for creating and editing owner/user objects."""
    
    def __init__(self, owner: Owner = None, parent=None):
        super().__init__(parent)
        self.owner = owner
        self.is_edit_mode = owner is not None
        
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Edit Owner" if self.is_edit_mode else "Add Owner")
        self.setModal(True)
        self.resize(450, 300)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        form_layout.addRow("Name *:", self.name_edit)
        
        self.default_tablespace_edit = QLineEdit()
        self.default_tablespace_edit.setMaxLength(100)
        form_layout.addRow("Default Tablespace:", self.default_tablespace_edit)
        
        self.temp_tablespace_edit = QLineEdit()
        self.temp_tablespace_edit.setMaxLength(100)
        form_layout.addRow("Temporary Tablespace:", self.temp_tablespace_edit)
        
        self.index_tablespace_edit = QLineEdit()
        self.index_tablespace_edit.setMaxLength(100)
        form_layout.addRow("Default Index Tablespace:", self.index_tablespace_edit)
        
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
        if self.is_edit_mode and self.owner:
            self.name_edit.setText(self.owner.name)
            self.default_tablespace_edit.setText(self.owner.default_tablespace or "")
            self.temp_tablespace_edit.setText(self.owner.temp_tablespace or "")
            self.index_tablespace_edit.setText(self.owner.default_index_tablespace or "")
            self.editionable_check.setChecked(self.owner.editionable)
            self.comment_edit.setPlainText(self.owner.comment or "")
            
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
        default_tablespace = self.default_tablespace_edit.text().strip() or None
        temp_tablespace = self.temp_tablespace_edit.text().strip() or None
        index_tablespace = self.index_tablespace_edit.text().strip() or None
        editionable = self.editionable_check.isChecked()
        comment = self.comment_edit.toPlainText().strip() or None
        
        if self.is_edit_mode:
            # Update existing owner
            self.owner.default_tablespace = default_tablespace
            self.owner.temp_tablespace = temp_tablespace
            self.owner.default_index_tablespace = index_tablespace
            self.owner.editionable = editionable
            self.owner.comment = comment
        else:
            # Create new owner
            self.owner = Owner(
                name=name,
                default_tablespace=default_tablespace,
                temp_tablespace=temp_tablespace,
                default_index_tablespace=index_tablespace,
                editionable=editionable,
                comment=comment
            )
        
        self.accept()
    
    def _validate_form(self) -> bool:
        """Validate the form data."""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Owner name is required.")
            self.name_edit.setFocus()
            return False
        
        return True
    
    def get_owner(self) -> Owner:
        """Get the owner object."""
        return self.owner