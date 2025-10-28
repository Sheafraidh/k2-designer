"""
Base classes and enums for the DB Designer data model.
"""

from enum import Enum
from typing import Optional, List
from abc import ABC, abstractmethod


class Stereotype(Enum):
    """Table stereotypes."""
    BUSINESS = "business"
    TECHNICAL = "technical"


class PartitionType(Enum):
    """Partition types."""
    RANGE = "range"
    LIST = "list"


class DatabaseObject(ABC):
    """Base class for all database objects."""
    
    def __init__(self, name: str, comment: Optional[str] = None):
        self.name = name
        self.comment = comment
    
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
                 domain: Optional[str] = None):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.comment = comment
        self.default = default
        self.domain = domain
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'data_type': self.data_type,
            'nullable': self.nullable,
            'comment': self.comment,
            'default': self.default,
            'domain': self.domain
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            data_type=data['data_type'],
            nullable=data.get('nullable', True),
            comment=data.get('comment'),
            default=data.get('default'),
            domain=data.get('domain')
        )


class Key:
    """Database key definition."""
    
    def __init__(self, name: str, columns: List[str]):
        self.name = name
        self.columns = columns
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'columns': self.columns
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            columns=data['columns']
        )


class Index:
    """Database index definition."""
    
    def __init__(self, name: str, columns: List[str], tablespace: Optional[str] = None):
        self.name = name
        self.columns = columns
        self.tablespace = tablespace
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'columns': self.columns,
            'tablespace': self.tablespace
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            columns=data['columns'],
            tablespace=data.get('tablespace')
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