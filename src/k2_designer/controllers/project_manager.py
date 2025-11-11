"""
Project manager for handling file operations and SQLite storage.
"""

import sqlite3
import json
import os
from typing import Optional

from ..models import Project


class ProjectManager:
    """Manages project file operations and SQLite storage."""
    
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.file_path: Optional[str] = None
    
    def new_project(self, name: str = "Untitled Project", description: str = None) -> Project:
        """Create a new project."""
        self.current_project = Project(name, description)
        self.file_path = None
        return self.current_project
    
    def save_project(self, file_path: str = None) -> bool:
        """Save the current project to SQLite database."""
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
            
            # Create database connection
            conn = sqlite3.connect(self.file_path)
            cursor = conn.cursor()
            
            # Create tables
            self._create_database_schema(cursor)
            
            # Clear existing data
            self._clear_database(cursor)
            
            # Save project data
            self._save_project_data(cursor)
            
            conn.commit()
            conn.close()
            
            self.current_project.file_path = self.file_path
            return True
            
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def load_project(self, file_path: str) -> Optional[Project]:
        """Load a project from SQLite database."""
        if not os.path.exists(file_path):
            return None
        
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Migrate database schema if needed
            self._migrate_database_schema(cursor)
            
            # Commit any migration changes
            conn.commit()
            
            # Load project data
            project = self._load_project_data(cursor)
            
            conn.close()
            
            if project:
                self.current_project = project
                self.file_path = file_path
                project.file_path = file_path
            
            return project
            
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
    
    def save_project_to_json(self, file_path: str = None) -> bool:
        """Save the current project to JSON format."""
        if not self.current_project:
            return False

        if file_path:
            json_file_path = file_path
        elif self.file_path:
            # Use same base name but with .json extension
            json_file_path = os.path.splitext(self.file_path)[0] + '.json'
        else:
            return False

        try:
            # Ensure .json extension
            if not json_file_path.endswith('.json'):
                json_file_path += '.json'

            # Convert project to dictionary
            project_data = self._project_to_dict(self.current_project)

            # Write to JSON file with nice formatting
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Project saved to JSON: {json_file_path}")
            return True

        except Exception as e:
            print(f"❌ Error saving project to JSON: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_project_from_json(self, file_path: str) -> Optional[Project]:
        """Load a project from JSON format."""
        if not os.path.exists(file_path):
            print(f"❌ JSON file not found: {file_path}")
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
                print(f"✅ Project loaded from JSON: {file_path}")

            return project

        except Exception as e:
            print(f"❌ Error loading project from JSON: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_database_schema(self, cursor: sqlite3.Cursor):
        """Create the database schema for storing project data."""
        # Check if this is an existing database and migrate if needed
        self._migrate_database_schema(cursor)
        
        # Project metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_info (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_date TEXT,
                modified_date TEXT
            )
        ''')
        
        # Project settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_settings (
                id INTEGER PRIMARY KEY,
                author TEXT,
                template_directory TEXT,
                output_directory TEXT,
                theme TEXT DEFAULT 'system'
            )
        ''')

        # Domains
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                data_type TEXT NOT NULL,
                comment TEXT
            )
        ''')
        
        # Owners
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS owners (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                default_tablespace TEXT,
                temp_tablespace TEXT,
                default_index_tablespace TEXT,
                editionable BOOLEAN DEFAULT 0,
                comment TEXT
            )
        ''')
        
        # Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                tablespace TEXT,
                stereotype TEXT DEFAULT 'business',
                color TEXT,
                domain TEXT,
                editionable BOOLEAN DEFAULT 0,
                comment TEXT,
                UNIQUE(name, owner),
                FOREIGN KEY (owner) REFERENCES owners(name)
            )
        ''')
        
        # Columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY,
                table_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                data_type TEXT NOT NULL,
                nullable BOOLEAN DEFAULT 1,
                default_value TEXT,
                comment TEXT,
                domain TEXT,
                stereotype TEXT,
                column_order INTEGER,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE
            )
        ''')
        
        # Keys
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS table_keys (
                id INTEGER PRIMARY KEY,
                table_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                columns TEXT NOT NULL,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE
            )
        ''')
        
        # Indexes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS table_indexes (
                id INTEGER PRIMARY KEY,
                table_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                columns TEXT NOT NULL,
                tablespace TEXT,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE
            )
        ''')
        
        # Partitioning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS table_partitioning (
                id INTEGER PRIMARY KEY,
                table_id INTEGER NOT NULL,
                columns TEXT NOT NULL,
                partition_type TEXT NOT NULL,
                FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE
            )
        ''')
        
        # Sequences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                owner TEXT NOT NULL,
                start_with INTEGER DEFAULT 1,
                increment_by INTEGER DEFAULT 1,
                min_value INTEGER,
                max_value INTEGER,
                cache_size INTEGER DEFAULT 20,
                cycle BOOLEAN DEFAULT 0,
                comment TEXT,
                UNIQUE(name, owner),
                FOREIGN KEY (owner) REFERENCES owners(name)
            )
        ''')
        
        # Foreign keys
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foreign_keys (
                id INTEGER PRIMARY KEY,
                source_table TEXT NOT NULL,
                source_column TEXT NOT NULL,
                target_table TEXT NOT NULL,
                target_column TEXT NOT NULL
            )
        ''')
        
        # Diagrams
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagrams (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 0,
                zoom_level REAL DEFAULT 1.0,
                scroll_x REAL DEFAULT 0.0,
                scroll_y REAL DEFAULT 0.0
            )
        ''')
        
        # Diagram items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagram_items (
                id INTEGER PRIMARY KEY,
                diagram_name TEXT NOT NULL,
                object_type TEXT NOT NULL,
                object_name TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                width REAL,
                height REAL,
                FOREIGN KEY (diagram_name) REFERENCES diagrams(name) ON DELETE CASCADE
            )
        ''')
        
        # Diagram connections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagram_connections (
                id INTEGER PRIMARY KEY,
                diagram_name TEXT NOT NULL,
                source_table TEXT NOT NULL,
                target_table TEXT NOT NULL,
                connection_type TEXT DEFAULT 'manual',
                label TEXT,
                FOREIGN KEY (diagram_name) REFERENCES diagrams(name) ON DELETE CASCADE
            )
        ''')
        
        # Stereotypes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stereotypes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                stereotype_type TEXT NOT NULL,
                description TEXT,
                background_color TEXT NOT NULL,
                UNIQUE(name, stereotype_type)
            )
        ''')
    
    def _migrate_database_schema(self, cursor: sqlite3.Cursor):
        """Migrate existing database schema to support new features."""
        try:
            # Check if domain column exists in columns table
            cursor.execute("PRAGMA table_info(columns)")
            columns_info = cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Add domain column if it doesn't exist
            if 'domain' not in column_names:
                cursor.execute('ALTER TABLE columns ADD COLUMN domain TEXT')
                print("Added domain column to existing database")
                
            # Add stereotype column if it doesn't exist
            if 'stereotype' not in column_names:
                cursor.execute('ALTER TABLE columns ADD COLUMN stereotype TEXT')
                print("Added stereotype column to existing database")
        except sqlite3.OperationalError:
            # Table doesn't exist yet, will be created by schema creation
            pass
    
    def _clear_database(self, cursor: sqlite3.Cursor):
        """Clear all data from the database."""
        tables = [
            'diagram_connections', 'diagram_items', 'diagrams', 'foreign_keys', 'table_partitioning', 'table_indexes', 
            'table_keys', 'columns', 'tables', 'sequences', 
            'owners', 'domains', 'stereotypes', 'project_settings', 'project_info'
        ]
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
    
    def _save_project_data(self, cursor: sqlite3.Cursor):
        """Save project data to the database."""
        # Save project info
        cursor.execute('''
            INSERT INTO project_info (name, description)
            VALUES (?, ?)
        ''', (self.current_project.name, self.current_project.description))
        
        # Save project settings
        settings = self.current_project.settings
        cursor.execute('''
            INSERT INTO project_settings (author, template_directory, output_directory, theme)
            VALUES (?, ?, ?, ?)
        ''', (settings.get('author', ''),
              settings.get('template_directory', ''),
              settings.get('output_directory', ''),
              settings.get('theme', 'system')))

        # Save domains
        for domain in self.current_project.domains:
            cursor.execute('''
                INSERT INTO domains (name, data_type, comment)
                VALUES (?, ?, ?)
            ''', (domain.name, domain.data_type, domain.comment))
        
        # Save owners
        for owner in self.current_project.owners:
            cursor.execute('''
                INSERT INTO owners (name, default_tablespace, temp_tablespace,
                                  default_index_tablespace, editionable, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (owner.name, owner.default_tablespace, owner.temp_tablespace,
                  owner.default_index_tablespace, owner.editionable, owner.comment))
        
        # Save stereotypes
        for stereotype in self.current_project.stereotypes:
            cursor.execute('''
                INSERT INTO stereotypes (name, stereotype_type, description, background_color)
                VALUES (?, ?, ?, ?)
            ''', (stereotype.name, stereotype.stereotype_type.value, stereotype.description, stereotype.background_color))
        
        # Save tables
        for table in self.current_project.tables:
            cursor.execute('''
                INSERT INTO tables (name, owner, tablespace, stereotype, color,
                                  domain, editionable, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (table.name, table.owner, table.tablespace, table.stereotype,
                  table.color, table.domain, table.editionable, table.comment))
            
            table_id = cursor.lastrowid
            
            # Save columns
            for i, column in enumerate(table.columns):
                cursor.execute('''
                    INSERT INTO columns (table_id, name, data_type, nullable,
                                       default_value, comment, domain, stereotype, column_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (table_id, column.name, column.data_type, column.nullable,
                      column.default, column.comment, column.domain, column.stereotype, i))
            
            # Save keys
            for key in table.keys:
                cursor.execute('''
                    INSERT INTO table_keys (table_id, name, columns)
                    VALUES (?, ?, ?)
                ''', (table_id, key.name, json.dumps(key.columns)))
            
            # Save indexes
            for index in table.indexes:
                cursor.execute('''
                    INSERT INTO table_indexes (table_id, name, columns, tablespace)
                    VALUES (?, ?, ?, ?)
                ''', (table_id, index.name, json.dumps(index.columns), index.tablespace))
            
            # Save partitioning
            if table.partitioning:
                cursor.execute('''
                    INSERT INTO table_partitioning (table_id, columns, partition_type)
                    VALUES (?, ?, ?)
                ''', (table_id, json.dumps(table.partitioning.columns),
                      table.partitioning.partition_type.value))
        
        # Save sequences
        for sequence in self.current_project.sequences:
            cursor.execute('''
                INSERT INTO sequences (name, owner, start_with, increment_by,
                                     min_value, max_value, cache_size, cycle, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sequence.name, sequence.owner, sequence.start_with, sequence.increment_by,
                  sequence.min_value, sequence.max_value, sequence.cache_size,
                  sequence.cycle, sequence.comment))
        
        # Save foreign keys
        for fk_key, fk_value in self.current_project.foreign_keys.items():
            source_parts = fk_key.split('.')
            if len(source_parts) >= 2:
                source_table = '.'.join(source_parts[:-1])
                source_column = source_parts[-1]
                
                cursor.execute('''
                    INSERT INTO foreign_keys (source_table, source_column,
                                            target_table, target_column)
                    VALUES (?, ?, ?, ?)
                ''', (source_table, source_column,
                      fk_value['target_table'], fk_value['target_column']))
        
        # Save diagrams
        for diagram in self.current_project.diagrams:
            cursor.execute('''
                INSERT INTO diagrams (name, description, is_active, zoom_level,
                                    scroll_x, scroll_y)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (diagram.name, diagram.description, diagram.is_active,
                  diagram.zoom_level, diagram.scroll_x, diagram.scroll_y))
            
            # Save diagram items
            for item in diagram.items:
                cursor.execute('''
                    INSERT INTO diagram_items (diagram_name, object_type, object_name,
                                             x, y, width, height)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (diagram.name, item.object_type, item.object_name,
                      item.x, item.y, item.width, item.height))
            
            # Save diagram connections
            for conn in diagram.connections:
                cursor.execute('''
                    INSERT INTO diagram_connections (diagram_name, source_table, target_table,
                                                   connection_type, label)
                    VALUES (?, ?, ?, ?, ?)
                ''', (diagram.name, conn.source_table, conn.target_table,
                      conn.connection_type, conn.label))
        
        # Save last active diagram
        if self.current_project.last_active_diagram:
            cursor.execute('''
                UPDATE project_info SET description = ?
                WHERE id = (SELECT MAX(id) FROM project_info)
            ''', (json.dumps({
                'description': self.current_project.description,
                'last_active_diagram': self.current_project.last_active_diagram
            }),))
    
    def _load_project_data(self, cursor: sqlite3.Cursor) -> Optional[Project]:
        """Load project data from the database."""
        # Load project info
        cursor.execute('SELECT name, description FROM project_info LIMIT 1')
        project_row = cursor.fetchone()
        
        if not project_row:
            return None
        
        project = Project(project_row[0], project_row[1], init_default_stereotypes=False)
        
        # Load project settings
        cursor.execute('SELECT author, template_directory, output_directory, theme FROM project_settings LIMIT 1')
        settings_row = cursor.fetchone()
        if settings_row:
            project.settings = {
                'author': settings_row[0] or '',
                'template_directory': settings_row[1] or '',
                'output_directory': settings_row[2] or '',
                'theme': settings_row[3] or 'system'
            }

        # Load domains
        cursor.execute('SELECT name, data_type, comment FROM domains')
        for row in cursor.fetchall():
            from ..models import Domain
            domain = Domain(row[0], row[1], row[2])
            project.add_domain(domain)
        
        # Load owners
        cursor.execute('''
            SELECT name, default_tablespace, temp_tablespace,
                   default_index_tablespace, editionable, comment
            FROM owners
        ''')
        for row in cursor.fetchall():
            from ..models import Owner
            owner = Owner(row[0], row[1], row[2], row[3], bool(row[4]), row[5])
            project.add_owner(owner)
        
        # Load stereotypes
        cursor.execute('''
            SELECT name, stereotype_type, description, background_color
            FROM stereotypes
        ''')
        for row in cursor.fetchall():
            from ..models.base import Stereotype, StereotypeType
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
            from ..models import Table
            table = Table(
                name=row[1],
                owner=row[2],
                tablespace=row[3],
                stereotype=row[4],  # Now a string, not a Stereotype object
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
                from ..models import Column
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
                from ..models import Key
                key = Key(key_row[0], json.loads(key_row[1]))
                table.add_key(key)
            
            # Load indexes
            cursor.execute('''
                SELECT name, columns, tablespace FROM table_indexes WHERE table_id = ?
            ''', (table_id,))
            
            for idx_row in cursor.fetchall():
                from ..models import Index
                index = Index(idx_row[0], json.loads(idx_row[1]), idx_row[2])
                table.add_index(index)
            
            # Load partitioning
            cursor.execute('''
                SELECT columns, partition_type FROM table_partitioning WHERE table_id = ?
            ''', (table_id,))
            
            part_row = cursor.fetchone()
            if part_row:
                from ..models import Partitioning, PartitionType
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
            from ..models import Sequence
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
            from ..models import Diagram
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
                    item_row[0],  # object_type
                    item_row[1],  # object_name
                    item_row[2],  # x
                    item_row[3],  # y
                    item_row[4],  # width
                    item_row[5]   # height
                )
            
            # Load diagram connections
            cursor.execute('''
                SELECT source_table, target_table, connection_type, label
                FROM diagram_connections
                WHERE diagram_name = ?
            ''', (diagram.name,))
            
            for conn_row in cursor.fetchall():
                diagram.add_connection(
                    conn_row[0],  # source_table
                    conn_row[1],  # target_table
                    conn_row[2],  # connection_type
                    conn_row[3]   # label
                )
            
            project.add_diagram(diagram)
        
        # Load last active diagram from project info description (if stored as JSON)
        cursor.execute('SELECT description FROM project_info LIMIT 1')
        desc_row = cursor.fetchone()
        if desc_row and desc_row[0]:
            try:
                desc_data = json.loads(desc_row[0])
                if isinstance(desc_data, dict) and 'last_active_diagram' in desc_data:
                    project.last_active_diagram = desc_data['last_active_diagram']
                    project.description = desc_data.get('description', '')
            except (json.JSONDecodeError, TypeError):
                # If it's not JSON, it's just a plain description
                project.description = desc_row[0]
        
        return project

    def _project_to_dict(self, project: Project) -> dict:
        """Convert a Project object to a dictionary for JSON serialization."""
        return {
            "name": project.name,
            "description": project.description,
            "last_active_diagram": project.last_active_diagram,
            "settings": project.settings,
            "domains": [
                {
                    "name": domain.name,
                    "data_type": domain.data_type,
                    "comment": domain.comment
                }
                for domain in project.domains
            ],
            "owners": [
                {
                    "name": owner.name,
                    "default_tablespace": owner.default_tablespace,
                    "temp_tablespace": owner.temp_tablespace,
                    "default_index_tablespace": owner.default_index_tablespace,
                    "editionable": owner.editionable,
                    "comment": owner.comment
                }
                for owner in project.owners
            ],
            "stereotypes": [
                {
                    "name": stereotype.name,
                    "stereotype_type": stereotype.stereotype_type.value,
                    "description": stereotype.description,
                    "background_color": stereotype.background_color
                }
                for stereotype in project.stereotypes
            ],
            "tables": [
                {
                    "name": table.name,
                    "owner": table.owner,
                    "tablespace": table.tablespace,
                    "stereotype": table.stereotype,
                    "color": table.color,
                    "domain": table.domain,
                    "editionable": table.editionable,
                    "comment": table.comment,
                    "columns": [
                        {
                            "name": col.name,
                            "data_type": col.data_type,
                            "nullable": col.nullable,
                            "default": col.default,
                            "comment": col.comment,
                            "domain": col.domain,
                            "stereotype": col.stereotype
                        }
                        for col in table.columns
                    ],
                    "keys": [
                        {
                            "name": key.name,
                            "columns": key.columns
                        }
                        for key in table.keys
                    ],
                    "indexes": [
                        {
                            "name": index.name,
                            "columns": index.columns,
                            "tablespace": index.tablespace
                        }
                        for index in table.indexes
                    ],
                    "partitioning": {
                        "columns": table.partitioning.columns,
                        "partition_type": table.partitioning.partition_type.value
                    } if table.partitioning else None
                }
                for table in project.tables
            ],
            "sequences": [
                {
                    "name": seq.name,
                    "owner": seq.owner,
                    "start_with": seq.start_with,
                    "increment_by": seq.increment_by,
                    "min_value": seq.min_value,
                    "max_value": seq.max_value,
                    "cache_size": seq.cache_size,
                    "cycle": seq.cycle,
                    "comment": seq.comment
                }
                for seq in project.sequences
            ],
            "foreign_keys": [
                {
                    "source_key": fk_key,
                    "target_table": fk_value["target_table"],
                    "target_column": fk_value["target_column"]
                }
                for fk_key, fk_value in project.foreign_keys.items()
            ],
            "diagrams": [
                {
                    "name": diagram.name,
                    "description": diagram.description,
                    "is_active": diagram.is_active,
                    "zoom_level": diagram.zoom_level,
                    "scroll_x": diagram.scroll_x,
                    "scroll_y": diagram.scroll_y,
                    "items": [
                        {
                            "object_type": item.object_type,
                            "object_name": item.object_name,
                            "x": item.x,
                            "y": item.y,
                            "width": item.width,
                            "height": item.height
                        }
                        for item in diagram.items
                    ],
                    "connections": [
                        {
                            "source_table": conn.source_table,
                            "target_table": conn.target_table,
                            "connection_type": conn.connection_type,
                            "label": conn.label
                        }
                        for conn in diagram.connections
                    ]
                }
                for diagram in project.diagrams
            ]
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

            # Load settings
            if "settings" in data:
                project.settings = data["settings"]

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
