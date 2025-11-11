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
            'owners', 'domains', 'stereotypes', 'project_info'
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