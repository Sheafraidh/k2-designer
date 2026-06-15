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


import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator


class StereotypeType(Enum):
    """Stereotype types."""
    TABLE = "table"
    COLUMN = "column"


class Stereotype:
    """Custom stereotype definition."""

    def __init__(self, name: str, stereotype_type: StereotypeType,
                 description: str | None = None, background_color: str | None = None, guid: str | None = None):
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


class PartitionType(Enum):
    """Partition types."""
    RANGE = "range"
    LIST = "list"


class DatabaseObject(ABC):
    """Base class for all database objects."""

    def __init__(self, name: str, comment: str | None = None, guid: str | None = None):
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


class Column(BaseModel):
    """Database column definition."""

    name: str
    data_type: str
    nullable: bool = True
    comment: str | None = None
    default: str | None = None
    domain: str | None = None
    stereotype: str | None = None
    guid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator('guid', mode='before')
    @classmethod
    def _ensure_guid(cls, v):
        return v or str(uuid.uuid4())


class KeyType(str, Enum):
    """Key type — str Enum so comparisons with plain strings still work."""
    PRIMARY = "PRIMARY"
    FOREIGN = "FOREIGN"
    UNIQUE = "UNIQUE"


class Key(BaseModel):
    """Database key definition."""

    # Class-level aliases kept for backward compatibility with GUI code
    # that references Key.PRIMARY / Key.FOREIGN / Key.UNIQUE.
    PRIMARY: ClassVar[KeyType] = KeyType.PRIMARY
    FOREIGN: ClassVar[KeyType] = KeyType.FOREIGN
    UNIQUE: ClassVar[KeyType] = KeyType.UNIQUE

    name: str
    columns: list[str]
    key_type: KeyType = KeyType.UNIQUE
    referenced_table: str | None = None
    referenced_columns: list[str] = Field(default_factory=list)
    on_delete: str | None = None
    on_update: str | None = None
    associated_index_guid: str | None = None
    guid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator('guid', mode='before')
    @classmethod
    def _ensure_guid(cls, v):
        return v or str(uuid.uuid4())


class Index(BaseModel):
    """Database index definition."""

    name: str
    columns: list[str]
    tablespace: str | None = None
    guid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @field_validator('guid', mode='before')
    @classmethod
    def _ensure_guid(cls, v):
        return v or str(uuid.uuid4())


class Partitioning(BaseModel):
    """Database partitioning definition."""

    columns: list[str]
    partition_type: PartitionType
