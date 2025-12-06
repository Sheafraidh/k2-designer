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

import json
import os
from typing import Optional

from ..models import Project


class ProjectManager:
    """Manages project file operations and JSON storage."""

    def __init__(self):
        self.current_project: Optional[Project] = None
        self.file_path: Optional[str] = None
    
    def new_project(self, name: str = "Untitled Project", description: str = None) -> Project:
        """Create a new project."""
        self.current_project = Project(name, description)
        self.file_path = None
        return self.current_project
    
    def save_project(self, file_path: str = None) -> bool:
        """Save the current project to JSON format."""
        if not self.current_project:
            return False
        
        if file_path:
            self.file_path = file_path
        elif not self.file_path:
            return False
        
        try:
            # Ensure .k2p extension
            if not self.file_path.endswith('.k2p'):
                self.file_path += '.k2p'
            
            # Convert project to dictionary
            project_data = self._project_to_dict(self.current_project)

            # Write to JSON file with nice formatting
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)

            self.current_project.file_path = self.file_path
            print(f"✅ Project saved: {self.file_path}")
            return True

        except Exception as e:
            print(f"❌ Error saving project: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_project(self, file_path: str) -> Optional[Project]:
        """Load a project from JSON format."""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Convert dictionary to project
            project = self._dict_to_project(project_data)

            if project:
                self.current_project = project
                self.file_path = file_path
                project.file_path = file_path
                print(f"✅ Project loaded: {file_path}")

            return project

        except Exception as e:
            print(f"❌ Error loading project: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _project_to_dict(self, project: Project) -> dict:
        """Convert a Project object to a dictionary for JSON serialization."""
        return {
            "name": project.name,
            "description": project.description,
            "last_active_diagram": project.last_active_diagram,
            "domains": [domain.to_dict() for domain in sorted(project.domains, key=lambda x: x.guid)],
            "owners": [owner.to_dict() for owner in sorted(project.owners, key=lambda x: x.guid)],
            "stereotypes": [stereotype.to_dict() for stereotype in sorted(project.stereotypes, key=lambda x: x.guid)],
            "tables": [table.to_dict() for table in sorted(project.tables, key=lambda x: x.guid)],
            "sequences": [seq.to_dict() for seq in sorted(project.sequences, key=lambda x: x.guid)],
            "foreign_keys": [
                {
                    "source_key": fk_key,
                    "target_table": fk_value["target_table"],
                    "target_column": fk_value["target_column"]
                }
                for fk_key, fk_value in sorted(project.foreign_keys.items())
            ],
            "diagrams": [diagram.to_dict() for diagram in sorted(project.diagrams, key=lambda x: x.guid)]
        }

    def _dict_to_project(self, data: dict) -> Optional[Project]:
        """Convert a dictionary to a Project object."""
        from ..models import (Domain, Owner, Table, Column, Key, Index,
                             Partitioning, PartitionType, Sequence, Diagram)
        from ..models.base import Stereotype, StereotypeType

        try:
            # Create project
            project = Project(
                name=data.get("name", "Untitled Project"),
                description=data.get("description"),
                init_default_stereotypes=False
            )

            project.last_active_diagram = data.get("last_active_diagram")

            # Load domains
            for domain_data in data.get("domains", []):
                domain = Domain(
                    name=domain_data["name"],
                    data_type=domain_data["data_type"],
                    comment=domain_data.get("comment")
                )
                project.add_domain(domain)

            # Load owners
            for owner_data in data.get("owners", []):
                owner = Owner(
                    name=owner_data["name"],
                    default_tablespace=owner_data.get("default_tablespace"),
                    temp_tablespace=owner_data.get("temp_tablespace"),
                    default_index_tablespace=owner_data.get("default_index_tablespace"),
                    editionable=owner_data.get("editionable", False),
                    comment=owner_data.get("comment")
                )
                project.add_owner(owner)

            # Load stereotypes
            for stereotype_data in data.get("stereotypes", []):
                stereotype = Stereotype(
                    name=stereotype_data["name"],
                    stereotype_type=StereotypeType(stereotype_data["stereotype_type"]),
                    description=stereotype_data.get("description"),
                    background_color=stereotype_data["background_color"]
                )
                project.add_stereotype(stereotype)

            # Load tables
            for table_data in data.get("tables", []):
                table = Table(
                    name=table_data["name"],
                    owner=table_data["owner"],
                    tablespace=table_data.get("tablespace"),
                    stereotype=table_data.get("stereotype"),
                    color=table_data.get("color"),
                    domain=table_data.get("domain"),
                    editionable=table_data.get("editionable", False),
                    comment=table_data.get("comment")
                )

                # Load columns
                for col_data in table_data.get("columns", []):
                    column = Column(
                        name=col_data["name"],
                        data_type=col_data["data_type"],
                        nullable=col_data.get("nullable", True),
                        default=col_data.get("default"),
                        comment=col_data.get("comment"),
                        domain=col_data.get("domain"),
                        stereotype=col_data.get("stereotype")
                    )
                    table.add_column(column)

                # Load keys
                for key_data in table_data.get("keys", []):
                    key = Key(
                        name=key_data["name"],
                        columns=key_data["columns"]
                    )
                    table.add_key(key)

                # Load indexes
                for index_data in table_data.get("indexes", []):
                    index = Index(
                        name=index_data["name"],
                        columns=index_data["columns"],
                        tablespace=index_data.get("tablespace")
                    )
                    table.add_index(index)

                # Load partitioning
                part_data = table_data.get("partitioning")
                if part_data:
                    partitioning = Partitioning(
                        columns=part_data["columns"],
                        partition_type=PartitionType(part_data["partition_type"])
                    )
                    table.set_partitioning(partitioning)

                project.add_table(table)

            # Load sequences
            for seq_data in data.get("sequences", []):
                sequence = Sequence(
                    name=seq_data["name"],
                    owner=seq_data["owner"],
                    start_with=seq_data.get("start_with", 1),
                    increment_by=seq_data.get("increment_by", 1),
                    min_value=seq_data.get("min_value"),
                    max_value=seq_data.get("max_value"),
                    cache_size=seq_data.get("cache_size", 20),
                    cycle=seq_data.get("cycle", False),
                    comment=seq_data.get("comment")
                )
                project.add_sequence(sequence)

            # Load foreign keys
            for fk_data in data.get("foreign_keys", []):
                source_key = fk_data["source_key"]
                source_parts = source_key.split('.')
                if len(source_parts) >= 2:
                    source_table = '.'.join(source_parts[:-1])
                    source_column = source_parts[-1]
                    project.add_foreign_key(
                        source_table,
                        source_column,
                        fk_data["target_table"],
                        fk_data["target_column"]
                    )

            # Load diagrams
            for diagram_data in data.get("diagrams", []):
                diagram = Diagram(
                    name=diagram_data["name"],
                    description=diagram_data.get("description")
                )
                diagram.is_active = diagram_data.get("is_active", False)
                diagram.zoom_level = diagram_data.get("zoom_level", 1.0)
                diagram.scroll_x = diagram_data.get("scroll_x", 0.0)
                diagram.scroll_y = diagram_data.get("scroll_y", 0.0)

                # Load diagram items
                for item_data in diagram_data.get("items", []):
                    diagram.add_item(
                        object_type=item_data["object_type"],
                        object_name=item_data["object_name"],
                        x=item_data["x"],
                        y=item_data["y"],
                        width=item_data.get("width"),
                        height=item_data.get("height")
                    )

                # Load diagram connections
                for conn_data in diagram_data.get("connections", []):
                    diagram.add_connection(
                        source_table=conn_data["source_table"],
                        target_table=conn_data["target_table"],
                        connection_type=conn_data.get("connection_type", "manual"),
                        label=conn_data.get("label")
                    )

                project.add_diagram(diagram)

            return project

        except Exception as e:
            print(f"❌ Error converting dict to project: {e}")
            import traceback
            traceback.print_exc()
            return None
