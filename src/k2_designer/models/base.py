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


from enum import Enum
from typing import Optional, List
from abc import ABC, abstractmethod
import uuid


class StereotypeType(Enum):
    """Stereotype types."""
    TABLE = "table"
    COLUMN = "column"


class Stereotype:
    """Custom stereotype definition."""
    
    def __init__(self, name: str, stereotype_type: StereotypeType, 
                 description: Optional[str] = None, background_color: Optional[str] = None, guid: Optional[str] = None):
        self.name = name
        self.stereotype_type = stereotype_type
        self.description = description
        self.background_color = background_color or self._get_default_color()
        self.guid = guid or str(uuid.uuid4())

    def _get_default_color(self) -> str:
        """Get default color for stereotype type."""
        if self.stereotype_type == StereotypeType.TABLE:
            return "#4C4C4C"
        else:  # COLUMN
            return "#808080"
    
    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'stereotype_type': self.stereotype_type.value,
            'description': self.description,
            'background_color': self.background_color
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            stereotype_type=StereotypeType(data['stereotype_type']),
            description=data.get('description'),
            background_color=data.get('background_color'),
            guid=data.get('guid')
        )


# Legacy enum for backward compatibility - will be replaced by custom stereotypes
class LegacyStereotype(Enum):
    """Legacy table stereotypes."""
    BUSINESS = "business"
    TECHNICAL = "technical"


class PartitionType(Enum):
    """Partition types."""
    RANGE = "range"
    LIST = "list"


class DatabaseObject(ABC):
    """Base class for all database objects."""
    
    def __init__(self, name: str, comment: Optional[str] = None, guid: Optional[str] = None):
        self.name = name
        self.comment = comment
        self.guid = guid or str(uuid.uuid4())

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize object to dictionary."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Deserialize object from dictionary."""
        pass


class Column:
    """Database column definition."""
    
    def __init__(self, name: str, data_type: str, nullable: bool = True, 
                 comment: Optional[str] = None, default: Optional[str] = None,
                 domain: Optional[str] = None, stereotype: Optional[str] = None, guid: Optional[str] = None):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.comment = comment
        self.default = default
        self.domain = domain
        self.stereotype = stereotype  # Reference to stereotype name
        self.guid = guid or str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'data_type': self.data_type,
            'nullable': self.nullable,
            'comment': self.comment,
            'default': self.default,
            'domain': self.domain,
            'stereotype': self.stereotype
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            data_type=data['data_type'],
            nullable=data.get('nullable', True),
            comment=data.get('comment'),
            default=data.get('default'),
            domain=data.get('domain'),
            stereotype=data.get('stereotype'),
            guid=data.get('guid')
        )


class Key:
    """Database key definition."""
    
    # Key types
    PRIMARY = "PRIMARY"
    FOREIGN = "FOREIGN"
    UNIQUE = "UNIQUE"

    def __init__(self, name: str, columns: List[str], key_type: str = UNIQUE,
                 referenced_table: Optional[str] = None, referenced_columns: Optional[List[str]] = None,
                 on_delete: Optional[str] = None, on_update: Optional[str] = None,
                 associated_index_guid: Optional[str] = None,
                 guid: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.key_type = key_type  # PRIMARY, FOREIGN, or UNIQUE
        # Foreign key specific attributes
        self.referenced_table = referenced_table
        self.referenced_columns = referenced_columns or []
        self.on_delete = on_delete  # CASCADE, SET NULL, NO ACTION, etc.
        self.on_update = on_update  # CASCADE, SET NULL, NO ACTION, etc.
        self.associated_index_guid = associated_index_guid  # GUID of associated index
        self.guid = guid or str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'columns': self.columns,
            'key_type': self.key_type,
            'referenced_table': self.referenced_table,
            'referenced_columns': self.referenced_columns,
            'on_delete': self.on_delete,
            'on_update': self.on_update,
            'associated_index_guid': self.associated_index_guid
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            columns=data['columns'],
            key_type=data.get('key_type', cls.UNIQUE),
            referenced_table=data.get('referenced_table'),
            referenced_columns=data.get('referenced_columns', []),
            on_delete=data.get('on_delete'),
            on_update=data.get('on_update'),
            associated_index_guid=data.get('associated_index_guid'),
            guid=data.get('guid')
        )


class Index:
    """Database index definition."""
    
    def __init__(self, name: str, columns: List[str], tablespace: Optional[str] = None, guid: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.tablespace = tablespace
        self.guid = guid or str(uuid.uuid4())

    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'columns': self.columns,
            'tablespace': self.tablespace
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            columns=data['columns'],
            tablespace=data.get('tablespace'),
            guid=data.get('guid')
        )


class Partitioning:
    """Database partitioning definition."""
    
    def __init__(self, columns: List[str], partition_type: PartitionType):
        self.columns = columns
        self.partition_type = partition_type
    
    def to_dict(self) -> dict:
        return {
            'columns': self.columns,
            'partition_type': self.partition_type.value
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            columns=data['columns'],
            partition_type=PartitionType(data['partition_type'])
        )