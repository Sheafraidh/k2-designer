# Integration Guide: Using DataGridWidget in Table Dialog

This guide shows how to refactor the existing table dialog to use the DataGridWidget component for the Keys tab and other use cases.

## Current vs. New Approach

### Before: Manual Grid Implementation

```python
# In table_dialog.py - Keys tab (OLD approach)
def _setup_keys_tab(self, tab_widget):
    layout = QVBoxLayout(tab_widget)
    
    # Manually create toolbar
    toolbar_layout = QHBoxLayout()
    self.add_key_btn = QPushButton("+")
    self.add_key_btn.setToolTip("Add Key")
    self.add_key_btn.setFixedSize(28, 28)
    self.add_key_btn.clicked.connect(self._add_key)
    toolbar_layout.addWidget(self.add_key_btn)
    # ... more buttons ...
    
    # Manually create table
    self.keys_table = QTableWidget()
    self.keys_table.setColumnCount(6)
    self.keys_table.setHorizontalHeaderLabels([...])
    # ... manual column setup ...
    
    layout.addLayout(toolbar_layout)
    layout.addWidget(self.keys_table)
```

### After: Using DataGridWidget

```python
# In table_dialog.py - Keys tab (NEW approach)
from ..widgets import DataGridWidget, ColumnConfig

def _setup_keys_tab(self, tab_widget):
    layout = QVBoxLayout(tab_widget)
    
    # Create grid widget
    self.keys_grid = DataGridWidget()
    
    # Define columns
    columns = [
        ColumnConfig(
            name="Name",
            width=150,
            resize_mode=QHeaderView.ResizeMode.Interactive,
            editor_type="text",
            filter_type="text"
        ),
        ColumnConfig(
            name="Type",
            width=120,
            resize_mode=QHeaderView.ResizeMode.Fixed,
            editor_type="combobox",
            editor_options={'items': ['PRIMARY', 'FOREIGN', 'UNIQUE']},
            filter_type="combobox",
            filter_options={'items': ['All', 'PRIMARY', 'FOREIGN', 'UNIQUE']}
        ),
        ColumnConfig(
            name="Columns",
            width=200,
            resize_mode=QHeaderView.ResizeMode.Stretch,
            editor_type="text",
            filter_type="text"
        ),
        ColumnConfig(
            name="Referenced Table",
            width=150,
            resize_mode=QHeaderView.ResizeMode.Interactive,
            editor_type="text",
            filter_type="text"
        ),
        ColumnConfig(
            name="Referenced Columns",
            width=150,
            resize_mode=QHeaderView.ResizeMode.Interactive,
            editor_type="text",
            filter_type="text"
        ),
        ColumnConfig(
            name="On Delete",
            width=120,
            resize_mode=QHeaderView.ResizeMode.Fixed,
            editor_type="combobox",
            editor_options={'items': ['', 'CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']},
            filter_type="combobox",
            filter_options={'items': ['All', 'CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']}
        ),
    ]
    
    # Configure and add to layout
    self.keys_grid.configure(
        columns=columns,
        show_filters=True,
        show_add_button=True,
        show_edit_button=True,
        show_remove_button=True,
        show_move_buttons=False
    )
    
    layout.addWidget(self.keys_grid)
```

## Benefits

1. **Less Code**: ~50% reduction in UI setup code
2. **Built-in Features**: Filtering, multi-select, move operations work out of the box
3. **Consistency**: Same look and behavior across all grids
4. **Reusability**: Easy to add grids to new dialogs
5. **Maintainability**: Fix bugs once, benefits all grids

## Step-by-Step Integration

### Step 1: Import the Widget

```python
# At the top of your dialog file
from ..widgets import DataGridWidget, ColumnConfig
from PyQt6.QtWidgets import QHeaderView
```

### Step 2: Define Column Configuration

Create a list of ColumnConfig objects describing your columns:

```python
def _create_column_config(self):
    """Create column configuration for the grid."""
    return [
        ColumnConfig(
            name="Column Name",           # Display name
            width=150,                    # Width in pixels
            resize_mode=QHeaderView.ResizeMode.Interactive,  # or Fixed, Stretch
            editor_type="text",           # "text", "checkbox", "combobox"
            editor_options={},            # Options for editor (e.g., combobox items)
            filter_type="text",           # "text", "combobox", "none"
            filter_options={}             # Options for filter
        ),
        # ... more columns ...
    ]
```

### Step 3: Replace Table Creation

Replace your manual table/toolbar creation with:

```python
# Create the grid
self.my_grid = DataGridWidget()

# Configure it
self.my_grid.configure(
    columns=self._create_column_config(),
    show_filters=True,
    show_add_button=True,
    show_edit_button=True,
    show_remove_button=True,
    show_move_buttons=True,
    custom_buttons=[]  # Optional custom buttons
)

# Add to layout
layout.addWidget(self.my_grid)
```

### Step 4: Handle Data Loading

Replace direct table access with grid methods:

```python
# OLD: Direct table access
def _load_keys(self):
    self.keys_table.setRowCount(0)
    for key in self.table.keys:
        row = self.keys_table.rowCount()
        self.keys_table.insertRow(row)
        self.keys_table.setItem(row, 0, QTableWidgetItem(key.name))
        # ... more items ...

# NEW: Using grid methods
def _load_keys(self):
    self.keys_grid.clear_data()
    for key in self.table.keys:
        self.keys_grid.add_row([
            key.name,
            key.key_type,
            ", ".join(key.columns),
            key.referenced_table or "",
            ", ".join(key.referenced_columns) if key.referenced_columns else "",
            key.on_delete or ""
        ])
```

### Step 5: Handle Data Saving

Replace table reading with grid data access:

```python
# OLD: Read from table
def _save_keys(self):
    keys = []
    for row in range(self.keys_table.rowCount()):
        name = self.keys_table.item(row, 0).text()
        key_type = self.keys_table.item(row, 1).text()
        # ... more items ...
        keys.append(Key(name, columns, key_type, ...))

# NEW: Read from grid
def _save_keys(self):
    keys = []
    for row_data in self.keys_grid.get_all_data():
        name, key_type, cols_str, ref_table, ref_cols_str, on_delete = row_data
        columns = [c.strip() for c in cols_str.split(",") if c.strip()]
        ref_columns = [c.strip() for c in ref_cols_str.split(",") if c.strip()]
        keys.append(Key(
            name=name,
            columns=columns,
            key_type=key_type,
            referenced_table=ref_table if ref_table else None,
            referenced_columns=ref_columns if ref_columns else None,
            on_delete=on_delete if on_delete else None
        ))
    return keys
```

### Step 6: Connect to Signals (Optional)

```python
# Track changes
self.keys_grid.data_changed.connect(self._on_keys_changed)

def _on_keys_changed(self):
    # Mark dialog as modified, enable save button, etc.
    self.modified = True
```

## Advanced Usage

### Custom Add/Edit Callbacks

If you need a dialog for adding/editing:

```python
def _custom_add_key(self):
    """Show a dialog to add a key."""
    dialog = KeyEditDialog(parent=self)
    if dialog.exec():
        key_data = dialog.get_key_data()
        self.keys_grid.add_row(key_data)

def _custom_edit_key(self):
    """Show a dialog to edit a key."""
    row = self.keys_grid.table.currentRow()
    if row >= 0:
        current_data = self.keys_grid.get_row_data(row)
        dialog = KeyEditDialog(initial_data=current_data, parent=self)
        if dialog.exec():
            key_data = dialog.get_key_data()
            self.keys_grid.set_row_data(row, key_data)

# Set the callbacks
self.keys_grid.set_add_callback(self._custom_add_key)
self.keys_grid.set_edit_callback(self._custom_edit_key)
```

### Custom Cell Setup

For custom cell appearance:

```python
def _setup_key_cell(self, row, col, value):
    """Custom cell setup for keys grid."""
    if col == 1:  # Type column
        # Make PRIMARY keys bold
        if value == "PRIMARY":
            item = self.keys_grid.table.item(row, col)
            font = item.font()
            font.setBold(True)
            item.setFont(font)

self.keys_grid.set_cell_setup_callback(self._setup_key_cell)
```

### Custom Buttons

Add custom functionality:

```python
custom_buttons = [
    {
        'text': '⚙️',
        'tooltip': 'Generate Key Name',
        'callback': self._generate_key_name,
        'style': 'font-size: 14px;'
    }
]

self.keys_grid.configure(
    columns=columns,
    custom_buttons=custom_buttons
)
```

## Migration Checklist

- [ ] Import DataGridWidget and ColumnConfig
- [ ] Create column configuration
- [ ] Replace table widget creation with DataGridWidget
- [ ] Update data loading code to use add_row()
- [ ] Update data saving code to use get_all_data()
- [ ] Remove manual toolbar creation
- [ ] Remove manual filter implementation
- [ ] Connect to signals if needed
- [ ] Test multi-selection
- [ ] Test filtering
- [ ] Test move up/down if enabled
- [ ] Update any references to old table widget

## Complete Example: Keys Tab Refactor

Here's a complete before/after for the Keys tab:

```python
# BEFORE: ~150 lines of code
def _setup_keys_tab(self, tab_widget):
    # Manual toolbar creation (~30 lines)
    # Manual table creation (~40 lines)
    # Manual filter setup (~40 lines)
    # Manual button connections (~20 lines)
    # Manual data loading (~20 lines)
    pass

# AFTER: ~50 lines of code
def _setup_keys_tab(self, tab_widget):
    layout = QVBoxLayout(tab_widget)
    
    self.keys_grid = DataGridWidget()
    
    columns = [
        ColumnConfig("Name", 150, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
        ColumnConfig("Type", 120, QHeaderView.ResizeMode.Fixed, "combobox", 
                    {'items': ['PRIMARY', 'FOREIGN', 'UNIQUE']}, "combobox",
                    {'items': ['All', 'PRIMARY', 'FOREIGN', 'UNIQUE']}),
        ColumnConfig("Columns", 200, QHeaderView.ResizeMode.Stretch, "text", {}, "text", {}),
        ColumnConfig("Referenced Table", 150, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
        ColumnConfig("Referenced Columns", 150, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
        ColumnConfig("On Delete", 120, QHeaderView.ResizeMode.Fixed, "combobox",
                    {'items': ['', 'CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']},
                    "combobox", {'items': ['All', 'CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']}),
    ]
    
    self.keys_grid.configure(columns=columns, show_filters=True, 
                            show_add_button=True, show_edit_button=True,
                            show_remove_button=True, show_move_buttons=False)
    
    layout.addWidget(self.keys_grid)
    
    # Info label
    info = QLabel("Tips: • Type: PRIMARY, FOREIGN, or UNIQUE • Columns: comma-separated list")
    info.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
    info.setWordWrap(True)
    layout.addWidget(info)
```

## Summary

The DataGridWidget provides a consistent, feature-rich grid component that significantly reduces boilerplate code while adding powerful features like filtering and multi-row operations. By migrating existing grids to use this component, you'll have:

- **Consistent UX** across all grids
- **Less code** to maintain
- **More features** out of the box
- **Easier testing** with a single, well-tested component
- **Better extensibility** for future enhancements

