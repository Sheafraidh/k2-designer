#!/usr/bin/env python3
"""
Migration utility to convert old SQLite .k2p files to JSON format.
"""

import os
import sys
import json
import sqlite3
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from k2_designer.models import (Project, Domain, Owner, Table, Column,
                                Key, Index, Partitioning, PartitionType,
                                Sequence, Diagram)
from k2_designer.models.base import Stereotype, StereotypeType


def is_sqlite_file(file_path: str) -> bool:
    """Check if a file is a SQLite database."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            return header[:16] == b'SQLite format 3\x00'
    except:
        return False


def load_project_from_sqlite(file_path: str) -> Optional[Project]:
    """Load a project from an old SQLite .k2p file."""
    if not os.path.exists(file_path):
        return None

    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        # Load project info
        cursor.execute('SELECT name, description FROM project_info LIMIT 1')
        project_row = cursor.fetchone()

        if not project_row:
            conn.close()
            return None

        project = Project(project_row[0], project_row[1], init_default_stereotypes=False)

        # Load domains
        cursor.execute('SELECT name, data_type, comment FROM domains')
        for row in cursor.fetchall():
            domain = Domain(row[0], row[1], row[2])
            project.add_domain(domain)

        # Load owners
        cursor.execute('''
            SELECT name, default_tablespace, temp_tablespace,
                   default_index_tablespace, editionable, comment
            FROM owners
        ''')
        for row in cursor.fetchall():
            owner = Owner(row[0], row[1], row[2], row[3], bool(row[4]), row[5])
            project.add_owner(owner)

        # Load stereotypes
        cursor.execute('''
            SELECT name, stereotype_type, description, background_color
            FROM stereotypes
        ''')
        for row in cursor.fetchall():
            stereotype = Stereotype(
                name=row[0],
                stereotype_type=StereotypeType(row[1]),
                description=row[2],
                background_color=row[3]
            )
            project.add_stereotype(stereotype)

        # Load tables
        cursor.execute('''
            SELECT id, name, owner, tablespace, stereotype, color,
                   domain, editionable, comment
            FROM tables
        ''')

        table_id_map = {}

        for row in cursor.fetchall():
            table = Table(
                name=row[1],
                owner=row[2],
                tablespace=row[3],
                stereotype=row[4],
                color=row[5],
                domain=row[6],
                editionable=bool(row[7]),
                comment=row[8]
            )

            table_id_map[row[0]] = table
            project.add_table(table)

        # Load columns for each table
        for table_id, table in table_id_map.items():
            cursor.execute('''
                SELECT name, data_type, nullable, default_value, comment, domain, stereotype
                FROM columns
                WHERE table_id = ?
                ORDER BY column_order
            ''', (table_id,))

            for col_row in cursor.fetchall():
                column = Column(
                    name=col_row[0],
                    data_type=col_row[1],
                    nullable=bool(col_row[2]),
                    default=col_row[3],
                    comment=col_row[4],
                    domain=col_row[5],
                    stereotype=col_row[6]
                )
                table.add_column(column)

            # Load keys
            cursor.execute('''
                SELECT name, columns FROM table_keys WHERE table_id = ?
            ''', (table_id,))

            for key_row in cursor.fetchall():
                key = Key(key_row[0], json.loads(key_row[1]))
                table.add_key(key)

            # Load indexes
            cursor.execute('''
                SELECT name, columns, tablespace FROM table_indexes WHERE table_id = ?
            ''', (table_id,))

            for idx_row in cursor.fetchall():
                index = Index(idx_row[0], json.loads(idx_row[1]), idx_row[2])
                table.add_index(index)

            # Load partitioning
            cursor.execute('''
                SELECT columns, partition_type FROM table_partitioning WHERE table_id = ?
            ''', (table_id,))

            part_row = cursor.fetchone()
            if part_row:
                partitioning = Partitioning(
                    json.loads(part_row[0]),
                    PartitionType(part_row[1])
                )
                table.set_partitioning(partitioning)

        # Load sequences
        cursor.execute('''
            SELECT name, owner, start_with, increment_by, min_value,
                   max_value, cache_size, cycle, comment
            FROM sequences
        ''')

        for row in cursor.fetchall():
            sequence = Sequence(
                name=row[0],
                owner=row[1],
                start_with=row[2],
                increment_by=row[3],
                min_value=row[4],
                max_value=row[5],
                cache_size=row[6],
                cycle=bool(row[7]),
                comment=row[8]
            )
            project.add_sequence(sequence)

        # Load foreign keys
        cursor.execute('''
            SELECT source_table, source_column, target_table, target_column
            FROM foreign_keys
        ''')

        for row in cursor.fetchall():
            project.add_foreign_key(row[0], row[1], row[2], row[3])

        # Load diagrams
        cursor.execute('''
            SELECT name, description, is_active, zoom_level, scroll_x, scroll_y
            FROM diagrams
        ''')

        for row in cursor.fetchall():
            diagram = Diagram(row[0], row[1])
            diagram.is_active = bool(row[2])
            diagram.zoom_level = row[3]
            diagram.scroll_x = row[4]
            diagram.scroll_y = row[5]

            # Load diagram items
            cursor.execute('''
                SELECT object_type, object_name, x, y, width, height
                FROM diagram_items
                WHERE diagram_name = ?
            ''', (diagram.name,))

            for item_row in cursor.fetchall():
                diagram.add_item(
                    item_row[0],
                    item_row[1],
                    item_row[2],
                    item_row[3],
                    item_row[4],
                    item_row[5]
                )

            # Load diagram connections
            cursor.execute('''
                SELECT source_table, target_table, connection_type, label
                FROM diagram_connections
                WHERE diagram_name = ?
            ''', (diagram.name,))

            for conn_row in cursor.fetchall():
                diagram.add_connection(
                    conn_row[0],
                    conn_row[1],
                    conn_row[2],
                    conn_row[3]
                )

            project.add_diagram(diagram)

        # Load last active diagram
        cursor.execute('SELECT description FROM project_info LIMIT 1')
        desc_row = cursor.fetchone()
        if desc_row and desc_row[0]:
            try:
                desc_data = json.loads(desc_row[0])
                if isinstance(desc_data, dict) and 'last_active_diagram' in desc_data:
                    project.last_active_diagram = desc_data['last_active_diagram']
                    project.description = desc_data.get('description', '')
            except (json.JSONDecodeError, TypeError):
                project.description = desc_row[0]

        conn.close()
        return project

    except Exception as e:
        print(f"❌ Error loading SQLite project: {e}")
        import traceback
        traceback.print_exc()
        return None


def migrate_sqlite_to_json(sqlite_file: str, json_file: str = None) -> bool:
    """Migrate a SQLite .k2p file to JSON format."""
    if not json_file:
        # Keep same name but with .json extension
        json_file = os.path.splitext(sqlite_file)[0] + '_migrated.k2p'

    print(f"🔄 Migrating {sqlite_file} to JSON format...")

    # Load from SQLite
    project = load_project_from_sqlite(sqlite_file)
    if not project:
        print(f"❌ Failed to load SQLite project")
        return False

    print(f"✅ Loaded project: {project.name}")
    print(f"   - {len(project.domains)} domains")
    print(f"   - {len(project.owners)} owners")
    print(f"   - {len(project.tables)} tables")
    print(f"   - {len(project.sequences)} sequences")
    print(f"   - {len(project.diagrams)} diagrams")

    # Save to JSON
    from k2_designer.controllers.project_manager import ProjectManager
    pm = ProjectManager()
    pm.current_project = project

    if pm.save_project(json_file):
        print(f"✅ Successfully migrated to: {json_file}")
        return True
    else:
        print(f"❌ Failed to save JSON project")
        return False


def main():
    """Main migration script."""
    if len(sys.argv) < 2:
        print("Usage: python migrate_sqlite_to_json.py <file.k2p> [output.k2p]")
        print("\nOr to migrate all .k2p files in current directory:")
        print("  python migrate_sqlite_to_json.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # Migrate all .k2p files in current directory
        k2p_files = [f for f in os.listdir('.') if f.endswith('.k2p') and is_sqlite_file(f)]

        if not k2p_files:
            print("No SQLite .k2p files found in current directory")
            sys.exit(0)

        print(f"Found {len(k2p_files)} SQLite .k2p files to migrate\n")

        success_count = 0
        for k2p_file in k2p_files:
            output_file = os.path.splitext(k2p_file)[0] + '_json.k2p'
            if migrate_sqlite_to_json(k2p_file, output_file):
                success_count += 1
            print()

        print(f"\n✅ Successfully migrated {success_count}/{len(k2p_files)} files")

    else:
        # Migrate single file
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None

        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            sys.exit(1)

        if not is_sqlite_file(input_file):
            print(f"❌ File is not a SQLite database: {input_file}")
            sys.exit(1)

        if migrate_sqlite_to_json(input_file, output_file):
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

