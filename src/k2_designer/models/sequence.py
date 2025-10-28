"""
Sequence model for database sequences.
"""

from typing import Optional, Dict, Any
from .base import DatabaseObject


class Sequence(DatabaseObject):
    """Database sequence definition."""
    
    def __init__(self, name: str, owner: str, start_with: int = 1, 
                 increment_by: int = 1, min_value: Optional[int] = None,
                 max_value: Optional[int] = None, cache_size: int = 20,
                 cycle: bool = False, comment: Optional[str] = None):
        super().__init__(name, comment)
        self.owner = owner
        self.start_with = start_with
        self.increment_by = increment_by
        self.min_value = min_value
        self.max_value = max_value
        self.cache_size = cache_size
        self.cycle = cycle
    
    @property
    def attributes(self) -> Dict[str, Any]:
        """Get sequence attributes as a dictionary."""
        return {
            'start_with': self.start_with,
            'increment_by': self.increment_by,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'cache_size': self.cache_size,
            'cycle': self.cycle
        }
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'owner': self.owner,
            'start_with': self.start_with,
            'increment_by': self.increment_by,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'cache_size': self.cache_size,
            'cycle': self.cycle,
            'comment': self.comment
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            owner=data['owner'],
            start_with=data.get('start_with', 1),
            increment_by=data.get('increment_by', 1),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            cache_size=data.get('cache_size', 20),
            cycle=data.get('cycle', False),
            comment=data.get('comment')
        )
    
    def __str__(self) -> str:
        return f"Sequence({self.owner}.{self.name})"
    
    def __repr__(self) -> str:
        return (f"Sequence(name='{self.name}', owner='{self.owner}', "
                f"start_with={self.start_with}, increment_by={self.increment_by})")