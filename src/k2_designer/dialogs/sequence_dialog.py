"""
Dialog for adding and editing sequence objects.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QPushButton, QLabel,
                             QCheckBox, QComboBox, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt

from ..models import Sequence


class SequenceDialog(QDialog):
    """Dialog for creating and editing sequence objects."""
    
    def __init__(self, sequence: Sequence = None, owners: list = None, selected_owner: str = None, parent=None):
        super().__init__(parent)
        self.sequence = sequence
        self.owners = owners or []
        self.selected_owner = selected_owner
        self.is_edit_mode = sequence is not None
        
        self._setup_ui()
        self._load_data()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Edit Sequence" if self.is_edit_mode else "Add Sequence")
        self.setModal(True)
        self.resize(450, 400)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(50)
        form_layout.addRow("Name *:", self.name_edit)
        
        self.owner_combo = QComboBox()
        self.owner_combo.addItems([owner.name for owner in self.owners])
        form_layout.addRow("Owner *:", self.owner_combo)
        
        # Sequence attributes
        self.start_with_spin = QSpinBox()
        self.start_with_spin.setRange(-2147483648, 2147483647)
        self.start_with_spin.setValue(1)
        form_layout.addRow("Start With:", self.start_with_spin)
        
        self.increment_by_spin = QSpinBox()
        self.increment_by_spin.setRange(-2147483648, 2147483647)
        self.increment_by_spin.setValue(1)
        form_layout.addRow("Increment By:", self.increment_by_spin)
        
        self.min_value_edit = QLineEdit()
        self.min_value_edit.setPlaceholderText("Leave empty for no minimum")
        form_layout.addRow("Minimum Value:", self.min_value_edit)
        
        self.max_value_edit = QLineEdit()
        self.max_value_edit.setPlaceholderText("Leave empty for no maximum")
        form_layout.addRow("Maximum Value:", self.max_value_edit)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(0, 2147483647)
        self.cache_size_spin.setValue(20)
        form_layout.addRow("Cache Size:", self.cache_size_spin)
        
        self.cycle_check = QCheckBox()
        form_layout.addRow("Cycle:", self.cycle_check)
        
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
        if self.is_edit_mode and self.sequence:
            self.name_edit.setText(self.sequence.name)
            
            # Set owner
            owner_index = self.owner_combo.findText(self.sequence.owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)
            
            self.start_with_spin.setValue(self.sequence.start_with)
            self.increment_by_spin.setValue(self.sequence.increment_by)
            
            if self.sequence.min_value is not None:
                self.min_value_edit.setText(str(self.sequence.min_value))
            
            if self.sequence.max_value is not None:
                self.max_value_edit.setText(str(self.sequence.max_value))
            
            self.cache_size_spin.setValue(self.sequence.cache_size)
            self.cycle_check.setChecked(self.sequence.cycle)
            self.comment_edit.setPlainText(self.sequence.comment or "")
            
            # Make name readonly in edit mode
            self.name_edit.setReadOnly(True)
        elif self.selected_owner:
            # Pre-select owner in add mode
            owner_index = self.owner_combo.findText(self.selected_owner)
            if owner_index >= 0:
                self.owner_combo.setCurrentIndex(owner_index)
    
    def _connect_signals(self):
        """Connect signals."""
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
    
    def _on_ok(self):
        """Handle OK button click."""
        if not self._validate_form():
            return
        
        name = self.name_edit.text().strip()
        owner = self.owner_combo.currentText()
        start_with = self.start_with_spin.value()
        increment_by = self.increment_by_spin.value()
        
        # Parse min/max values
        min_value = None
        max_value = None
        
        if self.min_value_edit.text().strip():
            try:
                min_value = int(self.min_value_edit.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Minimum value must be a valid integer.")
                self.min_value_edit.setFocus()
                return
        
        if self.max_value_edit.text().strip():
            try:
                max_value = int(self.max_value_edit.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Maximum value must be a valid integer.")
                self.max_value_edit.setFocus()
                return
        
        # Validate min/max relationship
        if min_value is not None and max_value is not None and min_value >= max_value:
            QMessageBox.warning(self, "Validation Error", "Minimum value must be less than maximum value.")
            self.min_value_edit.setFocus()
            return
        
        cache_size = self.cache_size_spin.value()
        cycle = self.cycle_check.isChecked()
        comment = self.comment_edit.toPlainText().strip() or None
        
        if self.is_edit_mode:
            # Update existing sequence
            self.sequence.start_with = start_with
            self.sequence.increment_by = increment_by
            self.sequence.min_value = min_value
            self.sequence.max_value = max_value
            self.sequence.cache_size = cache_size
            self.sequence.cycle = cycle
            self.sequence.comment = comment
        else:
            # Create new sequence
            self.sequence = Sequence(
                name=name,
                owner=owner,
                start_with=start_with,
                increment_by=increment_by,
                min_value=min_value,
                max_value=max_value,
                cache_size=cache_size,
                cycle=cycle,
                comment=comment
            )
        
        self.accept()
    
    def _validate_form(self) -> bool:
        """Validate the form data."""
        name = self.name_edit.text().strip()
        owner = self.owner_combo.currentText()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Sequence name is required.")
            self.name_edit.setFocus()
            return False
        
        if not owner:
            QMessageBox.warning(self, "Validation Error", "Owner is required.")
            self.owner_combo.setFocus()
            return False
        
        # Validate increment_by is not zero
        if self.increment_by_spin.value() == 0:
            QMessageBox.warning(self, "Validation Error", "Increment by cannot be zero.")
            self.increment_by_spin.setFocus()
            return False
        
        return True
    
    def get_sequence(self) -> Sequence:
        """Get the sequence object."""
        return self.sequence