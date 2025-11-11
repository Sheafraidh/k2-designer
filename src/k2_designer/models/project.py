"""
Project model for managing the entire database design.
"""

from typing import List, Dict, Optional
from .domain import Domain
from .owner import Owner
from .table import Table
from .sequence import Sequence
from .diagram import Diagram
from .base import Stereotype


class Project:
    """Database design project containing all objects."""
    
    def __init__(self, name: str = "Untitled Project", description: Optional[str] = None, 
                 init_default_stereotypes: bool = True):
        self.name = name
        self.description = description
        self.file_path: Optional[str] = None
        
        # Collections of database objects
        self.domains: List[Domain] = []
        self.owners: List[Owner] = []
        self.tables: List[Table] = []
        self.sequences: List[Sequence] = []
        self.diagrams: List[Diagram] = []
        self.stereotypes: List[Stereotype] = []
        
        # Initialize default stereotypes only if requested
        if init_default_stereotypes:
            self._initialize_default_stereotypes()
        
        # Foreign key relationships (source_table.column -> target_table.column)
        self.foreign_keys: Dict[str, Dict[str, str]] = {}
        
        # Track last active diagram
        self.last_active_diagram: Optional[str] = None

        # Project settings
        self.settings = {
            'author': '',
            'template_directory': '',
            'output_directory': ''
        }

    def _initialize_default_stereotypes(self):
        """Initialize default stereotypes for new projects."""
        from .base import StereotypeType
        
        # Default table stereotypes
        business_table = Stereotype(
            name="Business",
            stereotype_type=StereotypeType.TABLE,
            description="Business domain table",
            background_color="#4A90E2"  # Light blue
        )
        
        technical_table = Stereotype(
            name="Technical",
            stereotype_type=StereotypeType.TABLE,
            description="Technical/system table",
            background_color="#9B59B6"  # Light purple
        )
        
        # Default column stereotypes  
        business_column = Stereotype(
            name="Business",
            stereotype_type=StereotypeType.COLUMN,
            description="Business domain column",
            background_color="#85C1E9"  # Lighter blue
        )
        
        technical_column = Stereotype(
            name="Technical",
            stereotype_type=StereotypeType.COLUMN,
            description="Technical/system column",
            background_color="#BB8FCE"  # Lighter purple
        )
        
        self.stereotypes = [business_table, technical_table, business_column, technical_column]
    
    def add_domain(self, domain: Domain) -> None:
        """Add a domain to the project."""
        self.domains.append(domain)
    
    def remove_domain(self, domain_name: str) -> bool:
        """Remove a domain from the project."""
        for i, domain in enumerate(self.domains):
            if domain.name == domain_name:
                del self.domains[i]
                return True
        return False
    
    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """Get a domain by name."""
        for domain in self.domains:
            if domain.name == domain_name:
                return domain
        return None
    
    def add_owner(self, owner: Owner) -> None:
        """Add an owner to the project."""
        self.owners.append(owner)
    
    def remove_owner(self, owner_name: str) -> bool:
        """Remove an owner and all their objects from the project."""
        # Remove owner
        owner_removed = False
        for i, owner in enumerate(self.owners):
            if owner.name == owner_name:
                del self.owners[i]
                owner_removed = True
                break
        
        if not owner_removed:
            return False
        
        # Remove all tables owned by this owner
        self.tables = [table for table in self.tables if table.owner != owner_name]
        
        # Remove all sequences owned by this owner
        self.sequences = [seq for seq in self.sequences if seq.owner != owner_name]
        
        return True
    
    def get_owner(self, owner_name: str) -> Optional[Owner]:
        """Get an owner by name."""
        for owner in self.owners:
            if owner.name == owner_name:
                return owner
        return None
    
    def add_table(self, table: Table) -> None:
        """Add a table to the project."""
        self.tables.append(table)
    
    def remove_table(self, table_name: str, owner_name: str) -> bool:
        """Remove a table from the project."""
        for i, table in enumerate(self.tables):
            if table.name == table_name and table.owner == owner_name:
                del self.tables[i]
                # Remove any foreign keys involving this table
                self._remove_foreign_keys_for_table(f"{owner_name}.{table_name}")
                return True
        return False
    
    def get_table(self, table_name: str, owner_name: str) -> Optional[Table]:
        """Get a table by name and owner."""
        for table in self.tables:
            if table.name == table_name and table.owner == owner_name:
                return table
        return None
    
    def add_sequence(self, sequence: Sequence) -> None:
        """Add a sequence to the project."""
        self.sequences.append(sequence)
    
    def remove_sequence(self, sequence_name: str, owner_name: str) -> bool:
        """Remove a sequence from the project."""
        for i, sequence in enumerate(self.sequences):
            if sequence.name == sequence_name and sequence.owner == owner_name:
                del self.sequences[i]
                return True
        return False
    
    def get_sequence(self, sequence_name: str, owner_name: str) -> Optional[Sequence]:
        """Get a sequence by name and owner."""
        for sequence in self.sequences:
            if sequence.name == sequence_name and sequence.owner == owner_name:
                return sequence
        return None
    
    def add_foreign_key(self, source_table: str, source_column: str, 
                       target_table: str, target_column: str) -> None:
        """Add a foreign key relationship."""
        key = f"{source_table}.{source_column}"
        self.foreign_keys[key] = {
            'target_table': target_table,
            'target_column': target_column
        }
    
    def remove_foreign_key(self, source_table: str, source_column: str) -> bool:
        """Remove a foreign key relationship."""
        key = f"{source_table}.{source_column}"
        if key in self.foreign_keys:
            del self.foreign_keys[key]
            return True
        return False
    
    def _remove_foreign_keys_for_table(self, table_name: str) -> None:
        """Remove all foreign keys involving a specific table."""
        keys_to_remove = []
        for key, value in self.foreign_keys.items():
            if key.startswith(f"{table_name}.") or value['target_table'] == table_name:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.foreign_keys[key]
    
    def get_tables_by_owner(self, owner_name: str) -> List[Table]:
        """Get all tables owned by a specific owner."""
        return [table for table in self.tables if table.owner == owner_name]
    
    def get_sequences_by_owner(self, owner_name: str) -> List[Sequence]:
        """Get all sequences owned by a specific owner."""
        return [seq for seq in self.sequences if seq.owner == owner_name]
    
    def add_diagram(self, diagram: Diagram) -> None:
        """Add a diagram to the project."""
        self.diagrams.append(diagram)
    
    def remove_diagram(self, diagram_name: str) -> bool:
        """Remove a diagram from the project."""
        for i, diagram in enumerate(self.diagrams):
            if diagram.name == diagram_name:
                del self.diagrams[i]
                # Clear last active diagram if this was it
                if self.last_active_diagram == diagram_name:
                    self.last_active_diagram = None
                return True
        return False
    
    def get_diagram(self, diagram_name: str) -> Optional[Diagram]:
        """Get a diagram by name."""
        for diagram in self.diagrams:
            if diagram.name == diagram_name:
                return diagram
        return None
    
    def set_active_diagram(self, diagram_name: str) -> bool:
        """Set the active diagram."""
        diagram = self.get_diagram(diagram_name)
        if diagram:
            # Clear previous active diagram
            for d in self.diagrams:
                d.is_active = False
            # Set new active diagram
            diagram.is_active = True
            self.last_active_diagram = diagram_name
            return True
        return False
    
    def get_active_diagram(self) -> Optional[Diagram]:
        """Get the currently active diagram."""
        for diagram in self.diagrams:
            if diagram.is_active:
                return diagram
        return None
    
    def add_stereotype(self, stereotype: Stereotype) -> None:
        """Add a stereotype to the project."""
        self.stereotypes.append(stereotype)
    
    def remove_stereotype(self, stereotype_name: str) -> bool:
        """Remove a stereotype from the project."""
        for i, stereotype in enumerate(self.stereotypes):
            if stereotype.name == stereotype_name:
                del self.stereotypes[i]
                return True
        return False
    
    def get_stereotype(self, stereotype_name: str) -> Optional[Stereotype]:
        """Get a stereotype by name."""
        for stereotype in self.stereotypes:
            if stereotype.name == stereotype_name:
                return stereotype
        return None
    
    def to_dict(self) -> dict:
        """Serialize project to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'domains': [domain.to_dict() for domain in self.domains],
            'owners': [owner.to_dict() for owner in self.owners],
            'tables': [table.to_dict() for table in self.tables],
            'sequences': [sequence.to_dict() for sequence in self.sequences],
            'diagrams': [diagram.to_dict() for diagram in self.diagrams],
            'stereotypes': [stereotype.to_dict() for stereotype in self.stereotypes],
            'foreign_keys': self.foreign_keys,
            'last_active_diagram': self.last_active_diagram
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize project from dictionary."""
        project = cls(
            name=data.get('name', 'Untitled Project'),
            description=data.get('description')
        )
        
        # Load domains
        for domain_data in data.get('domains', []):
            project.add_domain(Domain.from_dict(domain_data))
        
        # Load owners
        for owner_data in data.get('owners', []):
            project.add_owner(Owner.from_dict(owner_data))
        
        # Load tables
        for table_data in data.get('tables', []):
            project.add_table(Table.from_dict(table_data))
        
        # Load sequences
        for sequence_data in data.get('sequences', []):
            project.add_sequence(Sequence.from_dict(sequence_data))
        
        # Load diagrams
        for diagram_data in data.get('diagrams', []):
            project.add_diagram(Diagram.from_dict(diagram_data))
        
        # Load stereotypes
        for stereotype_data in data.get('stereotypes', []):
            project.add_stereotype(Stereotype.from_dict(stereotype_data))
        
        # Load foreign keys
        project.foreign_keys = data.get('foreign_keys', {})
        
        # Set last active diagram
        project.last_active_diagram = data.get('last_active_diagram')
        
        return project
    
    def __str__(self) -> str:
        return f"Project({self.name})"
    
    def __repr__(self) -> str:
        return (f"Project(name='{self.name}', tables={len(self.tables)}, "
                f"sequences={len(self.sequences)}, owners={len(self.owners)})")