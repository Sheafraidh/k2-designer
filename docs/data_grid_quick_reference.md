# DataGridWidget Quick Reference

## Import

```python
from k2_designer.widgets import DataGridWidget, ColumnConfig
from PyQt6.QtWidgets import QHeaderView
```

## Create and Configure

```python
grid = DataGridWidget()

columns = [
    ColumnConfig(
        name="Column Name",
        width=150,
        resize_mode=QHeaderView.ResizeMode.Interactive,  # or Fixed, Stretch
        editor_type="text",      # "text", "checkbox", "combobox"
        editor_options={},       # {'items': [...]} for combobox
        filter_type="text",      # "text", "combobox", "none"
        filter_options={}        # {'items': [...], 'editable': True}
    ),
]

grid.configure(
    columns=columns,
    show_filters=True,
    show_add_button=True,
    show_edit_button=True,
    show_remove_button=True,
    show_move_buttons=True,
    custom_buttons=[
        {'text': '⚙️', 'tooltip': 'Settings', 'callback': my_func}
    ]
)
```

## Add Data

```python
# Add single row
row_idx = grid.add_row(["Value1", "Value2", True])

# Add multiple rows
for item in items:
    grid.add_row([item.name, item.type, item.active])
```

## Get Data

```python
# Get single row
row_data = grid.get_row_data(row_index)  # Returns: ["Value1", "Value2", True]

# Get all data
all_data = grid.get_all_data()  # Returns: [["Row1..."], ["Row2..."], ...]
```

## Set Data

```python
# Set single row
grid.set_row_data(row_index, ["NewValue1", "NewValue2", False])

# Clear all
grid.clear_data()
```

## Remove Data

```python
# Remove selected rows (with confirmation)
removed = grid.remove_selected_rows()

# Remove without confirmation
removed = grid.remove_selected_rows(confirm=False)
```

## Callbacks

```python
# Custom add
grid.set_add_callback(lambda: my_add_dialog())

# Custom edit
grid.set_edit_callback(lambda: my_edit_dialog())

# Custom remove
grid.set_remove_callback(lambda: my_custom_remove())

# Custom cell setup
def setup_cell(row, col, value):
    if value == "ERROR":
        item = grid.table.item(row, col)
        item.setForeground(QColor("red"))

grid.set_cell_setup_callback(setup_cell)
```

## Signals

```python
grid.data_changed.connect(lambda: print("Data changed"))
grid.row_added.connect(lambda row: print(f"Row {row} added"))
grid.row_removed.connect(lambda rows: print(f"Rows {rows} removed"))
grid.row_moved.connect(lambda from_row, to_row: print(f"Moved {from_row} to {to_row}"))
```

## Access Table Widget

```python
# Direct access to underlying QTableWidget
table = grid.table

# Current row/selection
current_row = table.currentRow()
selected_items = table.selectedItems()

# Row count
count = table.rowCount()
```

## Editor Types

### Text
```python
ColumnConfig(name="Name", editor_type="text")
```

### Checkbox
```python
ColumnConfig(name="Active", editor_type="checkbox")
# Data: True/False
```

### Combobox
```python
ColumnConfig(
    name="Type",
    editor_type="combobox",
    editor_options={'items': ['Type A', 'Type B', 'Type C']}
)
```

## Filter Types

### Text Filter
```python
ColumnConfig(name="Name", filter_type="text")
```

### Combobox Filter
```python
ColumnConfig(
    name="Type",
    filter_type="combobox",
    filter_options={
        'items': ['All', 'Type A', 'Type B'],
        'editable': True
    }
)
```

### No Filter
```python
ColumnConfig(name="ID", filter_type="none")
```

## Resize Modes

```python
from PyQt6.QtWidgets import QHeaderView

# User can resize
QHeaderView.ResizeMode.Interactive

# Fixed width
QHeaderView.ResizeMode.Fixed

# Stretch to fill space
QHeaderView.ResizeMode.Stretch
```

## Common Patterns

### Keys Grid
```python
columns = [
    ColumnConfig("Name", 150, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
    ColumnConfig("Type", 120, QHeaderView.ResizeMode.Fixed, "combobox",
                {'items': ['PRIMARY', 'FOREIGN', 'UNIQUE']}, "combobox",
                {'items': ['All', 'PRIMARY', 'FOREIGN', 'UNIQUE']}),
    ColumnConfig("Columns", 200, QHeaderView.ResizeMode.Stretch, "text", {}, "text", {}),
]
```

### Indexes Grid
```python
columns = [
    ColumnConfig("Name", 150, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
    ColumnConfig("Columns", 200, QHeaderView.ResizeMode.Stretch, "text", {}, "text", {}),
    ColumnConfig("Unique", 80, QHeaderView.ResizeMode.Fixed, "checkbox", {}, "combobox",
                {'items': ['All', 'Yes', 'No']}),
]
```

### Columns Grid
```python
columns = [
    ColumnConfig("Name", 120, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
    ColumnConfig("Data Type", 130, QHeaderView.ResizeMode.Interactive, "text", {}, "text", {}),
    ColumnConfig("Nullable", 80, QHeaderView.ResizeMode.Fixed, "checkbox", {}, "combobox",
                {'items': ['All', 'Nullable', 'Not Nullable']}),
    ColumnConfig("Comment", 150, QHeaderView.ResizeMode.Stretch, "text", {}, "text", {}),
]
```

## Tips

- Use `Interactive` resize mode for columns users might want to adjust
- Use `Fixed` for narrow columns (checkboxes, icons)
- Use `Stretch` for the last or widest column (comments, descriptions)
- Add "All" as first item in combobox filters
- Use icon buttons (emoji) for compact custom buttons
- Connect to `data_changed` signal to track modifications
- Use callbacks for complex add/edit operations requiring dialogs
- Access `grid.table` for direct QTableWidget operations when needed

## Files

- **Widget**: `src/k2_designer/widgets/data_grid_widget.py`
- **Examples**: `src/k2_designer/widgets/data_grid_examples.py`
- **Documentation**: `src/k2_designer/widgets/README.md`
- **Integration Guide**: `docs/data_grid_integration.md`

