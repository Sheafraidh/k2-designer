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
from typing import Optional, List
from jinja2 import Environment, FileSystemLoader, Template


class NamingRulesEngine:
    """Engine for generating database object names based on Jinja2 templates."""

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the naming rules engine.

        Args:
            templates_dir: Directory containing naming_rules.j2 template
        """
        if templates_dir is None:
            # Default to templates directory in project root
            templates_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'templates'
            )

        self.templates_dir = templates_dir
        self.template_file = os.path.join(templates_dir, 'naming_rules.j2')

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.env.filters['abbreviate'] = self._abbreviate

        # Load template
        self._load_template()

    def _load_template(self):
        """Load the naming rules template."""
        try:
            if os.path.exists(self.template_file):
                self.template = self.env.get_template('naming_rules.j2')
            else:
                # Create default template if it doesn't exist
                self._create_default_template()
                self.template = self.env.get_template('naming_rules.j2')
        except Exception as e:
            print(f"⚠ Error loading naming rules template: {e}")
            self.template = None

    def _create_default_template(self):
        """Create default naming rules template."""
        # This is handled by the template file we created
        pass

    def _abbreviate(self, text: str, length: int) -> str:
        """Abbreviate text to maximum length."""
        if len(text) <= length:
            return text
        return text[:length]

    def _count_existing_keys(self, table, key_type: str) -> int:
        """Count existing keys of a specific type in the table."""
        if not table or not hasattr(table, 'keys'):
            return 0

        from ..models.base import Key
        count = 0
        for key in table.keys:
            if key.key_type == key_type:
                count += 1
        return count

    def _count_existing_indexes(self, table) -> int:
        """Count existing indexes in the table."""
        if not table or not hasattr(table, 'indexes'):
            return 0
        return len(table.indexes)

    def generate_primary_key_name(self, table_name: str, columns: List[str],
                                   table=None, owner: Optional[str] = None) -> str:
        """
        Generate a primary key name.

        Args:
            table_name: Name of the table
            columns: List of column names in the key
            table: Optional table object to check existing keys
            owner: Optional owner/schema name

        Returns:
            Generated primary key name
        """
        if not self.template:
            # Fallback to default naming
            return f"{table_name}_PK"

        try:
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.PRIMARY) + 1

            # Render the primary_key macro
            macro_call = "{{ primary_key(table_name, columns, number) }}"
            result = self.env.from_string(
                "{% from 'naming_rules.j2' import primary_key %}\n" + macro_call
            ).render(
                table_name=table_name,
                columns=columns,
                number=number,
                owner=owner or ""
            )
            return result.strip()
        except Exception as e:
            print(f"⚠ Error generating primary key name: {e}")
            return f"{table_name}_PK"

    def generate_foreign_key_name(self, table_name: str, columns: List[str],
                                   referenced_table: Optional[str] = None,
                                   table=None, owner: Optional[str] = None) -> str:
        """
        Generate a foreign key name.

        Args:
            table_name: Name of the table
            columns: List of column names in the key
            referenced_table: Name of the referenced table
            table: Optional table object to check existing keys
            owner: Optional owner/schema name

        Returns:
            Generated foreign key name
        """
        if not self.template:
            # Fallback to default naming
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.FOREIGN) + 1
            return f"{table_name}_FK{number}"

        try:
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.FOREIGN) + 1

            # Render the foreign_key macro
            macro_call = "{{ foreign_key(table_name, columns, number, referenced_table) }}"
            result = self.env.from_string(
                "{% from 'naming_rules.j2' import foreign_key %}\n" + macro_call
            ).render(
                table_name=table_name,
                columns=columns,
                number=number,
                referenced_table=referenced_table or "",
                owner=owner or ""
            )
            return result.strip()
        except Exception as e:
            print(f"⚠ Error generating foreign key name: {e}")
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.FOREIGN) + 1
            return f"{table_name}_FK{number}"

    def generate_unique_key_name(self, table_name: str, columns: List[str],
                                  table=None, owner: Optional[str] = None) -> str:
        """
        Generate a unique key name.

        Args:
            table_name: Name of the table
            columns: List of column names in the key
            table: Optional table object to check existing keys
            owner: Optional owner/schema name

        Returns:
            Generated unique key name
        """
        if not self.template:
            # Fallback to default naming
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.UNIQUE) + 1
            return f"{table_name}_UK{number}"

        try:
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.UNIQUE) + 1

            # Render the unique_key macro
            macro_call = "{{ unique_key(table_name, columns, number) }}"
            result = self.env.from_string(
                "{% from 'naming_rules.j2' import unique_key %}\n" + macro_call
            ).render(
                table_name=table_name,
                columns=columns,
                number=number,
                owner=owner or ""
            )
            return result.strip()
        except Exception as e:
            print(f"⚠ Error generating unique key name: {e}")
            from ..models.base import Key
            number = self._count_existing_keys(table, Key.UNIQUE) + 1
            return f"{table_name}_UK{number}"

    def generate_index_name(self, table_name: str, columns: List[str],
                           table=None, owner: Optional[str] = None) -> str:
        """
        Generate an index name.

        Args:
            table_name: Name of the table
            columns: List of column names in the index
            table: Optional table object to check existing indexes
            owner: Optional owner/schema name

        Returns:
            Generated index name
        """
        if not self.template:
            # Fallback to default naming
            number = self._count_existing_indexes(table) + 1
            return f"{table_name}_I{number}"

        try:
            number = self._count_existing_indexes(table) + 1

            # Render the index_name macro
            macro_call = "{{ index_name(table_name, columns, number) }}"
            result = self.env.from_string(
                "{% from 'naming_rules.j2' import index_name %}\n" + macro_call
            ).render(
                table_name=table_name,
                columns=columns,
                number=number,
                owner=owner or ""
            )
            return result.strip()
        except Exception as e:
            print(f"⚠ Error generating index name: {e}")
            number = self._count_existing_indexes(table) + 1
            return f"{table_name}_I{number}"

