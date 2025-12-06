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


from typing import Optional, List
from .base import DatabaseObject, Column, Key, Index, Partitioning, LegacyStereotype


class Table(DatabaseObject):
    """Database table definition."""
    
    def __init__(self, name: str, owner: str, tablespace: Optional[str] = None,
                 stereotype: Optional[str] = None, color: Optional[str] = None,
                 domain: Optional[str] = None, editionable: bool = False,
                 comment: Optional[str] = None, guid: Optional[str] = None):
        super().__init__(name, comment, guid)
        self.owner = owner
        self.tablespace = tablespace
        self.stereotype = stereotype  # Reference to stereotype name
        self.color = color or self._get_default_color(stereotype)
        self.domain = domain
        self.editionable = editionable
        
        # Collections
        self.columns: List[Column] = []
        self.keys: List[Key] = []
        self.indexes: List[Index] = []
        self.partitioning: Optional[Partitioning] = None
    
    def _get_default_color(self, stereotype: Optional[str]) -> str:
        """Get default color based on stereotype."""
        # Default color if no stereotype specified
        if not stereotype:
            return "#4C4C4C"
        
        # Legacy color mapping for backward compatibility
        legacy_color_map = {
            "business": "#081B2A",  # Dark blue
            "technical": "#360A3C"  # Dark purple
        }
        return legacy_color_map.get(stereotype.lower(), "#4C4C4C")
    
    def add_column(self, column: Column) -> None:
        """Add a column to the table."""
        self.columns.append(column)
    
    def remove_column(self, column_name: str) -> bool:
        """Remove a column from the table."""
        for i, column in enumerate(self.columns):
            if column.name == column_name:
                del self.columns[i]
                return True
        return False
    
    def get_column(self, column_name: str) -> Optional[Column]:
        """Get a column by name."""
        for column in self.columns:
            if column.name == column_name:
                return column
        return None
    
    def add_key(self, key: Key) -> None:
        """Add a key to the table."""
        self.keys.append(key)
    
    def remove_key(self, key_name: str) -> bool:
        """Remove a key from the table."""
        for i, key in enumerate(self.keys):
            if key.name == key_name:
                del self.keys[i]
                return True
        return False
    
    def add_index(self, index: Index) -> None:
        """Add an index to the table."""
        self.indexes.append(index)
    
    def remove_index(self, index_name: str) -> bool:
        """Remove an index from the table."""
        for i, index in enumerate(self.indexes):
            if index.name == index_name:
                del self.indexes[i]
                return True
        return False
    
    def set_partitioning(self, partitioning: Optional[Partitioning]) -> None:
        """Set table partitioning."""
        self.partitioning = partitioning
    
    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.owner}.{self.name}"
    
    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'owner': self.owner,
            'tablespace': self.tablespace,
            'stereotype': self.stereotype,
            'color': self.color,
            'domain': self.domain,
            'editionable': self.editionable,
            'comment': self.comment,
            'columns': [col.to_dict() for col in sorted(self.columns, key=lambda x: x.guid)],
            'keys': [key.to_dict() for key in sorted(self.keys, key=lambda x: x.guid)],
            'indexes': [idx.to_dict() for idx in sorted(self.indexes, key=lambda x: x.guid)],
            'partitioning': self.partitioning.to_dict() if self.partitioning else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        table = cls(
            name=data['name'],
            owner=data['owner'],
            tablespace=data.get('tablespace'),
            stereotype=data.get('stereotype'),
            color=data.get('color'),
            domain=data.get('domain'),
            editionable=data.get('editionable', False),
            comment=data.get('comment'),
            guid=data.get('guid')
        )
        
        # Load columns
        for col_data in data.get('columns', []):
            table.add_column(Column.from_dict(col_data))
        
        # Load keys
        for key_data in data.get('keys', []):
            table.add_key(Key.from_dict(key_data))
        
        # Load indexes
        for idx_data in data.get('indexes', []):
            table.add_index(Index.from_dict(idx_data))
        
        # Load partitioning
        if data.get('partitioning'):
            table.set_partitioning(Partitioning.from_dict(data['partitioning']))
        
        return table
    
    def __str__(self) -> str:
        return f"Table({self.full_name})"
    
    def __repr__(self) -> str:
        return (f"Table(name='{self.name}', owner='{self.owner}', "
                f"stereotype='{self.stereotype}', columns={len(self.columns)})")