"""
Dialogs for the DB Designer application.
"""

from .domain_dialog import DomainDialog
from .owner_dialog import OwnerDialog
from .table_dialog import TableDialog
from .sequence_dialog import SequenceDialog
from .diagram_dialog import DiagramDialog
from .new_project_dialog import NewProjectDialog
from .generate_dialog import GenerateDialog

__all__ = ['DomainDialog', 'OwnerDialog', 'TableDialog', 'SequenceDialog', 'DiagramDialog', 'NewProjectDialog', 'GenerateDialog']