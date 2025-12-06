"""
Domain model for database data types.
"""

from typing import Optional
from .base import DatabaseObject


class Domain(DatabaseObject):
    """Domain definition for used data types."""
    
    def __init__(self, name: str, data_type: str, comment: Optional[str] = None, guid: Optional[str] = None):
        super().__init__(name, comment, guid)
        self.data_type = data_type
    
    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'data_type': self.data_type,
            'comment': self.comment
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            data_type=data['data_type'],
            comment=data.get('comment'),
            guid=data.get('guid')
        )
    
    def __str__(self) -> str:
        return f"Domain({self.name}: {self.data_type})"
    
    def __repr__(self) -> str:
        return f"Domain(name='{self.name}', data_type='{self.data_type}', comment='{self.comment}')"