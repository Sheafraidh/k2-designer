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

from typing import List, Dict, Optional, Callable, Any
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QComboBox, QGroupBox, QHeaderView, QMessageBox,
                             QStyledItemDelegate)
from PyQt6.QtCore import Qt, pyqtSignal


class MultiSelectDelegate(QStyledItemDelegate):
    """Custom delegate that handles multi-row editing."""

    editingStarted = pyqtSignal(int, int)  # row, column

    def setEditorData(self, editor, index):
        """Override to capture when editing starts."""
        self.editingStarted.emit(index.row(), index.column())
        super().setEditorData(editor, index)


class MultiSelectTableWidget(QTableWidget):
    """Custom table widget that preserves selection during editing for multi-row updates."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._captured_selection = set()
        self._delegate = MultiSelectDelegate()
        self.setItemDelegate(self._delegate)
        self._delegate.editingStarted.connect(self._on_editing_started)

    def _on_editing_started(self, row, column):
        """Capture selection when editing starts."""
        self._captured_selection = set()
        for item in self.selectedItems():
            self._captured_selection.add(item.row())

    def get_captured_selection(self):
        """Get the selection captured when editing started."""
        return self._captured_selection


class ColumnConfig:
    """Configuration for a grid column."""

    def __init__(self, name: str, width: int = 100,
                 resize_mode: QHeaderView.ResizeMode = QHeaderView.ResizeMode.Interactive,
                 editor_type: str = "text",
                 editor_options: Optional[Dict] = None,
                 filter_type: str = "text",
                 filter_options: Optional[Dict] = None):
        """
        Initialize column configuration.

        Args:
            name: Column display name
            width: Column width in pixels
            resize_mode: Qt resize mode (Interactive, Fixed, Stretch)
            editor_type: Type of editor ("text", "checkbox", "checkbox_centered", "combobox", "combobox_data")
            editor_options: Options for editor (e.g., {'items': [...]} for combobox,
                           {'items': [...], 'items_data': [...]} for combobox_data)
            filter_type: Type of filter ("text", "combobox", "none")
            filter_options: Options for filter (e.g., combobox items)
        """
        self.name = name
        self.width = width
        self.resize_mode = resize_mode
        self.editor_type = editor_type
        self.editor_options = editor_options or {}
        self.filter_type = filter_type
        self.filter_options = filter_options or {}


class DataGridWidget(QWidget):
    """
    Reusable data grid widget with filtering, sorting, and action buttons.

    Features:
    - Configurable columns with different editor types
    - Filter row with per-column filtering
    - Action buttons (Add, Edit, Remove, Move Up/Down)
    - Multi-row selection and operations
    - Custom button support

    Signals:
        data_changed: Emitted when grid data changes
        row_added: Emitted when a row is added
        row_removed: Emitted when rows are removed
        row_moved: Emitted when a row is moved
    """

    data_changed = pyqtSignal()
    row_added = pyqtSignal(int)  # row index
    row_removed = pyqtSignal(list)  # list of removed row indices
    row_moved = pyqtSignal(int, int)  # from_row, to_row

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuration
        self._columns: List[ColumnConfig] = []
        self._filters: List[QWidget] = []
        self._show_filters = True
        self._show_add_button = True
        self._show_edit_button = True
        self._show_remove_button = True
        self._show_move_buttons = True
        self._custom_buttons: List[Dict] = []

        # Custom callbacks
        self._add_callback: Optional[Callable] = None
        self._edit_callback: Optional[Callable] = None
        self._remove_callback: Optional[Callable] = None
        self._cell_setup_callback: Optional[Callable] = None

        # UI Components
        self.table: Optional[MultiSelectTableWidget] = None
        self.filter_group: Optional[QGroupBox] = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

    def configure(self, columns: List[ColumnConfig],
                  show_filters: bool = True,
                  show_add_button: bool = True,
                  show_edit_button: bool = True,
                  show_remove_button: bool = True,
                  show_move_buttons: bool = True,
                  custom_buttons: Optional[List[Dict]] = None):
        """
        Configure the grid widget.

        Args:
            columns: List of ColumnConfig objects
            show_filters: Show filter row
            show_add_button: Show add button
            show_edit_button: Show edit button
            show_remove_button: Show remove button
            show_move_buttons: Show move up/down buttons
            custom_buttons: List of custom button configs (dict with 'text', 'tooltip', 'callback')
        """
        self._columns = columns
        self._show_filters = show_filters
        self._show_add_button = show_add_button
        self._show_edit_button = show_edit_button
        self._show_remove_button = show_remove_button
        self._show_move_buttons = show_move_buttons
        self._custom_buttons = custom_buttons or []

        self._rebuild_ui()

    def _rebuild_ui(self):
        """Rebuild the UI based on configuration."""
        # Clear existing layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        # Build filter section if enabled
        if self._show_filters and self._columns:
            self._build_filters()

        # Build toolbar with action buttons
        if any([self._show_add_button, self._show_edit_button,
                self._show_remove_button, self._show_move_buttons,
                self._custom_buttons]):
            self._build_toolbar()

        # Build table
        self._build_table()

    def _clear_layout(self, layout):
        """Recursively clear a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _build_filters(self):
        """Build the filter section."""
        self.filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(self.filter_group)
        filter_layout.setContentsMargins(5, 5, 5, 5)
        filter_layout.setSpacing(3)

        # Labels row
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(0)  # Remove spacing for better alignment
        for col in self._columns:
            if col.filter_type != "none":
                label = QLabel(col.name)
                label.setFixedWidth(col.width)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                labels_layout.addWidget(label)

        # Small spacer for clear button
        clear_label = QLabel("")
        clear_label.setFixedWidth(30)
        labels_layout.addWidget(clear_label)

        filter_layout.addLayout(labels_layout)

        # Filter inputs row
        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(0)  # Remove spacing for better alignment
        self._filters = []

        for col in self._columns:
            if col.filter_type == "text":
                filter_widget = QLineEdit()
                filter_widget.setPlaceholderText(f"Filter {col.name}...")
                filter_widget.setFixedWidth(col.width)
                filter_widget.textChanged.connect(self._apply_filters)
                self._filters.append(filter_widget)
                inputs_layout.addWidget(filter_widget)

            elif col.filter_type == "combobox":
                filter_widget = QComboBox()
                filter_widget.setFixedWidth(col.width)
                items = col.filter_options.get('items', ['All'])
                filter_widget.addItems(items)
                if col.filter_options.get('editable', False):
                    filter_widget.setEditable(True)
                    filter_widget.lineEdit().setPlaceholderText(f"Filter {col.name}...")
                    filter_widget.lineEdit().textChanged.connect(self._apply_filters)
                filter_widget.currentTextChanged.connect(self._apply_filters)
                self._filters.append(filter_widget)
                inputs_layout.addWidget(filter_widget)

            elif col.filter_type == "none":
                self._filters.append(None)

        # Clear filters button - small icon button
        clear_btn = QPushButton("⊗")
        clear_btn.setToolTip("Clear Filters")
        clear_btn.setFixedSize(28, 28)
        clear_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
        clear_btn.clicked.connect(self._clear_filters)
        inputs_layout.addWidget(clear_btn)

        filter_layout.addLayout(inputs_layout)
        self.layout.addWidget(self.filter_group)

    def _build_toolbar(self):
        """Build the toolbar with action buttons."""
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 3, 0, 3)
        toolbar_layout.setSpacing(2)

        if self._show_add_button:
            add_btn = QPushButton("+")
            add_btn.setToolTip("Add Row")
            add_btn.setFixedSize(28, 28)
            add_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
            add_btn.clicked.connect(self._on_add)
            toolbar_layout.addWidget(add_btn)

        if self._show_edit_button:
            edit_btn = QPushButton("✎")
            edit_btn.setToolTip("Edit Row")
            edit_btn.setFixedSize(28, 28)
            edit_btn.setStyleSheet("font-size: 14px;")
            edit_btn.clicked.connect(self._on_edit)
            toolbar_layout.addWidget(edit_btn)

        if self._show_remove_button:
            remove_btn = QPushButton("✕")
            remove_btn.setToolTip("Remove Rows")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setStyleSheet("font-weight: bold; font-size: 14px; color: #c44;")
            remove_btn.clicked.connect(self._on_remove)
            toolbar_layout.addWidget(remove_btn)

        if self._show_move_buttons:
            if self._show_add_button or self._show_edit_button or self._show_remove_button:
                toolbar_layout.addWidget(QLabel("|"))  # Separator

            move_to_top_btn = QPushButton("⇈")
            move_to_top_btn.setToolTip("Move to Top")
            move_to_top_btn.setFixedSize(28, 28)
            move_to_top_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
            move_to_top_btn.clicked.connect(self._move_row_to_top)
            toolbar_layout.addWidget(move_to_top_btn)

            move_up_btn = QPushButton("↑")
            move_up_btn.setToolTip("Move Up")
            move_up_btn.setFixedSize(28, 28)
            move_up_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
            move_up_btn.clicked.connect(self._move_row_up)
            toolbar_layout.addWidget(move_up_btn)

            move_down_btn = QPushButton("↓")
            move_down_btn.setToolTip("Move Down")
            move_down_btn.setFixedSize(28, 28)
            move_down_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
            move_down_btn.clicked.connect(self._move_row_down)
            toolbar_layout.addWidget(move_down_btn)

            move_to_bottom_btn = QPushButton("⇊")
            move_to_bottom_btn.setToolTip("Move to Bottom")
            move_to_bottom_btn.setFixedSize(28, 28)
            move_to_bottom_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
            move_to_bottom_btn.clicked.connect(self._move_row_to_bottom)
            toolbar_layout.addWidget(move_to_bottom_btn)

        # Add custom buttons
        if self._custom_buttons:
            toolbar_layout.addWidget(QLabel("|"))  # Separator
            for btn_config in self._custom_buttons:
                btn = QPushButton(btn_config.get('text', ''))
                if 'tooltip' in btn_config:
                    btn.setToolTip(btn_config['tooltip'])
                if 'style' in btn_config:
                    btn.setStyleSheet(btn_config['style'])
                else:
                    btn.setFixedSize(28, 28)
                if 'callback' in btn_config:
                    btn.clicked.connect(btn_config['callback'])
                toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        self.layout.addLayout(toolbar_layout)

    def _build_table(self):
        """Build the data table."""
        self.table = MultiSelectTableWidget()
        self.table.setColumnCount(len(self._columns))
        self.table.setHorizontalHeaderLabels([col.name for col in self._columns])

        # Enable extended selection
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        # Configure column widths and resize modes
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)

        for i, col in enumerate(self._columns):
            self.table.setColumnWidth(i, col.width)
            header.setSectionResizeMode(i, col.resize_mode)

        self.layout.addWidget(self.table)

    def _apply_filters(self):
        """Apply filters to show/hide rows based on filter criteria."""
        if not self.table or not self._filters:
            return

        for row in range(self.table.rowCount()):
            show_row = True

            for col_idx, filter_widget in enumerate(self._filters):
                if filter_widget is None:
                    continue

                # Get cell value - check for widget first, then item
                cell_value = ""
                widget = self.table.cellWidget(row, col_idx)
                item = self.table.item(row, col_idx)

                # Determine column type
                col_editor_type = "text"
                if col_idx < len(self._columns):
                    col_editor_type = self._columns[col_idx].editor_type

                # Get value based on column type
                if widget and col_editor_type in ['checkbox_centered', 'combobox', 'combobox_data']:
                    # Get value from widget
                    if hasattr(widget, 'checkbox'):
                        # Checkbox widget
                        from PyQt6.QtWidgets import QCheckBox
                        checkbox = widget.checkbox
                        if isinstance(checkbox, QCheckBox):
                            cell_value = "true" if checkbox.isChecked() else "false"
                    elif isinstance(widget, QComboBox):
                        # Combobox widget
                        cell_value = widget.currentText().lower()
                elif item:
                    # Get value from item
                    cell_value = item.text().lower()

                # Apply filter based on filter widget type
                if isinstance(filter_widget, QLineEdit):
                    filter_value = filter_widget.text().lower()
                    if filter_value and filter_value not in cell_value:
                        show_row = False
                        break

                elif isinstance(filter_widget, QComboBox):
                    filter_value = filter_widget.currentText()
                    if filter_value and filter_value != "All":
                        # Special handling for Nullable filter
                        if filter_value == "Nullable":
                            if cell_value != "true":
                                show_row = False
                                break
                        elif filter_value == "Not Nullable":
                            if cell_value != "false":
                                show_row = False
                                break
                        # Special handling for "No Domain" / "No Stereotype"
                        elif filter_value in ["No Domain", "No Stereotype", "No Value"]:
                            if cell_value:
                                show_row = False
                                break
                        # Standard text matching
                        elif filter_value.lower() != cell_value:
                            show_row = False
                            break

            self.table.setRowHidden(row, not show_row)

    def _clear_filters(self):
        """Clear all filter values."""
        for filter_widget in self._filters:
            if isinstance(filter_widget, QLineEdit):
                filter_widget.clear()
            elif isinstance(filter_widget, QComboBox):
                filter_widget.setCurrentIndex(0)

    def _on_add(self):
        """Handle add button click."""
        if self._add_callback:
            self._add_callback()
        else:
            self.add_row()

    def _on_edit(self):
        """Handle edit button click."""
        if self._edit_callback:
            self._edit_callback()
        else:
            current_row = self.table.currentRow()
            if current_row >= 0:
                current_col = self.table.currentColumn()
                if current_col >= 0:
                    self.table.editItem(self.table.item(current_row, current_col))

    def _on_remove(self):
        """Handle remove button click."""
        if self._remove_callback:
            self._remove_callback()
        else:
            self.remove_selected_rows()

    def add_row(self, data: Optional[List[Any]] = None) -> int:
        """
        Add a new row to the grid.

        Args:
            data: Optional list of values for each column

        Returns:
            The row index of the new row
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Setup cells based on column configuration
        for col_idx, col in enumerate(self._columns):
            value = data[col_idx] if data and col_idx < len(data) else ""

            if col.editor_type == "text":
                self.table.setItem(row, col_idx, QTableWidgetItem(str(value)))

            elif col.editor_type == "checkbox":
                self._setup_checkbox_cell(row, col_idx, bool(value))

            elif col.editor_type == "checkbox_centered":
                self._setup_checkbox_centered_cell(row, col_idx, bool(value))

            elif col.editor_type == "combobox":
                self._setup_combobox_cell(row, col_idx, str(value),
                                         col.editor_options.get('items', []))

            elif col.editor_type == "combobox_data":
                items = col.editor_options.get('items', [])
                items_data = col.editor_options.get('items_data', items)
                self._setup_combobox_data_cell(row, col_idx, str(value), items, items_data)

            # Allow custom cell setup
            if self._cell_setup_callback:
                self._cell_setup_callback(row, col_idx, value)

        self._apply_filters()
        self.table.setCurrentCell(row, 0)
        self.row_added.emit(row)
        self.data_changed.emit()

        return row

    def _setup_checkbox_cell(self, row: int, col: int, checked: bool):
        """Setup a checkbox cell."""
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled |
                     Qt.ItemFlag.ItemIsSelectable)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.table.setItem(row, col, item)

    def _setup_checkbox_centered_cell(self, row: int, col: int, checked: bool):
        """Setup a centered checkbox cell (checkbox in a centered widget)."""
        from PyQt6.QtWidgets import QCheckBox

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        checkbox = QCheckBox()
        checkbox.setChecked(checked)

        # Center the checkbox
        layout.addStretch()
        layout.addWidget(checkbox)
        layout.addStretch()

        # Set the widget as the cell widget
        self.table.setCellWidget(row, col, widget)

        # Store checkbox reference for easy access
        widget.checkbox = checkbox

    def _setup_combobox_cell(self, row: int, col: int, value: str, items: List[str]):
        """Setup a combobox cell."""
        combo = QComboBox()
        combo.addItems(items)
        if value in items:
            combo.setCurrentText(value)
        self.table.setCellWidget(row, col, combo)

    def _setup_combobox_data_cell(self, row: int, col: int, value: str, items: List[str], items_data: List[str]):
        """Setup a combobox cell with separate display text and data values."""
        combo = QComboBox()
        combo.setEditable(False)

        # Add items with data
        for display_text, data_value in zip(items, items_data):
            combo.addItem(display_text, data_value)

        # Set current selection by data value
        if value:
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        self.table.setCellWidget(row, col, combo)

    def remove_selected_rows(self, confirm: bool = True) -> List[int]:
        """
        Remove all selected rows.

        Args:
            confirm: Show confirmation dialog for multiple rows

        Returns:
            List of removed row indices
        """
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            current_row = self.table.currentRow()
            if current_row >= 0:
                selected_rows.add(current_row)

        if not selected_rows:
            return []

        # Confirm if removing multiple rows
        if confirm and len(selected_rows) > 1:
            reply = QMessageBox.question(
                self,
                "Remove Rows",
                f"Remove {len(selected_rows)} selected rows?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply != QMessageBox.StandardButton.Yes:
                return []

        # Remove rows in reverse order
        removed_rows = sorted(selected_rows, reverse=True)
        for row in removed_rows:
            self.table.removeRow(row)

        self._apply_filters()
        self.row_removed.emit(list(removed_rows))
        self.data_changed.emit()

        return removed_rows

    def _move_row_up(self):
        """Move selected row(s) up."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))

        if not selected_rows:
            current_row = self.table.currentRow()
            if current_row >= 0:
                selected_rows = [current_row]

        if not selected_rows or selected_rows[0] == 0:
            return

        self.table.blockSignals(True)

        try:
            # Check if rows are contiguous
            is_contiguous = all(selected_rows[i] + 1 == selected_rows[i + 1]
                               for i in range(len(selected_rows) - 1))

            if is_contiguous:
                first_row = selected_rows[0]
                for offset in range(len(selected_rows)):
                    self._swap_rows(first_row - 1 + offset, first_row + offset)

                # Update selection
                self.table.clearSelection()
                for row in selected_rows:
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row - 1, col)
                        if item:
                            item.setSelected(True)
            else:
                # Move each row individually
                for row in selected_rows:
                    if row > 0:
                        self._swap_rows(row - 1, row)

                # Update selection
                self.table.clearSelection()
                for row in selected_rows:
                    new_row = row - 1 if row > 0 else row
                    for col in range(self.table.columnCount()):
                        item = self.table.item(new_row, col)
                        if item:
                            item.setSelected(True)

        finally:
            self.table.blockSignals(False)

        self.data_changed.emit()

    def _move_row_down(self):
        """Move selected row(s) down."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()), reverse=True)

        if not selected_rows:
            current_row = self.table.currentRow()
            if current_row >= 0:
                selected_rows = [current_row]

        if not selected_rows or selected_rows[0] >= self.table.rowCount() - 1:
            return

        self.table.blockSignals(True)

        try:
            # Check if rows are contiguous
            is_contiguous = all(selected_rows[i] - 1 == selected_rows[i + 1]
                               for i in range(len(selected_rows) - 1))

            if is_contiguous:
                last_row = selected_rows[0]
                for offset in range(len(selected_rows)):
                    self._swap_rows(last_row + 1 - offset, last_row - offset)

                # Update selection
                self.table.clearSelection()
                for row in reversed(selected_rows):
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row + 1, col)
                        if item:
                            item.setSelected(True)
            else:
                # Move each row individually
                for row in selected_rows:
                    if row < self.table.rowCount() - 1:
                        self._swap_rows(row, row + 1)

                # Update selection
                self.table.clearSelection()
                for row in selected_rows:
                    new_row = row + 1 if row < self.table.rowCount() - 1 else row
                    for col in range(self.table.columnCount()):
                        item = self.table.item(new_row, col)
                        if item:
                            item.setSelected(True)

        finally:
            self.table.blockSignals(False)

        self.data_changed.emit()

    def _move_row_to_top(self):
        """Move selected row(s) to the top of the table."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))

        if not selected_rows:
            current_row = self.table.currentRow()
            if current_row >= 0:
                selected_rows = [current_row]

        if not selected_rows or selected_rows[0] == 0:
            return  # Already at top

        self.table.blockSignals(True)

        try:
            # Extract data from selected rows
            rows_data = []
            for row in sorted(selected_rows, reverse=True):
                rows_data.insert(0, self.get_row_data(row))
                self.table.removeRow(row)

            # Insert rows at top
            for i, row_data in enumerate(rows_data):
                self.table.insertRow(i)
                self._populate_row(i, row_data)

            # Update selection
            self.table.clearSelection()
            for i in range(len(rows_data)):
                for col in range(self.table.columnCount()):
                    item = self.table.item(i, col)
                    if item:
                        item.setSelected(True)

        finally:
            self.table.blockSignals(False)

        self.data_changed.emit()

    def _move_row_to_bottom(self):
        """Move selected row(s) to the bottom of the table."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))

        if not selected_rows:
            current_row = self.table.currentRow()
            if current_row >= 0:
                selected_rows = [current_row]

        if not selected_rows or selected_rows[-1] == self.table.rowCount() - 1:
            return  # Already at bottom

        self.table.blockSignals(True)

        try:
            # Extract data from selected rows
            rows_data = []
            for row in sorted(selected_rows, reverse=True):
                rows_data.insert(0, self.get_row_data(row))
                self.table.removeRow(row)

            # Insert rows at bottom
            bottom_start = self.table.rowCount()
            for i, row_data in enumerate(rows_data):
                row_index = bottom_start + i
                self.table.insertRow(row_index)
                self._populate_row(row_index, row_data)

            # Update selection
            self.table.clearSelection()
            for i in range(len(rows_data)):
                row_index = bottom_start + i
                for col in range(self.table.columnCount()):
                    item = self.table.item(row_index, col)
                    if item:
                        item.setSelected(True)

        finally:
            self.table.blockSignals(False)

        self.data_changed.emit()

    def _populate_row(self, row: int, data: List[Any]):
        """Populate a row with data (helper method for move operations)."""
        for col_idx, col in enumerate(self._columns):
            value = data[col_idx] if col_idx < len(data) else ""

            if col.editor_type == "text":
                self.table.setItem(row, col_idx, QTableWidgetItem(str(value)))

            elif col.editor_type == "checkbox":
                self._setup_checkbox_cell(row, col_idx, bool(value))

            elif col.editor_type == "checkbox_centered":
                self._setup_checkbox_centered_cell(row, col_idx, bool(value))

            elif col.editor_type == "combobox":
                self._setup_combobox_cell(row, col_idx, str(value),
                                         col.editor_options.get('items', []))

            elif col.editor_type == "combobox_data":
                items = col.editor_options.get('items', [])
                items_data = col.editor_options.get('items_data', items)
                self._setup_combobox_data_cell(row, col_idx, str(value), items, items_data)

            # Allow custom cell setup
            if self._cell_setup_callback:
                self._cell_setup_callback(row, col_idx, value)

    def _swap_rows(self, row1: int, row2: int):
        """Swap two rows in the table by swapping their data."""
        # Get data from both rows
        data1 = self.get_row_data(row1)
        data2 = self.get_row_data(row2)

        # Set the swapped data back
        self.set_row_data(row1, data2)
        self.set_row_data(row2, data1)

        self.row_moved.emit(row1, row2)

    def get_row_data(self, row: int) -> List[Any]:
        """
        Get data from a specific row.

        Args:
            row: Row index

        Returns:
            List of values for each column
        """
        data = []
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            widget = self.table.cellWidget(row, col)

            # Check if this column is configured to use a widget
            use_widget = False
            col_editor_type = "text"  # default
            if self._columns and col < len(self._columns):
                col_config = self._columns[col]
                col_editor_type = col_config.editor_type
                use_widget = col_editor_type in ['checkbox_centered', 'combobox', 'combobox_data']

            if widget and use_widget:
                # Check for centered checkbox widget
                if hasattr(widget, 'checkbox'):
                    from PyQt6.QtWidgets import QCheckBox
                    checkbox = widget.checkbox
                    if isinstance(checkbox, QCheckBox):
                        data.append(checkbox.isChecked())
                        continue

                # Check for combobox widget
                if isinstance(widget, QComboBox):
                    # Return currentData() if available, otherwise currentText()
                    current_data = widget.currentData()
                    if current_data is not None:
                        data.append(current_data)
                    else:
                        data.append(widget.currentText())
                    continue

            # Use item data for text/checkbox cells
            if item:
                # For checkbox editor type (not checkbox_centered), check if it's checkable
                if col_editor_type == "checkbox" and (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
                    data.append(item.checkState() == Qt.CheckState.Checked)
                else:
                    # For text columns, always use text even if checkable flag is somehow set
                    data.append(item.text())
            else:
                data.append("")

        return data

    def get_all_data(self) -> List[List[Any]]:
        """
        Get all data from the grid.

        Returns:
            List of rows, where each row is a list of values
        """
        all_data = []
        for row in range(self.table.rowCount()):
            all_data.append(self.get_row_data(row))
        return all_data

    def set_row_data(self, row: int, data: List[Any]):
        """
        Set data for a specific row.

        Args:
            row: Row index
            data: List of values for each column
        """
        for col, value in enumerate(data):
            if col >= self.table.columnCount():
                break

            item = self.table.item(row, col)
            widget = self.table.cellWidget(row, col)

            # Check if this column is configured to use a widget
            use_widget = False
            col_editor_type = "text"  # default
            if self._columns and col < len(self._columns):
                col_config = self._columns[col]
                col_editor_type = col_config.editor_type
                use_widget = col_editor_type in ['checkbox_centered', 'combobox', 'combobox_data']

            if widget and use_widget:
                # Check for centered checkbox widget
                if hasattr(widget, 'checkbox'):
                    from PyQt6.QtWidgets import QCheckBox
                    checkbox = widget.checkbox
                    if isinstance(checkbox, QCheckBox):
                        checkbox.setChecked(bool(value))
                        continue

                # Check for combobox widget
                if isinstance(widget, QComboBox):
                    # Try to set by data first, then by text
                    index = widget.findData(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                    else:
                        widget.setCurrentText(str(value))
                    continue

            # Update item for text/checkbox cells
            if item:
                # For checkbox editor type (not checkbox_centered), check if it's checkable
                if col_editor_type == "checkbox" and (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
                    item.setCheckState(Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)
                else:
                    # For text columns, always set text even if checkable flag is set
                    item.setText(str(value))

    def clear_data(self):
        """Clear all rows from the grid."""
        self.table.setRowCount(0)
        self.data_changed.emit()

    def get_cell_widget(self, row: int, col: int):
        """
        Get the widget at a specific cell (for comboboxes, checkboxes, etc.).

        Args:
            row: Row index
            col: Column index

        Returns:
            The widget or None if it's a standard item
        """
        return self.table.cellWidget(row, col)

    def get_cell_item(self, row: int, col: int):
        """
        Get the table item at a specific cell.

        Args:
            row: Row index
            col: Column index

        Returns:
            The QTableWidgetItem or None
        """
        return self.table.item(row, col)

    def set_add_callback(self, callback: Callable):
        """Set custom callback for add button."""
        self._add_callback = callback

    def set_edit_callback(self, callback: Callable):
        """Set custom callback for edit button."""
        self._edit_callback = callback

    def set_remove_callback(self, callback: Callable):
        """Set custom callback for remove button."""
        self._remove_callback = callback

    def set_cell_setup_callback(self, callback: Callable):
        """Set custom callback for setting up cells (called after default setup)."""
        self._cell_setup_callback = callback

