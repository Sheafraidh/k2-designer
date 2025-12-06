"""
Diagram model for ER diagrams.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class DiagramItem:
    """Represents an item (table/sequence) positioned on a diagram."""
    object_type: str  # 'table' or 'sequence'
    object_name: str  # Full name (owner.name)
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None
    guid: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class DiagramConnection:
    """Represents a manual connection between two tables in a diagram."""
    source_table: str  # Full name of source table
    target_table: str  # Full name of target table
    connection_type: str = 'manual'  # Type of connection (manual, fk, etc.)
    label: Optional[str] = None  # Optional label for the connection
    guid: str = field(default_factory=lambda: str(uuid.uuid4()))


class Diagram:
    """Represents an ER diagram."""
    
    def __init__(self, name: str, description: str = "", guid: Optional[str] = None):
        self.name = name
        self.description = description
        self.items: List[DiagramItem] = []
        self.connections: List[DiagramConnection] = []  # Manual connections
        self.is_active = False  # Track if this is the currently active diagram
        self.zoom_level = 1.0
        self.scroll_x = 0.0
        self.scroll_y = 0.0
        self.guid = guid or str(uuid.uuid4())

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
    
    def add_connection(self, source_table: str, target_table: str, 
                      connection_type: str = 'manual', label: Optional[str] = None):
        """Add a connection between two tables."""
        # Remove existing connection if it exists
        self.remove_connection(source_table, target_table)
        
        connection = DiagramConnection(
            source_table=source_table,
            target_table=target_table,
            connection_type=connection_type,
            label=label
        )
        self.connections.append(connection)
    
    def remove_connection(self, source_table: str, target_table: str):
        """Remove a connection between two tables."""
        self.connections = [
            conn for conn in self.connections 
            if not ((conn.source_table == source_table and conn.target_table == target_table) or
                   (conn.source_table == target_table and conn.target_table == source_table))
        ]
    
    def get_connections(self) -> List[DiagramConnection]:
        """Get all connections in the diagram."""
        return self.connections.copy()
    
    def clear(self):
        """Clear all items and connections from the diagram."""
        self.items.clear()
        self.connections.clear()
    
    def to_dict(self) -> dict:
        """Convert diagram to dictionary for serialization."""
        return {
            'guid': self.guid,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'zoom_level': self.zoom_level,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y,
            'items': [
                {
                    'guid': item.guid,
                    'object_type': item.object_type,
                    'object_name': item.object_name,
                    'x': item.x,
                    'y': item.y,
                    'width': item.width,
                    'height': item.height
                }
                for item in sorted(self.items, key=lambda i: i.guid)
            ],
            'connections': [
                {
                    'guid': conn.guid,
                    'source_table': conn.source_table,
                    'target_table': conn.target_table,
                    'connection_type': conn.connection_type,
                    'label': conn.label
                }
                for conn in sorted(self.connections, key=lambda c: c.guid)
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Diagram':
        """Create diagram from dictionary."""
        diagram = cls(data['name'], data.get('description', ''), data.get('guid'))
        diagram.is_active = data.get('is_active', False)
        diagram.zoom_level = data.get('zoom_level', 1.0)
        diagram.scroll_x = data.get('scroll_x', 0.0)
        diagram.scroll_y = data.get('scroll_y', 0.0)
        
        for item_data in data.get('items', []):
            item = DiagramItem(
                object_type=item_data['object_type'],
                object_name=item_data['object_name'],
                x=item_data['x'],
                y=item_data['y'],
                width=item_data.get('width'),
                height=item_data.get('height'),
                guid=item_data.get('guid', str(uuid.uuid4()))
            )
            diagram.items.append(item)

        for conn_data in data.get('connections', []):
            conn = DiagramConnection(
                source_table=conn_data['source_table'],
                target_table=conn_data['target_table'],
                connection_type=conn_data.get('connection_type', 'manual'),
                label=conn_data.get('label'),
                guid=conn_data.get('guid', str(uuid.uuid4()))
            )
            diagram.connections.append(conn)

        return diagram
    
    @property
    def full_name(self) -> str:
        """Get the full name of the diagram."""
        return self.name