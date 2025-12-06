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


from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QVBoxLayout, 
                             QWidget, QMenu, QMessageBox, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QAction, QIcon, QDrag

from ..models import Project, Owner, Table, Sequence, Domain, Diagram


class DraggableTreeWidget(QTreeWidget):
    """Custom tree widget that supports dragging database objects."""
    
    def startDrag(self, supportedActions):
        """Start drag operation with proper mime data."""
        current_item = self.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, (Table, Sequence)):
            return  # Only allow dragging tables and sequences
        
        # Create mime data
        mime_data = QMimeData()
        if isinstance(data, Table):
            mime_data.setText(f"{data.owner}.{data.name}")
            mime_data.setData("application/x-db-table", f"{data.owner}.{data.name}".encode())
        elif isinstance(data, Sequence):
            mime_data.setText(f"{data.owner}.{data.name}")
            mime_data.setData("application/x-db-sequence", f"{data.owner}.{data.name}".encode())
        
        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        # Execute drag
        drag.exec(supportedActions)


class ObjectBrowser(QWidget):
    """Tree view widget for browsing database objects."""
    
    # Signals
    selection_changed = pyqtSignal(object)  # Emits selected object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Project = None
        self._current_owner_for_table = None
        self._current_owner_for_sequence = None
        self._filter_text = ""
        self._all_items = {}  # Cache of all items for filtering
        self._setup_ui()
        self._create_context_menus()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Create filter controls
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Type at least 3 characters to filter objects...")
        self.clear_filter_button = QPushButton("Clear Filter")
        self.clear_filter_button.setEnabled(False)  # Initially disabled
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_filter_button)
        
        layout.addLayout(filter_layout)
        
        self.tree_widget = DraggableTreeWidget()
        self.tree_widget.setHeaderLabel("Database Objects")
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # Enable drag and drop
        self.tree_widget.setDragEnabled(True)
        self.tree_widget.setDragDropMode(QTreeWidget.DragDropMode.DragOnly)
        
        layout.addWidget(self.tree_widget)
    
    def _create_context_menus(self):
        """Create context menus for different object types."""
        # Root context menu
        self.root_menu = QMenu(self)
        self.add_owner_action = QAction("Add Owner", self)
        self.add_domain_action = QAction("Add Domain", self)
        self.add_diagram_action = QAction("Add Diagram", self)
        self.root_menu.addAction(self.add_owner_action)
        self.root_menu.addAction(self.add_domain_action)
        self.root_menu.addAction(self.add_diagram_action)
        
        # Owner context menu
        self.owner_menu = QMenu(self)
        self.add_table_action = QAction("Add Table", self)
        self.add_sequence_action = QAction("Add Sequence", self)
        self.edit_owner_action = QAction("Edit Owner", self)
        self.delete_owner_action = QAction("Delete Owner", self)
        self.owner_menu.addAction(self.add_table_action)
        self.owner_menu.addAction(self.add_sequence_action)
        self.owner_menu.addSeparator()
        self.owner_menu.addAction(self.edit_owner_action)
        self.owner_menu.addAction(self.delete_owner_action)
        
        # Table context menu
        self.table_menu = QMenu(self)
        self.edit_table_action = QAction("Edit Table", self)
        self.delete_table_action = QAction("Delete Table", self)
        self.table_menu.addAction(self.edit_table_action)
        self.table_menu.addAction(self.delete_table_action)
        
        # Sequence context menu
        self.sequence_menu = QMenu(self)
        self.edit_sequence_action = QAction("Edit Sequence", self)
        self.delete_sequence_action = QAction("Delete Sequence", self)
        self.sequence_menu.addAction(self.edit_sequence_action)
        self.sequence_menu.addAction(self.delete_sequence_action)
        
        # Domain context menu
        self.domain_menu = QMenu(self)
        self.edit_domain_action = QAction("Edit Domain", self)
        self.delete_domain_action = QAction("Delete Domain", self)
        self.domain_menu.addAction(self.edit_domain_action)
        self.domain_menu.addAction(self.delete_domain_action)
        
        # Diagram context menu
        self.diagram_menu = QMenu(self)
        self.open_diagram_action = QAction("Open Diagram", self)
        self.edit_diagram_action = QAction("Edit Diagram", self)
        self.delete_diagram_action = QAction("Delete Diagram", self)
        self.diagram_menu.addAction(self.open_diagram_action)
        self.diagram_menu.addSeparator()
        self.diagram_menu.addAction(self.edit_diagram_action)
        self.diagram_menu.addAction(self.delete_diagram_action)
    
    def _connect_signals(self):
        """Connect signals."""
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Connect filter controls
        self.filter_input.textChanged.connect(self._on_filter_changed)
        self.clear_filter_button.clicked.connect(self._clear_filter)
        
        # Connect context menu actions
        self.add_owner_action.triggered.connect(self._add_owner)
        self.add_domain_action.triggered.connect(self._add_domain)
        self.add_diagram_action.triggered.connect(self._add_diagram)
        self.add_table_action.triggered.connect(self._add_table)
        self.add_sequence_action.triggered.connect(self._add_sequence)
        
        self.edit_owner_action.triggered.connect(self._edit_owner)
        self.edit_table_action.triggered.connect(self._edit_table)
        self.edit_sequence_action.triggered.connect(self._edit_sequence)
        self.edit_domain_action.triggered.connect(self._edit_domain)
        self.open_diagram_action.triggered.connect(self._open_diagram)
        self.edit_diagram_action.triggered.connect(self._edit_diagram)
        
        self.delete_owner_action.triggered.connect(self._delete_owner)
        self.delete_table_action.triggered.connect(self._delete_table)
        self.delete_sequence_action.triggered.connect(self._delete_sequence)
        self.delete_domain_action.triggered.connect(self._delete_domain)
        self.delete_diagram_action.triggered.connect(self._delete_diagram)
    
    def set_project(self, project: Project):
        """Set the current project and refresh the tree."""
        self.project = project
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh the entire tree view."""
        self.tree_widget.clear()
        self._all_items = {}  # Reset cache
        
        if not self.project:
            return
        
        # Create root items
        owners_item = QTreeWidgetItem(self.tree_widget, ["Owners"])
        domains_item = QTreeWidgetItem(self.tree_widget, ["Domains"])
        diagrams_item = QTreeWidgetItem(self.tree_widget, ["Diagrams"])
        
        # Add owners and their objects
        for owner in self.project.owners:
            owner_item = QTreeWidgetItem(owners_item, [owner.name])
            owner_item.setData(0, Qt.ItemDataRole.UserRole, owner)
            
            # Always add Tables folder (even if empty)
            tables_folder = QTreeWidgetItem(owner_item, ["Tables"])
            tables = self.project.get_tables_by_owner(owner.name)
            for table in tables:
                table_item = QTreeWidgetItem(tables_folder, [table.name])
                table_item.setData(0, Qt.ItemDataRole.UserRole, table)
                # Cache leaf items for filtering
                self._all_items[f"table_{table.owner}_{table.name}"] = table_item
            
            # Always add Sequences folder (even if empty)
            sequences_folder = QTreeWidgetItem(owner_item, ["Sequences"])
            sequences = self.project.get_sequences_by_owner(owner.name)
            for sequence in sequences:
                sequence_item = QTreeWidgetItem(sequences_folder, [sequence.name])
                sequence_item.setData(0, Qt.ItemDataRole.UserRole, sequence)
                # Cache leaf items for filtering
                self._all_items[f"sequence_{sequence.owner}_{sequence.name}"] = sequence_item
        
        # Add domains
        for domain in self.project.domains:
            domain_item = QTreeWidgetItem(domains_item, [domain.name])
            domain_item.setData(0, Qt.ItemDataRole.UserRole, domain)
            # Cache leaf items for filtering
            self._all_items[f"domain_{domain.name}"] = domain_item
        
        # Add diagrams
        for diagram in self.project.diagrams:
            diagram_item = QTreeWidgetItem(diagrams_item, [diagram.name])
            diagram_item.setData(0, Qt.ItemDataRole.UserRole, diagram)
            # Mark active diagram with a different appearance
            if diagram.is_active:
                diagram_item.setText(0, f"{diagram.name} (Active)")
            # Cache leaf items for filtering
            self._all_items[f"diagram_{diagram.name}"] = diagram_item
        
        # Apply current filter if any
        if self._filter_text and len(self._filter_text) >= 3:
            self._apply_filter()
        else:
            # Expand all items when no filter
            self.tree_widget.expandAll()
    
    def select_object(self, obj):
        """Select an object in the tree view."""
        if not obj:
            return
        
        # Find the item corresponding to this object
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            category_item = root.child(i)
            for j in range(category_item.childCount()):
                item = category_item.child(j)
                # Check direct object data
                if item.data(0, Qt.ItemDataRole.UserRole) == obj:
                    self.tree_widget.setCurrentItem(item)
                    category_item.setExpanded(True)
                    return
                
                # Check nested items (tables/sequences under owners)
                for k in range(item.childCount()):
                    sub_category = item.child(k)
                    for l in range(sub_category.childCount()):
                        sub_item = sub_category.child(l)
                        if sub_item.data(0, Qt.ItemDataRole.UserRole) == obj:
                            self.tree_widget.setCurrentItem(sub_item)
                            category_item.setExpanded(True)
                            item.setExpanded(True)
                            sub_category.setExpanded(True)
                            return
    
    def get_drag_data(self, item):
        """Get drag data for an item."""
        if not item:
            return None
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, (Table, Sequence)):
            return data
        return None
    
    def _on_selection_changed(self):
        """Handle selection change in the tree."""
        current_item = self.tree_widget.currentItem()
        if current_item:
            data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                self.selection_changed.emit(data)
            else:
                self.selection_changed.emit(None)
    
    def _on_item_double_clicked(self, item, column):
        """Handle double-click on tree items."""
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        # Route to appropriate action based on object type
        if isinstance(data, Diagram):
            self._open_diagram()
        elif isinstance(data, Table):
            self._edit_table()
        elif isinstance(data, Sequence):
            self._edit_sequence()
        elif isinstance(data, Owner):
            self._edit_owner()
        elif isinstance(data, Domain):
            self._edit_domain()
        # If it's not a recognized object type, do nothing
    
    def _show_context_menu(self, position):
        """Show context menu at the given position."""
        item = self.tree_widget.itemAt(position)
        
        if not item:
            # Right-click on empty space
            self.root_menu.exec(self.tree_widget.mapToGlobal(position))
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        item_text = item.text(0)
        
        # Handle folder items (no data attached)
        if data is None:
            if item_text == "Owners":
                # Create menu for Owners folder
                owners_folder_menu = QMenu(self)
                owners_folder_menu.addAction(self.add_owner_action)
                owners_folder_menu.exec(self.tree_widget.mapToGlobal(position))
            elif item_text == "Domains":
                # Create menu for Domains folder
                domains_folder_menu = QMenu(self)
                domains_folder_menu.addAction(self.add_domain_action)
                domains_folder_menu.exec(self.tree_widget.mapToGlobal(position))
            elif item_text == "Diagrams":
                # Create menu for Diagrams folder
                diagrams_folder_menu = QMenu(self)
                diagrams_folder_menu.addAction(self.add_diagram_action)
                diagrams_folder_menu.exec(self.tree_widget.mapToGlobal(position))
            elif item_text == "Tables":
                # Create menu for Tables folder under an owner
                tables_folder_menu = QMenu(self)
                tables_folder_menu.addAction(self.add_table_action)
                # Store the owner for table creation
                owner_item = item.parent()
                if owner_item:
                    self._current_owner_for_table = owner_item.data(0, Qt.ItemDataRole.UserRole)
                tables_folder_menu.exec(self.tree_widget.mapToGlobal(position))
            elif item_text == "Sequences":
                # Create menu for Sequences folder under an owner
                sequences_folder_menu = QMenu(self)
                sequences_folder_menu.addAction(self.add_sequence_action)
                # Store the owner for sequence creation
                owner_item = item.parent()
                if owner_item:
                    self._current_owner_for_sequence = owner_item.data(0, Qt.ItemDataRole.UserRole)
                sequences_folder_menu.exec(self.tree_widget.mapToGlobal(position))
            return
        
        # Handle object items (with data attached)
        if isinstance(data, Owner):
            self.owner_menu.exec(self.tree_widget.mapToGlobal(position))
        elif isinstance(data, Table):
            self.table_menu.exec(self.tree_widget.mapToGlobal(position))
        elif isinstance(data, Sequence):
            self.sequence_menu.exec(self.tree_widget.mapToGlobal(position))
        elif isinstance(data, Domain):
            self.domain_menu.exec(self.tree_widget.mapToGlobal(position))
        elif isinstance(data, Diagram):
            self.diagram_menu.exec(self.tree_widget.mapToGlobal(position))
    
    # Context menu action handlers
    def _add_owner(self):
        """Add a new owner."""
        from ..dialogs import OwnerDialog
        dialog = OwnerDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            owner = dialog.get_owner()
            self.project.add_owner(owner)
            self._refresh_tree()
    
    def _add_domain(self):
        """Add a new domain."""
        from ..dialogs import DomainDialog
        dialog = DomainDialog(parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            domain = dialog.get_domain()
            self.project.add_domain(domain)
            self._refresh_tree()
    
    def _add_table(self):
        """Add a new table to the selected owner."""
        from ..dialogs import TableDialog
        
        # If we have a specific owner from context menu, pre-select it
        selected_owner = None
        if self._current_owner_for_table:
            selected_owner = self._current_owner_for_table.name
            self._current_owner_for_table = None  # Reset after use
        
        dialog = TableDialog(owners=self.project.owners, selected_owner=selected_owner, 
                             project=self.project, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            table = dialog.get_table()
            self.project.add_table(table)
            self._refresh_tree()
    
    def _add_sequence(self):
        """Add a new sequence to the selected owner."""
        from ..dialogs import SequenceDialog
        
        # If we have a specific owner from context menu, pre-select it
        selected_owner = None
        if self._current_owner_for_sequence:
            selected_owner = self._current_owner_for_sequence.name
            self._current_owner_for_sequence = None  # Reset after use
        
        dialog = SequenceDialog(owners=self.project.owners, selected_owner=selected_owner, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            sequence = dialog.get_sequence()
            self.project.add_sequence(sequence)
            self._refresh_tree()
    
    def _edit_owner(self):
        """Edit the selected owner."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Owner):
            return
        
        from ..dialogs import OwnerDialog
        dialog = OwnerDialog(owner=data, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._refresh_tree()
    
    def _edit_table(self):
        """Edit the selected table."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Table):
            return
        
        from ..dialogs import TableDialog
        dialog = TableDialog(table=data, owners=self.project.owners, project=self.project, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._refresh_tree()
    
    def _edit_sequence(self):
        """Edit the selected sequence."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Sequence):
            return
        
        from ..dialogs import SequenceDialog
        dialog = SequenceDialog(sequence=data, owners=self.project.owners, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._refresh_tree()
    
    def _edit_domain(self):
        """Edit the selected domain."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Domain):
            return
        
        from ..dialogs import DomainDialog
        dialog = DomainDialog(domain=data, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._refresh_tree()
    
    def _delete_owner(self):
        """Delete the selected owner."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Owner):
            return
        
        reply = QMessageBox.question(
            self, "Delete Owner",
            f"Are you sure you want to delete owner '{data.name}' and all its objects?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project.remove_owner(data.name)
            self._refresh_tree()
    
    def _delete_table(self):
        """Delete the selected table."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Table):
            return
        
        reply = QMessageBox.question(
            self, "Delete Table",
            f"Are you sure you want to delete table '{data.full_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project.remove_table(data.name, data.owner)
            self._refresh_tree()
    
    def _delete_sequence(self):
        """Delete the selected sequence."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Sequence):
            return
        
        reply = QMessageBox.question(
            self, "Delete Sequence",
            f"Are you sure you want to delete sequence '{data.owner}.{data.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project.remove_sequence(data.name, data.owner)
            self._refresh_tree()
    
    def _delete_domain(self):
        """Delete the selected domain."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Domain):
            return
        
        reply = QMessageBox.question(
            self, "Delete Domain",
            f"Are you sure you want to delete domain '{data.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project.remove_domain(data.name)
            self._refresh_tree()
    
    def _add_diagram(self):
        """Add a new diagram."""
        from ..dialogs import DiagramDialog
        existing_names = [diagram.name for diagram in self.project.diagrams]
        dialog = DiagramDialog(existing_names=existing_names, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            diagram = dialog.create_diagram()
            self.project.add_diagram(diagram)
            self._refresh_tree()
    
    def _open_diagram(self):
        """Open the selected diagram."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Diagram):
            return
        
        # Find the main window by looking for the MainWindow class
        widget = self
        while widget and widget.__class__.__name__ != 'MainWindow':
            widget = widget.parent()
        
        if widget:
            widget._open_diagram(data)
    
    def _edit_diagram(self):
        """Edit the selected diagram."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Diagram):
            return
        
        from ..dialogs import DiagramDialog
        existing_names = [diagram.name for diagram in self.project.diagrams if diagram != data]
        dialog = DiagramDialog(diagram=data, existing_names=existing_names, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            dialog.update_diagram()
            self._refresh_tree()
    
    def _delete_diagram(self):
        """Delete the selected diagram."""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, Diagram):
            return
        
        reply = QMessageBox.question(
            self, "Delete Diagram",
            f"Are you sure you want to delete diagram '{data.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project.remove_diagram(data.name)
            self._refresh_tree()
    
    # Filter methods
    def _on_filter_changed(self, text):
        """Handle filter text changes."""
        self._filter_text = text.strip()
        
        # Enable/disable clear button based on filter text
        self.clear_filter_button.setEnabled(bool(self._filter_text))
        
        if len(self._filter_text) >= 3:
            self._apply_filter()
        else:
            self._clear_filter_display()
    
    def _clear_filter(self):
        """Clear the filter text and show all items."""
        self.filter_input.clear()
        self._filter_text = ""
        self.clear_filter_button.setEnabled(False)
        self._clear_filter_display()
    
    def _apply_filter(self):
        """Apply the current filter to show/hide items."""
        if not self._filter_text or len(self._filter_text) < 3:
            return
        
        filter_lower = self._filter_text.lower()
        
        # First, hide all leaf items
        for item in self._all_items.values():
            item.setHidden(True)
        
        # Show matching leaf items
        for key, item in self._all_items.items():
            item_name = item.text(0).lower()
            # Remove "(Active)" suffix for diagrams when filtering
            if "(Active)" in item_name:
                item_name = item_name.replace(" (active)", "")
            
            if filter_lower in item_name:
                item.setHidden(False)
                # Show parent folders up to the root
                self._show_parent_hierarchy(item)
        
        # Expand all visible items to show matches
        self.tree_widget.expandAll()
    
    def _clear_filter_display(self):
        """Clear filter display and show all items."""
        # Show all items
        for item in self._all_items.values():
            item.setHidden(False)
        
        # Expand all items
        self.tree_widget.expandAll()
    
    def _show_parent_hierarchy(self, item):
        """Show all parent items up to the root for the given item."""
        parent = item.parent()
        while parent:
            parent.setHidden(False)
            parent = parent.parent()