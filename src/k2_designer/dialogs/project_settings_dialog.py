"""
Dialog for managing project settings.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QFileDialog, QLabel,
                             QGroupBox, QDialogButtonBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
import os


class ProjectSettingsDialog(QDialog):
    """Dialog for editing project-wide settings."""

    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Project Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Project Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # General Settings Group
        general_group = QGroupBox("General")
        general_layout = QFormLayout()

        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter your name or organization")
        general_layout.addRow("Author:", self.author_edit)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Appearance Settings Group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()

        # Theme Mode
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("System Default", "system")
        self.theme_combo.addItem("Light Mode", "light")
        self.theme_combo.addItem("Dark Mode", "dark")
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        appearance_layout.addRow("Theme:", self.theme_combo)

        # Theme help text
        theme_help = QLabel("🎨 Changes take effect immediately")
        theme_help.setStyleSheet("color: gray; font-size: 10px;")
        appearance_layout.addRow("", theme_help)

        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        # Paths Settings Group
        paths_group = QGroupBox("Paths")
        paths_layout = QVBoxLayout()

        # Template Directory
        template_layout = QHBoxLayout()
        template_label = QLabel("Template Directory:")
        template_layout.addWidget(template_label)

        self.template_dir_edit = QLineEdit()
        self.template_dir_edit.setPlaceholderText("Directory containing Jinja2 template files")
        template_layout.addWidget(self.template_dir_edit)

        self.template_browse_btn = QPushButton("Browse...")
        self.template_browse_btn.clicked.connect(self._browse_template_dir)
        template_layout.addWidget(self.template_browse_btn)

        paths_layout.addLayout(template_layout)

        # Template directory help text
        template_help = QLabel("📁 This directory should contain .j2 template files for SQL generation")
        template_help.setStyleSheet("color: gray; font-size: 10px; padding-left: 20px;")
        paths_layout.addWidget(template_help)

        # Output Directory
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Directory:")
        output_layout.addWidget(output_label)

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Default directory for generated SQL files")
        output_layout.addWidget(self.output_dir_edit)

        self.output_browse_btn = QPushButton("Browse...")
        self.output_browse_btn.clicked.connect(self._browse_output_dir)
        output_layout.addWidget(self.output_browse_btn)

        paths_layout.addLayout(output_layout)

        # Output directory help text
        output_help = QLabel("💾 Generated SQL scripts will be saved to this directory by default")
        output_help.setStyleSheet("color: gray; font-size: 10px; padding-left: 20px;")
        paths_layout.addWidget(output_help)

        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)

        # Spacer
        layout.addStretch()

        # Info section
        info_label = QLabel(
            "ℹ️ These settings are saved with your project and can be exported/imported via JSON."
        )
        info_label.setStyleSheet("color: #0066cc; padding: 10px; background-color: #e6f2ff; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_settings(self):
        """Load current settings from the project."""
        if not self.project:
            return

        settings = self.project.settings
        self.author_edit.setText(settings.get('author', ''))
        self.template_dir_edit.setText(settings.get('template_directory', ''))
        self.output_dir_edit.setText(settings.get('output_directory', ''))

        # Load theme setting
        theme = settings.get('theme', 'system')
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

    def _browse_template_dir(self):
        """Browse for template directory."""
        current_dir = self.template_dir_edit.text() or os.path.expanduser("~")

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Template Directory",
            current_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.template_dir_edit.setText(directory)

    def _browse_output_dir(self):
        """Browse for output directory."""
        current_dir = self.output_dir_edit.text() or os.path.expanduser("~")

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if directory:
            self.output_dir_edit.setText(directory)

    def _on_theme_changed(self, index):
        """Handle theme change - apply immediately."""
        theme = self.theme_combo.currentData()
        self._apply_theme(theme)

    def _apply_theme(self, theme):
        """Apply the selected theme to the application."""
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if not app:
            return

        if theme == "dark":
            # Dark mode palette
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

            # Disabled colors
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))

            app.setPalette(palette)

        elif theme == "light":
            # Light mode palette (reset to default)
            app.setPalette(app.style().standardPalette())

        else:  # system
            # Use system default
            app.setPalette(app.style().standardPalette())

    def get_settings(self):
        """Get the settings from the dialog."""
        return {
            'author': self.author_edit.text().strip(),
            'template_directory': self.template_dir_edit.text().strip(),
            'output_directory': self.output_dir_edit.text().strip(),
            'theme': self.theme_combo.currentData()
        }

    def apply_settings(self):
        """Apply the settings to the project."""
        if self.project:
            self.project.settings = self.get_settings()
            # Apply theme immediately
            self._apply_theme(self.project.settings['theme'])

