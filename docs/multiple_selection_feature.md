# Multiple Table Selection in Diagram View

## Overview
The diagram view now supports selecting and manipulating multiple tables simultaneously, providing enhanced productivity for diagram layout and bulk operations.

## 🖱️ Selection Methods

### Single Selection
- **Click**: Select individual tables
- **Arrow Keys**: Navigate between tables (when focused)

### Multiple Selection
- **Ctrl+Click**: Add or remove tables from current selection
- **Ctrl+A**: Select all tables in the diagram
- **Escape**: Clear all selections
- **Rubber Band**: Drag to create selection rectangle (built-in PyQt6 feature)

### Visual Feedback
- **Selected Tables**: Blue border (3px thick)
- **Unselected Tables**: Black border (1px thick)
- **Selection Count**: Displayed in properties panel for multiple selections

## 📊 Properties Panel Integration

### Single Selection
When one table is selected, the properties panel shows:
- Full table details (columns, keys, indexes)
- Editable properties
- Save changes functionality

### Multiple Selection
When multiple tables are selected, the properties panel shows:
- **Selection Summary**: Total count and breakdown by type
- **Common Properties**: Shared characteristics across selected tables
- **Object List**: Table showing all selected tables with type and owner
- **Smart Analysis**: 
  - Mixed stereotypes indicator
  - Common owners detection
  - Total column count across all tables

### Mixed Object Types
When selecting different object types (tables, sequences), the panel:
- Shows type breakdown
- Displays common properties where applicable
- Lists all selected objects in a unified view

## 🔧 Context Menu Operations

### Single Table Context Menu
- **Edit Table**: Open table properties dialog
- **Remove from Diagram**: Remove table from current diagram

### Multiple Tables Context Menu
- **Selection Header**: Shows "X Tables Selected"
- **Alignment Operations**:
  - ⬅️ Align Left: Align all tables to leftmost position
  - ➡️ Align Right: Align all tables to rightmost position  
  - ⬆️ Align Top: Align all tables to topmost position
  - ⬇️ Align Bottom: Align all tables to bottommost position
- **Distribution Operations**:
  - ↔️ Distribute Horizontally: Even horizontal spacing
  - ↕️ Distribute Vertically: Even vertical spacing
- **Bulk Operations**:
  - Remove All from Diagram: Remove all selected tables

## ⌨️ Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Ctrl+A` | Select All Tables | Diagram focused |
| `Escape` | Clear Selection | Any time |
| `Ctrl+Click` | Toggle Selection | On table items |
| `Delete` | Remove Selected | Multiple selection |
| `Arrow Keys` | Navigate Selection | Single selection |

## 🔄 Integration with Other Components

### Object Browser Sync
- **Single Selection**: Object browser highlights corresponding item
- **Multiple Selection**: Object browser selection is cleared
- **No Selection**: Both components show empty state

### Main Window Coordination
- Selection changes propagate to properties panel
- Multiple selection signals update UI accordingly
- Legacy single-selection signals maintained for compatibility

## 🎯 Use Cases

### Diagram Layout
1. **Quick Alignment**: Select multiple tables and align them instantly
2. **Even Distribution**: Create professional layouts with consistent spacing
3. **Bulk Positioning**: Move groups of related tables together

### Content Management
1. **Bulk Removal**: Remove multiple tables from diagram at once
2. **Group Operations**: Perform operations on logically related tables
3. **Visual Organization**: Organize tables by stereotype or owner

### Analysis and Review
1. **Multi-Selection Summary**: Quick overview of selected table characteristics
2. **Common Properties**: Identify patterns across multiple tables
3. **Type Analysis**: Understand distribution of business vs technical tables

## 🛠️ Implementation Details

### Architecture
- **DiagramScene**: Manages selection state and emits selection signals
- **TableGraphicsItem**: Handles visual feedback and context menus
- **PropertiesPanel**: Displays single or multiple selection information
- **MainWindow**: Coordinates between components

### Signals and Slots
```python
# New signals for multiple selection
tables_selected = pyqtSignal(list)          # List of selected tables
multiple_selection_changed = pyqtSignal(list) # Propagated to main window

# Legacy single selection (maintained for compatibility)
table_selected = pyqtSignal(object)         # Single table or None
selection_changed = pyqtSignal(object)      # Single object selection
```

### Key Methods
- `_on_selection_changed()`: Handles PyQt6 selection changes
- `_show_multiple_selection_properties()`: Displays multi-selection UI
- `_align_selected_tables()`: Implements alignment operations
- `_distribute_selected_tables()`: Implements distribution operations

## 🧪 Testing Scenarios

### Basic Functionality
- [ ] Single table selection and deselection
- [ ] Multiple table selection with Ctrl+Click
- [ ] Select all with Ctrl+A
- [ ] Clear selection with Escape
- [ ] Rubber band selection

### Visual Feedback
- [ ] Selected tables show blue borders
- [ ] Unselected tables show black borders
- [ ] Selection changes update immediately

### Properties Panel
- [ ] Single selection shows full properties
- [ ] Multiple selection shows summary
- [ ] Common properties displayed correctly
- [ ] Object list shows all selected items

### Context Menus
- [ ] Single selection menu has Edit/Remove options
- [ ] Multiple selection menu has alignment options
- [ ] Alignment operations work correctly
- [ ] Distribution operations work correctly
- [ ] Bulk removal confirms and works

### Integration
- [ ] Object browser syncs with single selection
- [ ] Object browser clears on multiple selection
- [ ] Properties panel updates on selection changes
- [ ] Signals propagate correctly through application

## 🚀 Future Enhancements

### Potential Additions
1. **Shift+Click Range Selection**: Select ranges of tables
2. **Bulk Property Editing**: Edit common properties for multiple tables
3. **Selection Groups**: Save and restore selection groups
4. **Advanced Layouts**: Grid layout, circular arrangement
5. **Selection History**: Undo/redo for selection operations
6. **Keyboard Navigation**: Tab through selected items

### Performance Optimizations
1. **Large Diagram Handling**: Optimize for diagrams with many tables
2. **Selection Caching**: Cache selection state for performance
3. **Lazy Property Loading**: Load properties on-demand for large selections

## 💡 Best Practices

### For Users
1. **Use Ctrl+A** for quick selection of all tables
2. **Align Before Distributing** for best layout results
3. **Group Related Tables** before bulk operations
4. **Check Properties Panel** for selection confirmation

### For Developers
1. **Emit Both Signals**: Maintain legacy and new selection signals
2. **Handle Edge Cases**: Empty selections, single items, mixed types
3. **Provide Visual Feedback**: Immediate response to user actions
4. **Test Thoroughly**: Multiple selection has many interaction paths

## 🔍 Troubleshooting

### Common Issues
- **Selection Not Visible**: Check if items are actually selectable
- **Context Menu Missing**: Verify right-click on selected items
- **Properties Not Updating**: Check signal connections
- **Alignment Not Working**: Ensure multiple items are selected

### Debug Information
- Selection count is shown in properties panel header
- Console logs can be added to selection change handlers
- Visual borders provide immediate selection state feedback