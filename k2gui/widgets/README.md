# DataGridWidget

A reusable Qt6 widget for displaying and editing tabular data with filtering, sorting, and action buttons.

## Features

- **Configurable Columns**: Define columns with custom widths, resize modes, and editor types
- **Built-in Filtering**: Per-column filters with text search and dropdown options
- **Action Buttons**: Add, Edit, Remove, Move Up/Down with icon-based toolbar
- **Multi-Row Selection**: Select and operate on multiple rows at once
- **Custom Buttons**: Add custom buttons with callbacks to the toolbar
- **Editor Types**: Support for text fields, checkboxes, and comboboxes
- **Callbacks**: Hook into add, edit, remove, and cell setup operations
- **Signals**: Get notified of data changes, row additions, removals, and movements

## Basic Usage

```python
from k2_designer.widgets import DataGridWidget, ColumnConfig
from PyQt6.QtWidgets import QHeaderView

# Create the widget
grid = DataGridWidget()

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
        editor_options={'items': ['Type A', 'Type B', 'Type C']},
        filter_type="combobox",
        filter_options={'items': ['All', 'Type A', 'Type B', 'Type C']}
    ),
    ColumnConfig(
        name="Active",
        width=80,
        resize_mode=QHeaderView.ResizeMode.Fixed,
        editor_type="checkbox",
        filter_type="combobox",
        filter_options={'items': ['All', 'Yes', 'No']}
    ),
]

# Configure the grid
grid.configure(
    columns=columns,
    show_filters=True,
    show_add_button=True,
    show_edit_button=True,
    show_remove_button=True,
    show_move_buttons=True
)

# Add data
grid.add_row(["Item 1", "Type A", True])
grid.add_row(["Item 2", "Type B", False])

# Get all data
all_data = grid.get_all_data()
```

## Column Configuration

### ColumnConfig Parameters

- **name** (str): Display name for the column header
- **width** (int): Column width in pixels (default: 100)
- **resize_mode** (QHeaderView.ResizeMode): How the column resizes
  - `Interactive`: User can resize
  - `Fixed`: Fixed width
  - `Stretch`: Column stretches to fill space
- **editor_type** (str): Type of cell editor (default: "text")
  - `"text"`: Standard text input
  - `"checkbox"`: Checkbox for boolean values
  - `"combobox"`: Dropdown selector
- **editor_options** (dict): Options for the editor
  - For combobox: `{'items': ['Option 1', 'Option 2']}`
- **filter_type** (str): Type of filter (default: "text")
  - `"text"`: Text search filter
  - `"combobox"`: Dropdown filter
  - `"none"`: No filter for this column
- **filter_options** (dict): Options for the filter
  - For combobox: `{'items': ['All', 'Option 1'], 'editable': True}`

## Configuration Options

### configure() Method

```python
grid.configure(
    columns: List[ColumnConfig],          # Column definitions
    show_filters: bool = True,            # Show filter row
    show_add_button: bool = True,         # Show add button
    show_edit_button: bool = True,        # Show edit button  
    show_remove_button: bool = True,      # Show remove button
    show_move_buttons: bool = True,       # Show move up/down buttons
    custom_buttons: Optional[List[Dict]] = None  # Custom button configs
)
```

### Custom Buttons

Add custom buttons to the toolbar:

```python
custom_buttons = [
    {
        'text': '📊',
        'tooltip': 'Analyze Data',
        'callback': self._analyze_data,
        'style': 'font-size: 14px;'
    },
    {
        'text': 'Import...',
        'tooltip': 'Import from File',
        'callback': self._import_file,
        'style': 'min-width: 60px; height: 28px;'
    }
]

grid.configure(columns=columns, custom_buttons=custom_buttons)
```

## Callbacks

### Set Custom Callbacks

```python
# Custom add behavior
def custom_add():
    # Show a dialog or perform custom logic
    pass

grid.set_add_callback(custom_add)

# Custom edit behavior
def custom_edit():
    row = grid.table.currentRow()
    # Edit the row in a custom dialog
    pass

grid.set_edit_callback(custom_edit)

# Custom remove behavior
def custom_remove():
    # Custom removal logic with validation
    pass

grid.set_remove_callback(custom_remove)

# Custom cell setup
def setup_cell(row, col, value):
    # Customize cell appearance or behavior
    if col == 0 and value.startswith("ERROR"):
        item = grid.table.item(row, col)
        item.setForeground(QColor("red"))

grid.set_cell_setup_callback(setup_cell)
```

## Signals

Connect to widget signals to respond to changes:

```python
# Data changed
grid.data_changed.connect(lambda: print("Data changed!"))

# Row added
grid.row_added.connect(lambda row: print(f"Row {row} added"))

# Rows removed
grid.row_removed.connect(lambda rows: print(f"Rows {rows} removed"))

# Row moved
grid.row_moved.connect(lambda from_row, to_row: print(f"Row moved from {from_row} to {to_row}"))
```

## Data Operations

### Adding Data

```python
# Add a row with data
row_index = grid.add_row(["Value 1", "Value 2", True])

# Add an empty row (will be filled with default values)
row_index = grid.add_row()
```

### Getting Data

```python
# Get data from a specific row
row_data = grid.get_row_data(row_index)

# Get all data
all_data = grid.get_all_data()
# Returns: [["Value 1", "Value 2", True], ["Value 3", "Value 4", False], ...]
```

### Setting Data

```python
# Set data for a specific row
grid.set_row_data(row_index, ["New Value 1", "New Value 2", False])
```

### Removing Data

```python
# Remove selected rows (with confirmation for multiple rows)
removed_rows = grid.remove_selected_rows()

# Remove without confirmation
removed_rows = grid.remove_selected_rows(confirm=False)

# Clear all data
grid.clear_data()
```

## Access to Table Widget

Direct access to the underlying QTableWidget:

```python
# Get current selection
selected_items = grid.table.selectedItems()
current_row = grid.table.currentRow()

# Programmatically select rows
grid.table.selectRow(5)

# Get row count
row_count = grid.table.rowCount()
```

## Examples

See `data_grid_examples.py` for complete working examples:

1. **KeysGridExample**: Managing database keys (PRIMARY, FOREIGN, UNIQUE)
2. **IndexesGridExample**: Managing database indexes with custom analysis button
3. **ColumnsGridExample**: Managing table columns with domains and stereotypes

### Running Examples

```python
from k2_designer.widgets.data_grid_examples import KeysGridExample

dialog = KeysGridExample()
if dialog.exec():
    keys_data = dialog.get_keys()
    print(keys_data)
```

## Use Cases

This widget is perfect for:

- **Database Keys Management**: PRIMARY, FOREIGN, UNIQUE keys
- **Index Management**: Table indexes with properties
- **Column Definitions**: Table columns with data types, domains, stereotypes
- **Configuration Grids**: Any tabular configuration data
- **Property Editors**: Editing object properties in a grid format
- **Data Entry Forms**: Structured data entry with validation

## Styling

The widget uses a consistent icon-based button style:

- **+** Add (green-ish, 16px, bold)
- **✎** Edit (14px)
- **✕** Remove (red-ish #c44, 14px, bold)
- **↑** Move Up (16px, bold)
- **↓** Move Down (16px, bold)

All buttons are 28×28px for consistent sizing.

## Integration with Existing Code

To migrate existing table code to use DataGridWidget:

1. Extract column definitions into `ColumnConfig` objects
2. Move toolbar buttons to the `configure()` call
3. Replace custom filter logic with built-in filters
4. Use callbacks for custom add/edit/remove behavior
5. Connect to signals instead of manual change tracking

## Thread Safety

The widget is not thread-safe. All operations should be performed on the Qt main thread.

## Performance

The widget handles thousands of rows efficiently. For very large datasets (10k+ rows), consider:

- Using filtering to limit visible rows
- Implementing virtual scrolling
- Lazy loading of data

## License

Dual-licensed under AGPL-3.0 and Commercial License.
See LICENSE file for details.

