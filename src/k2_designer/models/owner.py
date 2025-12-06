"""
Owner model for database schema owners/users.
"""

from typing import Optional
from .base import DatabaseObject


class Owner(DatabaseObject):
    """Database owner/user definition."""
    
    def __init__(self, name: str, default_tablespace: Optional[str] = None,
                 temp_tablespace: Optional[str] = None, 
                 default_index_tablespace: Optional[str] = None,
                 editionable: bool = False, comment: Optional[str] = None, guid: Optional[str] = None):
        super().__init__(name, comment, guid)
        self.default_tablespace = default_tablespace
        self.temp_tablespace = temp_tablespace
        self.default_index_tablespace = default_index_tablespace
        self.editionable = editionable
    
    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'default_tablespace': self.default_tablespace,
            'temp_tablespace': self.temp_tablespace,
            'default_index_tablespace': self.default_index_tablespace,
            'editionable': self.editionable,
            'comment': self.comment
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            default_tablespace=data.get('default_tablespace'),
            temp_tablespace=data.get('temp_tablespace'),
            default_index_tablespace=data.get('default_index_tablespace'),
            editionable=data.get('editionable', False),
            comment=data.get('comment'),
            guid=data.get('guid')
        )
    
    def __str__(self) -> str:
        return f"Owner({self.name})"
    
    def __repr__(self) -> str:
        return (f"Owner(name='{self.name}', default_tablespace='{self.default_tablespace}', "
                f"editionable={self.editionable})")