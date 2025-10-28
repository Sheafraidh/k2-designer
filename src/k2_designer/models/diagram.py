"""
Diagram model for ER diagrams.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DiagramItem:
    """Represents an item (table/sequence) positioned on a diagram."""
    object_type: str  # 'table' or 'sequence'
    object_name: str  # Full name (owner.name)
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None


class Diagram:
    """Represents an ER diagram."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.items: List[DiagramItem] = []
        self.is_active = False  # Track if this is the currently active diagram
        self.zoom_level = 1.0
        self.scroll_x = 0.0
        self.scroll_y = 0.0
    
    def add_item(self, object_type: str, object_name: str, x: float, y: float, 
                 width: Optional[float] = None, height: Optional[float] = None):
        """Add an item to the diagram."""
        # Remove existing item with same name if exists
        self.remove_item(object_name)
        
        item = DiagramItem(
            object_type=object_type,
            object_name=object_name,
            x=x,
            y=y,
            width=width,
            height=height
        )
        self.items.append(item)
    
    def remove_item(self, object_name: str):
        """Remove an item from the diagram."""
        self.items = [item for item in self.items if item.object_name != object_name]
    
    def get_item(self, object_name: str) -> Optional[DiagramItem]:
        """Get an item from the diagram by name."""
        for item in self.items:
            if item.object_name == object_name:
                return item
        return None
    
    def update_item_position(self, object_name: str, x: float, y: float):
        """Update the position of an item."""
        item = self.get_item(object_name)
        if item:
            item.x = x
            item.y = y
    
    def clear(self):
        """Clear all items from the diagram."""
        self.items.clear()
    
    def to_dict(self) -> dict:
        """Convert diagram to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'zoom_level': self.zoom_level,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y,
            'items': [
                {
                    'object_type': item.object_type,
                    'object_name': item.object_name,
                    'x': item.x,
                    'y': item.y,
                    'width': item.width,
                    'height': item.height
                }
                for item in self.items
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Diagram':
        """Create diagram from dictionary."""
        diagram = cls(data['name'], data.get('description', ''))
        diagram.is_active = data.get('is_active', False)
        diagram.zoom_level = data.get('zoom_level', 1.0)
        diagram.scroll_x = data.get('scroll_x', 0.0)
        diagram.scroll_y = data.get('scroll_y', 0.0)
        
        for item_data in data.get('items', []):
            diagram.add_item(
                item_data['object_type'],
                item_data['object_name'],
                item_data['x'],
                item_data['y'],
                item_data.get('width'),
                item_data.get('height')
            )
        
        return diagram
    
    @property
    def full_name(self) -> str:
        """Get the full name of the diagram."""
        return self.name