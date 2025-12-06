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


from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
                             QGraphicsPolygonItem, QMenu, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSize, pyqtSignal
from PyQt6.QtGui import (QPen, QBrush, QColor, QFont, QPainter, QTransform, 
                         QPalette, QPolygonF)
import math

from ..models import Project, Table, Column, Sequence, Diagram


class TableGraphicsItem(QGraphicsRectItem):
    """Graphics item representing a database table."""
    
    def __init__(self, table: Table, project=None, parent=None):
        super().__init__(parent)
        self.table = table
        self.project = project
        self._setup_appearance()
        self._create_content()
    
    def _setup_appearance(self):
        """Setup the visual appearance of the table."""
        # Set colors
        color = QColor(self.table.color)
        self.setBrush(QBrush(color))
        self._update_selection_appearance()
        
        # Make it movable and selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
    
    def _get_project(self):
        """Get the project reference, either from constructor or scene."""
        if self.project:
            return self.project
        scene = self.scene()
        if hasattr(scene, 'project'):
            return scene.project
        return None
    
    def _update_selection_appearance(self):
        """Update the visual appearance based on selection state."""
        # Check if we're in dark mode for better contrast
        is_dark = self._is_dark_mode()
        
        if self.isSelected():
            # Selected: thicker blue border (same in both modes)
            self.setPen(QPen(QColor("#2196F3"), 3))  # Material Blue
        else:
            # Not selected: adapt border color to theme
            if is_dark:
                # Dark mode: light gray border for visibility
                self.setPen(QPen(QColor("#cccccc"), 1))
            else:
                # Light mode: dark border
                self.setPen(QPen(QColor("#333333"), 1))
    
    def _is_dark_mode(self):
        """Check if the system is in dark mode."""
        app = QApplication.instance()
        if app is None:
            return False
        
        palette = app.palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        text_color = palette.color(QPalette.ColorRole.WindowText)
        
        window_brightness = (window_color.red() * 0.299 + 
                           window_color.green() * 0.587 + 
                           window_color.blue() * 0.114)
        text_brightness = (text_color.red() * 0.299 + 
                         text_color.green() * 0.587 + 
                         text_color.blue() * 0.114)
        
        return window_brightness < text_brightness
    
    def itemChange(self, change, value):
        """Handle item changes, particularly selection changes."""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            # Update appearance when selection changes
            self._update_selection_appearance()
        elif change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update connected lines when position changes
            self._update_connections()
        return super().itemChange(change, value)
    
    def _update_connections(self):
        """Update all connections involving this table."""
        scene = self.scene()
        if scene and hasattr(scene, 'connection_items'):
            for connection in scene.connection_items:
                if connection.source_table == self or connection.target_table == self:
                    connection._update_line()
    
    def _create_content(self):
        """Create the content of the table (title and columns)."""
        # Clear existing child items
        for child in list(self.childItems()):
            if child.scene():
                child.scene().removeItem(child)
            else:
                child.setParentItem(None)
        
        y_offset = 5
        project = self._get_project()
        
        # Table stereotype (if any)
        if self.table.stereotype and project:
            stereotype_text = QGraphicsTextItem(f"<<{self.table.stereotype}>>", self)
            stereotype_font = QFont()
            stereotype_font.setItalic(True)
            stereotype_font.setPointSize(8)
            stereotype_text.setFont(stereotype_font)
            
            # Set text color based on theme (slightly dimmed)
            if self._is_dark_mode():
                stereotype_text.setDefaultTextColor(QColor("#cccccc"))  # Light gray in dark mode
            else:
                stereotype_text.setDefaultTextColor(QColor("#666666"))  # Dark gray in light mode
                
            stereotype_text.setPos(5, y_offset)
            y_offset += stereotype_text.boundingRect().height() + 2
        
        # Table title
        title_text = QGraphicsTextItem(self.table.name, self)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title_text.setFont(title_font)
        
        # Set text color based on theme
        if self._is_dark_mode():
            title_text.setDefaultTextColor(QColor("#ffffff"))  # White text in dark mode
        else:
            title_text.setDefaultTextColor(QColor("#000000"))  # Black text in light mode
            
        title_text.setPos(5, y_offset)
        
        y_offset += title_text.boundingRect().height() + 5
        
        # Add a separator line
        line_width = max(150, title_text.boundingRect().width() + 10)
        separator = QGraphicsLineItem(5, y_offset, line_width - 5, y_offset, self)
        
        # Set separator color based on theme
        if self._is_dark_mode():
            separator.setPen(QPen(QColor("#666666"), 1))  # Gray in dark mode
        else:
            separator.setPen(QPen(QColor("#333333"), 1))  # Dark gray in light mode
        
        y_offset += 10
        
        # Columns
        max_width = line_width
        column_font = QFont()
        column_font.setPointSize(9)
        
        # Determine text color based on theme
        text_color = QColor("#ffffff") if self._is_dark_mode() else QColor("#000000")
        
        for column in self.table.columns:
            # Format column text
            column_text = f"{column.name}: {column.data_type}"
            if not column.nullable:
                column_text += " NOT NULL"
            
            # Add column stereotype if it exists
            if hasattr(column, 'stereotype') and column.stereotype and project:
                column_text += f" <<{column.stereotype}>>"
            
            column_item = QGraphicsTextItem(column_text, self)
            column_item.setFont(column_font)
            column_item.setDefaultTextColor(text_color)
            column_item.setPos(10, y_offset)
            
            max_width = max(max_width, column_item.boundingRect().width() + 20)
            y_offset += column_item.boundingRect().height() + 2
        
        # Set the rectangle size
        self.setRect(0, 0, max_width, y_offset + 5)
    
    def contextMenuEvent(self, event):
        """Handle context menu events."""
        scene = self.scene()
        if not scene:
            return
        
        selected_items = [item for item in scene.selectedItems() 
                         if isinstance(item, TableGraphicsItem)]
        
        menu = QMenu()
        
        if len(selected_items) == 1:
            # Single selection context menu
            edit_action = menu.addAction("Edit Table")
            menu.addSeparator()
            create_connection_action = menu.addAction("Create Connection")
            menu.addSeparator()
            delete_action = menu.addAction("Remove from Diagram")
            
            action = menu.exec(event.screenPos())
            if action == edit_action:
                self._edit_table()
            elif action == create_connection_action:
                self._start_connection_creation()
            elif action == delete_action:
                self._remove_from_diagram()
        
        elif len(selected_items) > 1:
            # Multiple selection context menu
            count = len(selected_items)
            
            # Header showing selection count
            header_action = menu.addAction(f"{count} Tables Selected")
            header_action.setEnabled(False)
            menu.addSeparator()
            
            # Bulk operations
            align_left_action = menu.addAction("⬅️ Align Left")
            align_right_action = menu.addAction("➡️ Align Right")
            align_top_action = menu.addAction("⬆️ Align Top")
            align_bottom_action = menu.addAction("⬇️ Align Bottom")
            menu.addSeparator()
            
            distribute_h_action = menu.addAction("↔️ Distribute Horizontally")
            distribute_v_action = menu.addAction("↕️ Distribute Vertically")
            menu.addSeparator()
            
            # Bulk removal
            delete_all_action = menu.addAction(f"Remove All {count} from Diagram")
            
            action = menu.exec(event.screenPos())
            if action == align_left_action:
                self._align_selected_tables("left")
            elif action == align_right_action:
                self._align_selected_tables("right")
            elif action == align_top_action:
                self._align_selected_tables("top")
            elif action == align_bottom_action:
                self._align_selected_tables("bottom")
            elif action == distribute_h_action:
                self._distribute_selected_tables("horizontal")
            elif action == distribute_v_action:
                self._distribute_selected_tables("vertical")
            elif action == delete_all_action:
                self._remove_multiple_from_diagram(selected_items)
        
        else:
            # No selection - shouldn't happen, but fallback
            menu.addAction("No tables selected").setEnabled(False)
            menu.exec(event.screenPos())
    
    def _edit_table(self):
        """Edit the table using the table dialog."""
        # Find the main window
        scene = self.scene()
        if scene:
            view = None
            for v in scene.views():
                view = v
                break
            
            if view:
                widget = view
                while widget and widget.__class__.__name__ != 'MainWindow':
                    widget = widget.parent()
                
                if widget:
                    # Open table dialog  
                    from ..dialogs import TableDialog
                    owners = widget.current_project.owners
                    
                    dialog = TableDialog(
                        table=self.table,
                        owners=owners,
                        selected_owner=self.table.owner,
                        project=widget.current_project,
                        parent=widget
                    )
                    
                    if dialog.exec() == dialog.DialogCode.Accepted:
                        dialog.update_table()
                        # The update_table method handles main window notification
                        # which will refresh all diagrams and the object browser
    
    def _remove_from_diagram(self):
        """Remove this table from the diagram (not from project)."""
        scene = self.scene()
        if scene and hasattr(scene, 'diagram') and scene.diagram:
            # Remove from diagram model
            scene.diagram.remove_item(self.table.full_name)
            # Remove from scene
            scene.removeItem(self)
            # Remove from scene's table_items dict
            if self.table.full_name in scene.table_items:
                del scene.table_items[self.table.full_name]
    
    def _refresh_display(self):
        """Refresh the visual display of the table."""
        # Update colors and appearance
        self._setup_appearance()
        # Recreate content
        self._create_content()
        # Ensure selection appearance is correct
        self._update_selection_appearance()
    
    def _align_selected_tables(self, alignment):
        """Align multiple selected tables."""
        scene = self.scene()
        if not scene:
            return
        
        selected_items = [item for item in scene.selectedItems() 
                         if isinstance(item, TableGraphicsItem)]
        
        if len(selected_items) < 2:
            return
        
        # Get reference coordinates from the first selected item
        reference_item = selected_items[0]
        ref_pos = reference_item.pos()
        ref_rect = reference_item.boundingRect()
        
        for item in selected_items[1:]:
            current_pos = item.pos()
            
            if alignment == "left":
                item.setPos(ref_pos.x(), current_pos.y())
            elif alignment == "right":
                item.setPos(ref_pos.x() + ref_rect.width() - item.boundingRect().width(), 
                           current_pos.y())
            elif alignment == "top":
                item.setPos(current_pos.x(), ref_pos.y())
            elif alignment == "bottom":
                item.setPos(current_pos.x(), 
                           ref_pos.y() + ref_rect.height() - item.boundingRect().height())
        
        # Update diagram positions if we have one
        if scene.diagram:
            scene._update_diagram_positions()
    
    def _distribute_selected_tables(self, direction):
        """Distribute multiple selected tables evenly."""
        scene = self.scene()
        if not scene:
            return
        
        selected_items = [item for item in scene.selectedItems() 
                         if isinstance(item, TableGraphicsItem)]
        
        if len(selected_items) < 3:
            return  # Need at least 3 items to distribute
        
        # Sort items by position
        if direction == "horizontal":
            selected_items.sort(key=lambda item: item.pos().x())
            
            # Calculate spacing
            leftmost = selected_items[0].pos().x()
            rightmost = selected_items[-1].pos().x() + selected_items[-1].boundingRect().width()
            total_width = sum(item.boundingRect().width() for item in selected_items)
            spacing = (rightmost - leftmost - total_width) / (len(selected_items) - 1)
            
            # Distribute
            current_x = leftmost
            for item in selected_items:
                item.setPos(current_x, item.pos().y())
                current_x += item.boundingRect().width() + spacing
        
        else:  # vertical
            selected_items.sort(key=lambda item: item.pos().y())
            
            # Calculate spacing
            topmost = selected_items[0].pos().y()
            bottommost = selected_items[-1].pos().y() + selected_items[-1].boundingRect().height()
            total_height = sum(item.boundingRect().height() for item in selected_items)
            spacing = (bottommost - topmost - total_height) / (len(selected_items) - 1)
            
            # Distribute
            current_y = topmost
            for item in selected_items:
                item.setPos(item.pos().x(), current_y)
                current_y += item.boundingRect().height() + spacing
        
        # Update diagram positions if we have one
        if scene.diagram:
            scene._update_diagram_positions()
    
    def _remove_multiple_from_diagram(self, table_items):
        """Remove multiple tables from the diagram."""
        scene = self.scene()
        if not scene:
            return
        
        from PyQt6.QtWidgets import QMessageBox
        
        # Confirm deletion
        count = len(table_items)
        reply = QMessageBox.question(
            None, "Remove Tables",
            f"Are you sure you want to remove {count} tables from the diagram?\n"
            "(This will not delete them from the project)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in table_items:
                if hasattr(scene, 'diagram') and scene.diagram:
                    # Remove from diagram model
                    scene.diagram.remove_item(item.table.full_name)
                
                # Remove from scene
                scene.removeItem(item)
                
                # Remove from scene's table_items dict
                if item.table.full_name in scene.table_items:
                    del scene.table_items[item.table.full_name]

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events on the table item."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Select the table first
            self.setSelected(True)
            # Then open the edit dialog
            self._edit_table()
        else:
            # Let the parent handle other mouse buttons
            super().mouseDoubleClickEvent(event)

    def _start_connection_creation(self):
        """Start the connection creation mode."""
        print(f"🔴 [DEBUG] Starting connection creation from source table: {self.table.name}")
        scene = self.scene()
        if scene and hasattr(scene, 'start_connection_mode'):
            scene.start_connection_mode(self)
        else:
            print(f"🔴 [DEBUG] ERROR: No scene or start_connection_mode method available")


class ConnectionGraphicsItem(QGraphicsLineItem):
    """Graphics item representing a foreign key or manual connection."""
    
    def __init__(self, source_table: TableGraphicsItem, target_table: TableGraphicsItem,
                 source_column: str = None, target_column: str = None, parent=None):
        super().__init__(parent)
        self.source_table = source_table
        self.target_table = target_table
        self.source_column = source_column
        self.target_column = target_column
        self.is_manual = False  # Will be set to True for manual connections
        self.arrow_head = None  # Arrow head graphics item
        
        self._setup_appearance()
        self._update_line()
    
    def _setup_appearance(self):
        """Setup the visual appearance of the connection."""
        if self.is_manual or self.source_column == "manual":
            # Manual connections: solid red line
            self.setPen(QPen(QColor("#E53E3E"), 2))  # Red color
        else:
            # FK connections: blue line
            self.setPen(QPen(QColor("#3182CE"), 2))  # Blue color
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Create arrow head
        self._create_arrow_head()
    
    def _create_arrow_head(self):
        """Create an arrow head at the target end."""
        self.arrow_head = QGraphicsPolygonItem(parent=self)
        
        # Arrow head color matches line color
        if self.is_manual or self.source_column == "manual":
            color = QColor("#E53E3E")
        else:
            color = QColor("#3182CE")
        
        self.arrow_head.setPen(QPen(color, 1))
        self.arrow_head.setBrush(QBrush(color))
    
    def _update_line(self):
        """Update the line position based on table positions using shortest path between edges."""
        source_rect = self.source_table.boundingRect()
        target_rect = self.target_table.boundingRect()
        
        source_pos = self.source_table.pos()
        target_pos = self.target_table.pos()
        
        # Calculate table centers
        source_center = QPointF(
            source_pos.x() + source_rect.width() / 2,
            source_pos.y() + source_rect.height() / 2
        )
        target_center = QPointF(
            target_pos.x() + target_rect.width() / 2,
            target_pos.y() + target_rect.height() / 2
        )
        
        # Calculate potential connection points on all four sides of each table
        source_points = {
            'top': QPointF(source_center.x(), source_pos.y()),
            'bottom': QPointF(source_center.x(), source_pos.y() + source_rect.height()),
            'left': QPointF(source_pos.x(), source_center.y()),
            'right': QPointF(source_pos.x() + source_rect.width(), source_center.y())
        }
        
        target_points = {
            'top': QPointF(target_center.x(), target_pos.y()),
            'bottom': QPointF(target_center.x(), target_pos.y() + target_rect.height()),
            'left': QPointF(target_pos.x(), target_center.y()),
            'right': QPointF(target_pos.x() + target_rect.width(), target_center.y())
        }
        
        # Find the shortest connection between any two edge points
        min_distance = float('inf')
        best_source_point = None
        best_target_point = None
        
        for source_side, source_point in source_points.items():
            for target_side, target_point in target_points.items():
                # Calculate distance between points
                dx = target_point.x() - source_point.x()
                dy = target_point.y() - source_point.y()
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Prefer connections that don't cross the tables
                if self._is_valid_connection(source_side, target_side, source_center, target_center):
                    if distance < min_distance:
                        min_distance = distance
                        best_source_point = source_point
                        best_target_point = target_point
        
        # Fallback to any shortest connection if no valid one found
        if best_source_point is None:
            for source_side, source_point in source_points.items():
                for target_side, target_point in target_points.items():
                    dx = target_point.x() - source_point.x()
                    dy = target_point.y() - source_point.y()
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_source_point = source_point
                        best_target_point = target_point
        
        self.setLine(best_source_point.x(), best_source_point.y(), 
                    best_target_point.x(), best_target_point.y())
        
        # Update arrow head position and rotation
        self._update_arrow_head(best_source_point, best_target_point)
    
    def _is_valid_connection(self, source_side, target_side, source_center, target_center):
        """Check if the connection between two sides makes geometric sense."""
        # Horizontal relationship
        if source_center.x() < target_center.x():  # Target is to the right
            if source_side == 'right' and target_side == 'left':
                return True
        elif source_center.x() > target_center.x():  # Target is to the left
            if source_side == 'left' and target_side == 'right':
                return True
        
        # Vertical relationship
        if source_center.y() < target_center.y():  # Target is below
            if source_side == 'bottom' and target_side == 'top':
                return True
        elif source_center.y() > target_center.y():  # Target is above
            if source_side == 'top' and target_side == 'bottom':
                return True
        
        return False
    
    def _update_arrow_head(self, source_point, target_point):
        """Update arrow head position and rotation."""
        if not self.arrow_head:
            return
        
        # Calculate arrow direction
        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()
        length = math.sqrt(dx * dx + dy * dy)
        
        if length == 0:
            return
        
        # Normalize direction
        dx /= length
        dy /= length
        
        # Arrow head size
        arrow_length = 15
        arrow_width = 8
        
        # Calculate arrow head points
        tip = target_point
        base1 = QPointF(
            tip.x() - arrow_length * dx - arrow_width * dy,
            tip.y() - arrow_length * dy + arrow_width * dx
        )
        base2 = QPointF(
            tip.x() - arrow_length * dx + arrow_width * dy,
            tip.y() - arrow_length * dy - arrow_width * dx
        )
        
        # Create arrow polygon
        arrow_polygon = QPolygonF([tip, base1, base2])
        self.arrow_head.setPolygon(arrow_polygon)
    
    def contextMenuEvent(self, event):
        """Handle context menu for connections."""
        if self.is_manual or self.source_column == "manual":
            menu = QMenu()
            delete_action = menu.addAction("Delete Connection")
            
            action = menu.exec(event.screenPos())
            if action == delete_action:
                self._delete_connection()
    
    def _delete_connection(self):
        """Delete this manual connection."""
        scene = self.scene()
        if scene:
            # Remove from scene
            scene.removeItem(self)
            if self in scene.connection_items:
                scene.connection_items.remove(self)
            
            # Remove from diagram model
            if scene.diagram and self.is_manual:
                scene.diagram.remove_connection(
                    self.source_table.table.full_name,
                    self.target_table.table.full_name
                )


class DiagramScene(QGraphicsScene):
    """Custom graphics scene for ER diagrams."""
    
    # Signals
    table_selected = pyqtSignal(object)  # Can emit Table or None (legacy, single selection)
    tables_selected = pyqtSignal(list)    # New signal for multiple table selections
    
    def __init__(self, project: Project, diagram: Diagram = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.diagram = diagram
        self.table_items = {}  # table_name -> TableGraphicsItem
        self.connection_items = []  # List of ConnectionGraphicsItem
        
        # Connection creation state
        self.connection_mode = False
        self.connection_source = None
        self.temp_connection_line = None
        
        self._setup_scene()
        
        # Only load existing items if we have a diagram
        if self.diagram:
            self._load_diagram_items()
        else:
            self._load_tables()  # Fallback to old behavior
        
        self._load_connections()
        
        # Connect selection changes
        self.selectionChanged.connect(self._on_selection_changed)
        
        # Connect to theme changes
        app = QApplication.instance()
        if app is not None:
            app.paletteChanged.connect(self._on_theme_changed)
    
    def _on_theme_changed(self):
        """Handle system theme changes."""
        self._update_background_color()
        self._refresh_all_table_items()
    
    def _refresh_all_table_items(self):
        """Refresh all table items to update their appearance for the current theme."""
        for item in self.table_items.values():
            if isinstance(item, TableGraphicsItem):
                item._refresh_display()
    
    def refresh_all_items(self):
        """Refresh all items in the scene to reflect data changes without losing positions."""
        try:
            # Create a mapping of current table items to their positions
            table_positions = {}
            tables_to_remove = []
            
            # First pass: Update existing table items and track positions
            for item_name, table_item in list(self.table_items.items()):
                if isinstance(table_item, TableGraphicsItem):
                    # Store position for potential recreation
                    table_positions[table_item.table] = table_item.pos()
                    
                    # Check if this table still exists in the project
                    table_found = False
                    old_table_name = f"{table_item.table.owner}.{table_item.table.name}"
                    
                    for table in self.project.tables:
                        # Match by name and owner instead of object identity
                        current_table_name = f"{table.owner}.{table.name}"
                        if (current_table_name == item_name or 
                            current_table_name == old_table_name or
                            table == table_item.table):  # Try object identity as fallback
                            
                            # Update the reference and refresh
                            table_item.table = table
                            table_item._refresh_display()
                            
                            # Check if name changed - update the key
                            new_name = current_table_name
                            if new_name != item_name:
                                self.table_items[new_name] = table_item
                                del self.table_items[item_name]
                                # Update diagram item name if needed
                                if self.diagram:
                                    for diag_item in self.diagram.items:
                                        if diag_item.object_name == item_name:
                                            diag_item.object_name = new_name
                                            break
                            
                            table_found = True
                            break
                    
                    # If table no longer exists, mark for removal
                    if not table_found:
                        tables_to_remove.append((item_name, table_item))
            
            # Remove tables that no longer exist
            for item_name, table_item in tables_to_remove:
                self.removeItem(table_item)
                del self.table_items[item_name]
            
            # Second pass: Add any new tables from diagram
            if self.diagram:
                for item in self.diagram.items:
                    if item.object_type == 'table' and item.object_name not in self.table_items:
                        # Find the table in the project
                        for table in self.project.tables:
                            if f"{table.owner}.{table.name}" == item.object_name:
                                table_item = TableGraphicsItem(table, self.project)
                                table_item.setPos(item.x, item.y)
                                self.addItem(table_item)
                                self.table_items[item.object_name] = table_item
                                break
            
            # Refresh connections (they might need to be recreated if table structures changed)
            # Remove existing connections
            for connection in list(self.connection_items):
                self.removeItem(connection)
            self.connection_items.clear()
            
            # Reload connections
            self._load_connections()
            if self.diagram:
                self._load_diagram_connections()
            
        except Exception as e:
            print(f"❌ Error during diagram refresh: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to full refresh
            self.clear()
            self.table_items.clear()
            self.connection_items.clear()
            if self.diagram:
                self._load_diagram_items()
            else:
                self._load_tables()
                self._load_connections()
    
    def _load_diagram_items(self):
        """Load items from the diagram."""
        if not self.diagram:
            return
        
        for item in self.diagram.items:
            if item.object_type == 'table':
                # Find the table in the project
                for table in self.project.tables:
                    if f"{table.owner}.{table.name}" == item.object_name:
                        table_item = TableGraphicsItem(table, self.project)
                        table_item.setPos(item.x, item.y)
                        self.addItem(table_item)
                        self.table_items[item.object_name] = table_item
                        break
            elif item.object_type == 'sequence':
                # Find the sequence in the project
                for sequence in self.project.sequences:
                    if f"{sequence.owner}.{sequence.name}" == item.object_name:
                        from PyQt6.QtWidgets import QGraphicsTextItem
                        sequence_item = QGraphicsTextItem(f"SEQ: {item.object_name}")
                        sequence_item.setPos(item.x, item.y)
                        sequence_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                        sequence_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                        self.addItem(sequence_item)
                        self.table_items[item.object_name] = sequence_item
                        break
        
        # Load connections after all items are loaded
        self._load_diagram_connections()
    
    def _load_diagram_connections(self):
        """Load connections from the diagram."""
        if not self.diagram:
            return
        
        print(f"\n🔗 Loading {len(self.diagram.connections)} saved connections from diagram...")
        
        for connection in self.diagram.connections:
            source_name = connection.source_table
            target_name = connection.target_table
            
            print(f"📍 Loading connection: {source_name} -> {target_name}")
            
            # Find source and target table graphics items
            source_item = self.table_items.get(source_name)
            target_item = self.table_items.get(target_name)
            
            if source_item and target_item:
                # Create connection graphics item (manual connections don't have specific columns)
                connection_item = ConnectionGraphicsItem(source_item, target_item, None, None)
                connection_item.is_manual = True  # Mark as manual connection
                connection_item._setup_appearance()  # Refresh appearance with manual flag
                self.addItem(connection_item)
                self.connection_items.append(connection_item)
                print(f"✅ Connection created successfully")
            else:
                print(f"❌ Could not find table items for connection:")
                print(f"   Source '{source_name}': {'found' if source_item else 'NOT FOUND'}")
                print(f"   Target '{target_name}': {'found' if target_item else 'NOT FOUND'}")
                print(f"   Available tables: {list(self.table_items.keys())}")
        
        print(f"🔗 Finished loading connections. Total active: {len(self.connection_items)}")
    
    def add_table(self, table: Table, position: QPointF):
        """Add a table to the scene at the specified position."""
        table_name = table.full_name
        
        # Don't add if already exists
        if table_name in self.table_items:
            return
        
        # Create table item
        table_item = TableGraphicsItem(table, self.project)
        table_item.setPos(position)
        self.addItem(table_item)
        
        self.table_items[table_name] = table_item
        
        # Save to diagram if we have one
        if self.diagram:
            self.diagram.add_item('table', table_name, position.x(), position.y())
    
    def add_sequence(self, sequence: Sequence, position: QPointF):
        """Add a sequence to the scene at the specified position."""
        # For now, sequences will be displayed as simple text items
        # In a full implementation, you might want a dedicated SequenceGraphicsItem
        sequence_name = f"{sequence.owner}.{sequence.name}"
        
        # Don't add if already exists
        if sequence_name in self.table_items:
            return
        
        # Create a simple text item for the sequence
        from PyQt6.QtWidgets import QGraphicsTextItem
        sequence_item = QGraphicsTextItem(f"SEQ: {sequence_name}")
        sequence_item.setPos(position)
        sequence_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        sequence_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.addItem(sequence_item)
        
        self.table_items[sequence_name] = sequence_item
        
        # Save to diagram if we have one
        if self.diagram:
            self.diagram.add_item('sequence', sequence_name, position.x(), position.y())
    
    def _on_selection_changed(self):
        """Handle selection changes in the scene."""
        selected_items = self.selectedItems()
        selected_tables = []
        
        # Collect all selected table items
        for item in selected_items:
            if isinstance(item, TableGraphicsItem):
                selected_tables.append(item.table)
        
        # Emit new multi-selection signal
        self.tables_selected.emit(selected_tables)
        
        # Legacy single-selection signal for backward compatibility
        if len(selected_tables) == 1:
            self.table_selected.emit(selected_tables[0])
        elif len(selected_tables) == 0:
            self.table_selected.emit(None)
        else:
            # Multiple selections - emit None for single selection signal
            self.table_selected.emit(None)
    
    def _setup_scene(self):
        """Setup the scene properties."""
        self.setSceneRect(0, 0, 2000, 2000)
        self._update_background_color()
    
    def _update_background_color(self):
        """Update background color based on system theme."""
        if self._is_dark_mode():
            # Dark mode: use dark gray background
            self.setBackgroundBrush(QBrush(QColor("#2b2b2b")))
        else:
            # Light mode: use light background
            self.setBackgroundBrush(QBrush(QColor("#ffffff")))
    
    def _is_dark_mode(self):
        """Check if the system is in dark mode."""
        app = QApplication.instance()
        if app is None:
            return False
        
        palette = app.palette()
        # Check if the window background is darker than the window text
        window_color = palette.color(QPalette.ColorRole.Window)
        text_color = palette.color(QPalette.ColorRole.WindowText)
        
        # Calculate brightness using standard luminance formula
        window_brightness = (window_color.red() * 0.299 + 
                           window_color.green() * 0.587 + 
                           window_color.blue() * 0.114)
        text_brightness = (text_color.red() * 0.299 + 
                         text_color.green() * 0.587 + 
                         text_color.blue() * 0.114)
        
        # Dark mode when background is darker than text
        return window_brightness < text_brightness
    
    def _load_tables(self):
        """Load all tables from the project into the scene."""
        x_offset = 50
        y_offset = 50
        max_height = 0
        
        for table in self.project.tables:
            table_item = TableGraphicsItem(table, self.project)
            table_item.setPos(x_offset, y_offset)
            self.addItem(table_item)
            
            self.table_items[table.full_name] = table_item
            
            # Update position for next table
            max_height = max(max_height, table_item.boundingRect().height())
            x_offset += table_item.boundingRect().width() + 50
            
            # Wrap to next row if needed
            if x_offset > 1500:
                x_offset = 50
                y_offset += max_height + 50
                max_height = 0
    
    def _load_connections(self):
        """Load foreign key connections and manual connections."""
        # Load FK connections from project
        for fk_key, fk_value in self.project.foreign_keys.items():
            source_table_column = fk_key.split('.')
            if len(source_table_column) >= 3:
                source_table_name = '.'.join(source_table_column[:-1])
                source_column = source_table_column[-1]
                target_table_name = fk_value['target_table']
                target_column = fk_value['target_column']
                
                if (source_table_name in self.table_items and 
                    target_table_name in self.table_items):
                    
                    connection = ConnectionGraphicsItem(
                        self.table_items[source_table_name],
                        self.table_items[target_table_name],
                        source_column,
                        target_column
                    )
                    self.addItem(connection)
                    self.connection_items.append(connection)
        
        # Manual connections are loaded by _load_diagram_connections()
        # No need to duplicate the loading here
    
    def start_connection_mode(self, source_table):
        """Start connection creation mode from the specified table."""
        print(f"🟢 [DEBUG] Connection mode started with source table: {source_table.table.name}")
        
        self.connection_mode = True
        self.connection_source = source_table
        
        # Create temporary line to follow cursor
        self.temp_connection_line = QGraphicsLineItem()
        self.temp_connection_line.setPen(QPen(QColor("#E53E3E"), 2, Qt.PenStyle.DashLine))
        self.addItem(self.temp_connection_line)
        
        # Set initial line position
        source_rect = source_table.boundingRect()
        source_pos = source_table.pos()
        start_point = QPointF(
            source_pos.x() + source_rect.width(),
            source_pos.y() + source_rect.height() / 2
        )
        self.temp_connection_line.setLine(start_point.x(), start_point.y(), 
                                         start_point.x() + 50, start_point.y())
        
        # Change cursor to crosshair
        for view in self.views():
            view.setCursor(Qt.CursorShape.CrossCursor)
    
    def cancel_connection_mode(self):
        """Cancel connection creation mode."""
        print(f"🔴 [DEBUG] Canceling connection mode")
        
        if self.temp_connection_line:
            self.removeItem(self.temp_connection_line)
            self.temp_connection_line = None
            print(f"🔴 [DEBUG] Temporary connection line removed")
        
        self.connection_mode = False
        self.connection_source = None
        print(f"🔴 [DEBUG] Connection mode variables reset")
        
        # Restore normal cursor
        for view in self.views():
            view.setCursor(Qt.CursorShape.ArrowCursor)
        print(f"🔴 [DEBUG] Cursor restored to normal")
    
    def create_manual_connection(self, target_table):
        """Create a manual connection between source and target tables."""
        print(f"🟢 [DEBUG] create_manual_connection called")
        print(f"🟢 [DEBUG] Source: {self.connection_source.table.name if self.connection_source else 'None'}")
        print(f"🟢 [DEBUG] Target: {target_table.table.name if target_table else 'None'}")
        
        if not self.connection_source or not target_table:
            print(f"🟢 [DEBUG] Missing source or target - aborting")
            return
        
        # Don't connect table to itself
        if self.connection_source == target_table:
            print(f"🟢 [DEBUG] Cannot connect table to itself - canceling")
            self.cancel_connection_mode()
            return
        
        # Create manual connection (no specific columns for manual connections)
        connection = ConnectionGraphicsItem(
            self.connection_source,
            target_table,
            None,  # No specific source column for manual connections
            None   # No specific target column for manual connections
        )
        connection.is_manual = True  # Mark as manual connection
        print(f"🟢 [DEBUG] Connection object created successfully")
        
        # Update appearance after setting the flag
        connection._setup_appearance()
        print(f"🟢 [DEBUG] Connection appearance setup complete")
        
        self.addItem(connection)
        self.connection_items.append(connection)
        print(f"🟢 [DEBUG] Connection added to scene. Total connections: {len(self.connection_items)}")
        
        # Save to diagram if available
        if self.diagram:
            self.diagram.add_connection(
                self.connection_source.table.full_name,
                target_table.table.full_name,
                'manual'
            )
            print(f"🟢 [DEBUG] Connection saved to diagram model")
        else:
            print(f"🟢 [DEBUG] No diagram available - connection not persisted")
        
        # Clean up
        print(f"🟢 [DEBUG] Cleaning up connection mode...")
        self.cancel_connection_mode()

        # Refresh diagram view
        for view in self.views():
            view.viewport().update()
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if self.connection_mode:
            print(f"🔵 [DEBUG] Mouse click in connection mode: {event.button()}")
            
            # Handle connection creation
            if event.button() == Qt.MouseButton.LeftButton:
                print(f"🔵 [DEBUG] Left click detected - searching for target table...")
                
                # Find the table item under the cursor (ignore temp connection line)
                item = self.itemAt(event.scenePos(), QTransform())
                target_table = None
                
                # Skip the temporary connection line
                if item == self.temp_connection_line:
                    # Get items under cursor, excluding the temp line
                    items = self.items(event.scenePos())
                    item = None
                    for potential_item in items:
                        if potential_item != self.temp_connection_line:
                            item = potential_item
                            break
                
                print(f"🔵 [DEBUG] Item at click position: {type(item).__name__ if item else 'None'}")
                
                # Check if the clicked item is a table or part of a table
                if isinstance(item, TableGraphicsItem):
                    target_table = item
                    print(f"🔵 [DEBUG] Found target table directly: {target_table.table.name}")
                else:
                    # Check if it's a child item of a table (like text items)
                    parent = item
                    while parent and not isinstance(parent, TableGraphicsItem):
                        parent = parent.parentItem()
                    if isinstance(parent, TableGraphicsItem):
                        target_table = parent
                        print(f"🔵 [DEBUG] Found target table via parent: {target_table.table.name}")
                    else:
                        print(f"🔵 [DEBUG] No table found under click")
                
                if target_table:
                    if target_table == self.connection_source:
                        print(f"🔵 [DEBUG] Cannot connect table to itself: {target_table.table.name}")
                    else:
                        print(f"🔵 [DEBUG] Creating connection: {self.connection_source.table.name} -> {target_table.table.name}")
                    
                    # Complete the connection
                    self.create_manual_connection(target_table)
                else:
                    print(f"🔵 [DEBUG] Clicking empty space - canceling connection mode")
                    # Cancel if clicking empty space
                    self.cancel_connection_mode()
            elif event.button() == Qt.MouseButton.RightButton:
                print(f"🔵 [DEBUG] Right click - canceling connection mode")
                # Cancel connection mode on right-click
                self.cancel_connection_mode()
            
            event.accept()  # Mark event as handled
            return
        
        super().mousePressEvent(event)
        
        # Selection is now handled by the selectionChanged signal
        # This allows for proper multi-selection with Ctrl/Shift keys
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.connection_mode and self.temp_connection_line:
            # Update temporary connection line to follow cursor
            source_rect = self.connection_source.boundingRect()
            source_pos = self.connection_source.pos()
            start_point = QPointF(
                source_pos.x() + source_rect.width(),
                source_pos.y() + source_rect.height() / 2
            )
            self.temp_connection_line.setLine(start_point.x(), start_point.y(),
                                             event.scenePos().x(), event.scenePos().y())
            
            # Debug: Track what's under cursor (ignore temp connection line)
            item = self.itemAt(event.scenePos(), QTransform())
            target_table = None
            
            # Skip the temporary connection line
            if item == self.temp_connection_line:
                # Get items under cursor, excluding the temp line
                items = self.items(event.scenePos())
                item = None
                for potential_item in items:
                    if potential_item != self.temp_connection_line:
                        item = potential_item
                        break
            
            if isinstance(item, TableGraphicsItem):
                target_table = item
                print(f"🟡 [DEBUG] Cursor over table (direct): {target_table.table.name}")
            elif item:
                # Check if it's a child item of a table
                parent = item
                while parent and not isinstance(parent, TableGraphicsItem):
                    parent = parent.parentItem()
                if isinstance(parent, TableGraphicsItem):
                    target_table = parent
                    print(f"🟡 [DEBUG] Cursor over table (via child): {target_table.table.name}")
                else:
                    print(f"🟡 [DEBUG] Cursor over item: {type(item).__name__}")
            else:
                print(f"🟡 [DEBUG] Cursor over empty space")
            
            # Check if it's a valid target
            if target_table:
                is_valid = target_table != self.connection_source
                print(f"🟡 [DEBUG] Valid target: {is_valid} (source: {self.connection_source.table.name})")
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events to save position changes."""
        super().mouseReleaseEvent(event)
        
        # Update positions in diagram if we have one
        if self.diagram:
            self._update_diagram_positions()
    
    def keyPressEvent(self, event):
        """Handle key press events for selection operations."""
        from PyQt6.QtCore import Qt
        
        if event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+A: Select all table items
            self.clearSelection()
            for item in self.table_items.values():
                if isinstance(item, TableGraphicsItem):
                    item.setSelected(True)
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            # Escape: Cancel connection mode or clear selection
            if self.connection_mode:
                self.cancel_connection_mode()
            else:
                self.clearSelection()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def _update_diagram_positions(self):
        """Update positions of all items in the diagram."""
        if not self.diagram:
            return
        
        for item_name, graphics_item in self.table_items.items():
            pos = graphics_item.pos()
            self.diagram.update_item_position(item_name, pos.x(), pos.y())


class DiagramGraphicsView(QGraphicsView):
    """Custom graphics view that supports drag and drop from object browser."""
    
    # Signals
    table_dropped = pyqtSignal(object, QPointF)  # table, position
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        
        # Enable focus and keyboard events for multi-selection
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Panning state variables
        self._is_panning = False
        self._last_pan_point = None
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        # Accept drag if it contains table or sequence data
        mime_data = event.mimeData()
        if (mime_data.hasFormat("application/x-db-table") or 
            mime_data.hasFormat("application/x-db-sequence") or
            mime_data.hasText()):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move event."""
        mime_data = event.mimeData()
        if (mime_data.hasFormat("application/x-db-table") or 
            mime_data.hasFormat("application/x-db-sequence") or
            mime_data.hasText()):
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event."""
        mime_data = event.mimeData()
        
        if (mime_data.hasFormat("application/x-db-table") or 
            mime_data.hasFormat("application/x-db-sequence") or
            mime_data.hasText()):
            # Get the position in scene coordinates
            scene_pos = self.mapToScene(event.position().toPoint())
            print("Drop position in scene:", scene_pos)
            
            # Extract object information from mime data
            if mime_data.hasFormat("application/x-db-table"):
                object_info = mime_data.data("application/x-db-table").data().decode()
            elif mime_data.hasFormat("application/x-db-sequence"):
                object_info = mime_data.data("application/x-db-sequence").data().decode()
            else:
                object_info = mime_data.text()
            
            # Emit signal with drop information
            self.table_dropped.emit(object_info, scene_pos)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def mousePressEvent(self, event):
        """Handle mouse press events for canvas panning."""
        from PyQt6.QtCore import Qt
        
        # Always let the scene handle events first
        super().mousePressEvent(event)
        
        # Only handle panning if the scene didn't handle the event
        if not event.isAccepted() and event.button() == Qt.MouseButton.RightButton:
            # Check if we're clicking on empty space (not on an item)
            scene_pos = self.mapToScene(event.position().toPoint())
            item_at_pos = self.scene().itemAt(scene_pos, self.transform())
            
            if item_at_pos is None:
                # Start panning - no item under cursor
                self._is_panning = True
                self._last_pan_point = event.position().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for canvas panning."""
        if self._is_panning and self._last_pan_point is not None:
            # Calculate the movement delta
            delta = event.position().toPoint() - self._last_pan_point
            self._last_pan_point = event.position().toPoint()
            
            # Get current scroll bar values
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()
            
            # Update scroll positions (negative delta for natural scrolling feel)
            h_scroll.setValue(h_scroll.value() - delta.x())
            v_scroll.setValue(v_scroll.value() - delta.y())
            
            event.accept()
        else:
            # Let the base class handle other events
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for canvas panning."""
        from PyQt6.QtCore import Qt
        
        if event.button() == Qt.MouseButton.RightButton and self._is_panning:
            # End panning
            self._is_panning = False
            self._last_pan_point = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            # Let the base class handle other events
            super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming with Alt modifier."""
        from PyQt6.QtCore import Qt
        
        # Check if Alt/Option key is pressed
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            # Get wheel delta (positive for zoom in, negative for zoom out)
            delta = event.angleDelta().y()
            
            # Zoom factor - smaller values for more gradual zoom
            zoom_factor = 1.15
            
            if delta > 0:
                # Zoom in (scroll up with Alt)
                scale_factor = zoom_factor
            else:
                # Zoom out (scroll down with Alt)  
                scale_factor = 1.0 / zoom_factor
            
            # Get the mouse position in scene coordinates before scaling
            mouse_pos = event.position().toPoint()
            scene_pos = self.mapToScene(mouse_pos)
            
            # Apply the scaling
            self.scale(scale_factor, scale_factor)
            
            # Get the new position in scene coordinates after scaling
            new_scene_pos = self.mapToScene(mouse_pos)
            
            # Calculate the offset and adjust the view to keep mouse position stable
            delta_scene = new_scene_pos - scene_pos
            self.translate(delta_scene.x(), delta_scene.y())
            
            event.accept()
        else:
            # Let the base class handle normal scrolling
            super().wheelEvent(event)


class DiagramView(QWidget):
    """Main diagram view widget."""
    
    # Signals
    selection_changed = pyqtSignal(object)       # Single object or None (legacy)
    multiple_selection_changed = pyqtSignal(list)  # List of selected objects
    
    def __init__(self, project: Project, diagram: Diagram = None, parent=None):
        super().__init__(parent)
        self.project = project
        self.diagram = diagram
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        layout.setSpacing(2)  # Reduce spacing between toolbar and view

        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)  # Remove toolbar margins
        toolbar_layout.setSpacing(2)  # Minimal spacing between buttons

        # Get standard icons from Qt
        style = QApplication.style()
        zoom_in_icon = style.standardIcon(style.StandardPixmap.SP_ArrowUp)  # Will use text icon instead
        zoom_out_icon = style.standardIcon(style.StandardPixmap.SP_ArrowDown)  # Will use text icon instead

        # Create buttons with icons - matching table dialog style
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.setFixedSize(28, 28)
        self.zoom_in_btn.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.setFixedSize(28, 28)
        self.zoom_out_btn.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.fit_to_view_btn = QPushButton("⊡")
        self.fit_to_view_btn.setToolTip("Fit to View")
        self.fit_to_view_btn.setFixedSize(28, 28)
        self.fit_to_view_btn.setStyleSheet("font-size: 14px;")

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setToolTip("Refresh Diagram - Reload table structures")
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.setStyleSheet("font-size: 16px;")

        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.fit_to_view_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Graphics view
        self.scene = DiagramScene(self.project, self.diagram)
        self.graphics_view = DiagramGraphicsView(self.scene)
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Connect drop signal
        self.graphics_view.table_dropped.connect(self._on_table_dropped)
        
        layout.addWidget(self.graphics_view)
    
    def _connect_signals(self):
        """Connect signals."""
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        self.fit_to_view_btn.clicked.connect(self._fit_to_view)
        self.refresh_btn.clicked.connect(self._refresh_diagram)

        # Connect scene signals
        self.scene.table_selected.connect(self.selection_changed.emit)
        self.scene.tables_selected.connect(self.multiple_selection_changed.emit)
    
    def _on_table_dropped(self, object_info, position):
        """Handle when an object is dropped on the diagram."""
        # object_info is a string in format "OWNER.OBJECT_NAME"
        print(f"Object dropped: {object_info} at position {position}")
        object_full_name = object_info
        
        # Try to find a table first
        found_table = None
        for table in self.project.tables:
            if f"{table.owner}.{table.name}" == object_full_name:
                found_table = table
                break
        
        if found_table:
            # Add table to scene at the dropped position
            self.scene.add_table(found_table, position)
            return
        
        # Try to find a sequence
        found_sequence = None
        for sequence in self.project.sequences:
            if f"{sequence.owner}.{sequence.name}" == object_full_name:
                found_sequence = sequence
                break
        
        if found_sequence:
            # Add sequence to scene at the dropped position
            self.scene.add_sequence(found_sequence, position)

        # refresh diagram to show new item
        self.refresh_diagram()
    
    def _zoom_in(self):
        """Zoom in the view."""
        self.graphics_view.scale(1.2, 1.2)
    
    def _zoom_out(self):
        """Zoom out the view."""
        self.graphics_view.scale(0.8, 0.8)
    
    def _fit_to_view(self):
        """Fit all items to the view."""
        self.graphics_view.fitInView(self.scene.itemsBoundingRect(), 
                                   Qt.AspectRatioMode.KeepAspectRatio)
    
    def _refresh_diagram(self):
        """Refresh diagram button handler - reload table structures."""
        self.refresh_diagram()

    def refresh_diagram(self):
        """Refresh the entire diagram."""
        if hasattr(self, 'scene') and self.scene:
            self.scene.refresh_all_items()
        else:
            # Fallback: Clear and reload everything
            self.scene.clear()
            self.scene.table_items.clear()
            self.scene.connection_items.clear()
            self.scene._load_tables()
            self.scene._load_connections()

    def save_view_state(self):
        """Save the current view state (zoom and scroll position) to the diagram."""
        if not self.diagram:
            return

        # Get the current transformation matrix
        transform = self.graphics_view.transform()
        self.diagram.zoom_level = transform.m11()  # m11() is the horizontal scale factor

        # Get the current scroll position
        horizontal_scrollbar = self.graphics_view.horizontalScrollBar()
        vertical_scrollbar = self.graphics_view.verticalScrollBar()

        if horizontal_scrollbar:
            self.diagram.scroll_x = horizontal_scrollbar.value()
        if vertical_scrollbar:
            self.diagram.scroll_y = vertical_scrollbar.value()

    def restore_view_state(self):
        """Restore the view state (zoom and scroll position) from the diagram."""
        if not self.diagram:
            return

        # Restore zoom level
        if self.diagram.zoom_level != 1.0:
            # Reset any existing transform first
            self.graphics_view.resetTransform()
            # Apply the saved zoom level
            self.graphics_view.scale(self.diagram.zoom_level, self.diagram.zoom_level)

        # Restore scroll position (need to do this after the scene is fully loaded)
        # Use QTimer to ensure the scene is rendered before setting scroll position
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(10, self._apply_scroll_position)

    def _apply_scroll_position(self):
        """Apply the saved scroll position (called after a short delay)."""
        if not self.diagram:
            return

        horizontal_scrollbar = self.graphics_view.horizontalScrollBar()
        vertical_scrollbar = self.graphics_view.verticalScrollBar()

        if horizontal_scrollbar and self.diagram.scroll_x != 0.0:
            horizontal_scrollbar.setValue(int(self.diagram.scroll_x))
        if vertical_scrollbar and self.diagram.scroll_y != 0.0:
            vertical_scrollbar.setValue(int(self.diagram.scroll_y))
