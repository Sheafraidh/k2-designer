"""
User settings manager for K2 Designer.
Settings are saved per-user, not per-project.
"""

import json
import os
from pathlib import Path
from typing import Optional


class UserSettingsManager:
    """Manages user-specific settings saved to user's home directory."""

    def __init__(self):
        self.settings_dir = Path.home() / '.k2designer'
        self.settings_file = self.settings_dir / 'settings.json'
        self._settings = None
        self._ensure_settings_dir()
        self.load_settings()

    def _ensure_settings_dir(self):
        """Ensure the settings directory exists."""
        if not self.settings_dir.exists():
            self.settings_dir.mkdir(parents=True, exist_ok=True)

    def _get_default_settings(self):
        """Get default settings."""
        return {
            'author': '',
            'template_directory': '',
            'output_directory': '',
            'theme': 'system',  # system, light, or dark
            'last_project_path': ''  # Path to last opened project
        }

    def load_settings(self):
        """Load settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                print(f"✓ User settings loaded from: {self.settings_file}")
            except Exception as e:
                print(f"⚠ Error loading user settings: {e}")
                self._settings = self._get_default_settings()
        else:
            self._settings = self._get_default_settings()
            self.save_settings()

    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            print(f"✓ User settings saved to: {self.settings_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving user settings: {e}")
            return False

    def get_setting(self, key: str, default=None):
        """Get a specific setting value."""
        return self._settings.get(key, default)

    def set_setting(self, key: str, value):
        """Set a specific setting value."""
        self._settings[key] = value
        self.save_settings()

    def get_all_settings(self):
        """Get all settings as a dictionary."""
        return self._settings.copy()

    def update_settings(self, settings_dict: dict):
        """Update multiple settings at once."""
        self._settings.update(settings_dict)
        self.save_settings()

    @property
    def author(self):
        """Get author setting."""
        return self._settings.get('author', '')

    @author.setter
    def author(self, value):
        """Set author setting."""
        self._settings['author'] = value
        self.save_settings()

    @property
    def template_directory(self):
        """Get template directory setting."""
        return self._settings.get('template_directory', '')

    @template_directory.setter
    def template_directory(self, value):
        """Set template directory setting."""
        self._settings['template_directory'] = value
        self.save_settings()

    @property
    def output_directory(self):
        """Get output directory setting."""
        return self._settings.get('output_directory', '')

    @output_directory.setter
    def output_directory(self, value):
        """Set output directory setting."""
        self._settings['output_directory'] = value
        self.save_settings()

    @property
    def theme(self):
        """Get theme setting."""
        return self._settings.get('theme', 'system')

    @theme.setter
    def theme(self, value):
        """Set theme setting."""
        self._settings['theme'] = value
        self.save_settings()

    @property
    def last_project_path(self):
        """Get last project path setting."""
        return self._settings.get('last_project_path', '')

    @last_project_path.setter
    def last_project_path(self, value):
        """Set last project path setting."""
        self._settings['last_project_path'] = value
        self.save_settings()

