"""
K2 Designer - Database Schema Designer

Copyright (c) 2025 Karel Švejnoha
All rights reserved.

SPDX-License-Identifier: AGPL-3.0-only OR Commercial

This software is dual-licensed:
- AGPL-3.0: Free for personal use, education, research, and internal use.
  Any modifications or derivative works must remain open-source under AGPL.
- Commercial License: Required for closed-source products, commercial distribution,
  SaaS deployment, or use in proprietary systems.

You MAY use this project at your company internally at no cost.
You MAY NOT sell, sublicense, or redistribute it as a proprietary product
without a commercial agreement.

For commercial licensing, contact: sheafraidh@gmail.com
See LICENSE file for full terms.
"""


import os
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TemplateInfo:
    """Information about a template file."""
    name: str
    description: str
    object_type: str  # table, sequence, user
    filepath: str
    filename: str
    group: str  # Directory name (tables, sequences, users, etc.)


class TemplateManager:
    """Manages template discovery and organization based on directory structure."""

    def __init__(self, templates_root_dir: str):
        self.templates_root_dir = templates_root_dir
        self.templates: Dict[str, List[TemplateInfo]] = {}  # group -> list of templates
        self._scan_templates()

    def _scan_templates(self):
        """Scan the templates directory and organize templates by group."""
        if not os.path.exists(self.templates_root_dir):
            print(f"⚠️ Templates directory not found: {self.templates_root_dir}")
            return

        # Clear existing templates
        self.templates.clear()

        # Scan subdirectories
        for entry in os.listdir(self.templates_root_dir):
            entry_path = os.path.join(self.templates_root_dir, entry)

            # Skip if not a directory
            if not os.path.isdir(entry_path):
                continue

            # Scan template files in this directory
            group_templates = self._scan_group_directory(entry, entry_path)
            if group_templates:
                self.templates[entry] = group_templates

        print(f"✅ Scanned {sum(len(t) for t in self.templates.values())} templates in {len(self.templates)} groups")

    def _scan_group_directory(self, group_name: str, directory_path: str) -> List[TemplateInfo]:
        """Scan a specific group directory for template files."""
        templates = []

        for filename in os.listdir(directory_path):
            if not filename.endswith('.j2'):
                continue

            filepath = os.path.join(directory_path, filename)
            template_info = self._parse_template_file(filepath, filename, group_name)

            if template_info:
                templates.append(template_info)

        return templates

    def _parse_template_file(self, filepath: str, filename: str, group_name: str) -> Optional[TemplateInfo]:
        """Parse a template file and extract metadata from the header."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata from Jinja2 comment block at the start
            # Format: {# name: ... \n description: ... \n object_type: ... #}
            metadata_pattern = r'\{#\s*(.*?)\s*#\}'
            match = re.search(metadata_pattern, content, re.DOTALL)

            if not match:
                # No metadata header, create default
                return TemplateInfo(
                    name=filename.replace('.sql.j2', '').replace('_', ' ').title(),
                    description=f"Template: {filename}",
                    object_type=self._guess_object_type(group_name),
                    filepath=filepath,
                    filename=filename,
                    group=group_name
                )

            # Parse metadata lines
            metadata_text = match.group(1)
            metadata = {}

            for line in metadata_text.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            return TemplateInfo(
                name=metadata.get('name', filename.replace('.sql.j2', '')),
                description=metadata.get('description', ''),
                object_type=metadata.get('object_type', self._guess_object_type(group_name)),
                filepath=filepath,
                filename=filename,
                group=group_name
            )

        except Exception as e:
            print(f"⚠️ Error parsing template {filepath}: {e}")
            return None

    def _guess_object_type(self, group_name: str) -> str:
        """Guess the object type from the group name."""
        group_lower = group_name.lower()

        if 'table' in group_lower:
            return 'table'
        elif 'sequence' in group_lower or 'seq' in group_lower:
            return 'sequence'
        elif 'user' in group_lower or 'owner' in group_lower:
            return 'user'
        else:
            return 'unknown'

    def get_groups(self) -> List[str]:
        """Get list of template groups (directory names)."""
        return sorted(self.templates.keys())

    def get_templates_for_group(self, group_name: str) -> List[TemplateInfo]:
        """Get all templates for a specific group."""
        return self.templates.get(group_name, [])

    def get_templates_for_object_type(self, object_type: str) -> Dict[str, List[TemplateInfo]]:
        """Get all templates for a specific object type, grouped by directory."""
        result = {}

        for group_name, templates in self.templates.items():
            matching_templates = [t for t in templates if t.object_type == object_type]
            if matching_templates:
                result[group_name] = matching_templates

        return result

    def get_template_info(self, filepath: str) -> Optional[TemplateInfo]:
        """Get template info by filepath."""
        for templates in self.templates.values():
            for template in templates:
                if template.filepath == filepath:
                    return template
        return None

    def get_all_templates(self) -> List[TemplateInfo]:
        """Get all templates as a flat list."""
        result = []
        for templates in self.templates.values():
            result.extend(templates)
        return result

