"""
Diagram view for drawing ER diagrams.
"""

from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
                             QMenu, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QApplication)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QTransform, QPalette

from ..models import Project, Table, Column, Sequence, Diagram


class TableGraphicsItem(QGraphicsRectItem):
    """Graphics item representing a database table."""
    
    def __init__(self, table: Table, parent=None):
        super().__init__(parent)
        self.table = table
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
        return super().itemChange(change, value)
    
    def _create_content(self):
        """Create the content of the table (title and columns)."""
        # Clear existing child items
        for child in list(self.childItems()):
            if child.scene():
                child.scene().removeItem(child)
            else:
                child.setParentItem(None)
        
        y_offset = 5
        
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
            delete_action = menu.addAction("Remove from Diagram")
            
            action = menu.exec(event.screenPos())
            if action == edit_action:
                self._edit_table()
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
                        # Refresh the table display
                        self._refresh_display()
                        # Refresh object browser
                        widget.object_browser._refresh_tree()
    
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


class ConnectionGraphicsItem(QGraphicsLineItem):
    """Graphics item representing a foreign key connection."""
    
    def __init__(self, source_table: TableGraphicsItem, target_table: TableGraphicsItem,
                 source_column: str, target_column: str, parent=None):
        super().__init__(parent)
        self.source_table = source_table
        self.target_table = target_table
        self.source_column = source_column
        self.target_column = target_column
        
        self._setup_appearance()
        self._update_line()
    
    def _setup_appearance(self):
        """Setup the visual appearance of the connection."""
        self.setPen(QPen(QColor("blue"), 2))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
    
    def _update_line(self):
        """Update the line position based on table positions."""
        source_rect = self.source_table.boundingRect()
        target_rect = self.target_table.boundingRect()
        
        source_pos = self.source_table.pos()
        target_pos = self.target_table.pos()
        
        # Calculate connection points (center right of source, center left of target)
        source_point = QPointF(
            source_pos.x() + source_rect.width(),
            source_pos.y() + source_rect.height() / 2
        )
        target_point = QPointF(
            target_pos.x(),
            target_pos.y() + target_rect.height() / 2
        )
        
        self.setLine(source_point.x(), source_point.y(), 
                    target_point.x(), target_point.y())


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
    
    def _load_diagram_items(self):
        """Load items from the diagram."""
        if not self.diagram:
            return
        
        for item in self.diagram.items:
            if item.object_type == 'table':
                # Find the table in the project
                for table in self.project.tables:
                    if f"{table.owner}.{table.name}" == item.object_name:
                        table_item = TableGraphicsItem(table)
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
    
    def add_table(self, table: Table, position: QPointF):
        """Add a table to the scene at the specified position."""
        table_name = table.full_name
        
        # Don't add if already exists
        if table_name in self.table_items:
            return
        
        # Create table item
        table_item = TableGraphicsItem(table)
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
            table_item = TableGraphicsItem(table)
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
        """Load foreign key connections from the project."""
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
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        super().mousePressEvent(event)
        
        # Selection is now handled by the selectionChanged signal
        # This allows for proper multi-selection with Ctrl/Shift keys
    
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
            # Escape: Clear selection
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
        
        if event.button() == Qt.MouseButton.RightButton:
            # Check if we're clicking on empty space (not on an item)
            scene_pos = self.mapToScene(event.position().toPoint())
            item_at_pos = self.scene().itemAt(scene_pos, self.transform())
            
            if item_at_pos is None:
                # Start panning - no item under cursor
                self._is_panning = True
                self._last_pan_point = event.position().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return
        
        # Let the base class handle other events (selection, context menus on items, etc.)
        super().mousePressEvent(event)
    
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
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.fit_to_view_btn = QPushButton("Fit to View")
        
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.zoom_out_btn)
        toolbar_layout.addWidget(self.fit_to_view_btn)
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
    
    def refresh_diagram(self):
        """Refresh the entire diagram."""
        # Clear existing items
        self.scene.clear()
        self.scene.table_items.clear()
        self.scene.connection_items.clear()

        # Reload everything
        self.scene._load_tables()
        self.scene._load_connections()