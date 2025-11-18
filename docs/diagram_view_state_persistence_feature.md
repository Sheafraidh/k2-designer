# Diagram View State Persistence Feature

## Overview
The diagram view state (zoom level and scroll position) is now automatically saved and restored when you work with diagrams. This means tables will appear exactly where you left them, at the same zoom level and scroll position.

## Implementation Date
November 18, 2025

## Files Modified

### 1. `src/k2_designer/views/diagram_view.py`
Added methods to save and restore view state:
- `save_view_state()` - Saves current zoom level and scroll position to the diagram model
- `restore_view_state()` - Restores saved zoom level and scroll position when diagram is opened
- `_apply_scroll_position()` - Helper method to apply scroll position after scene is rendered

### 2. `src/k2_designer/views/main_window.py`
Integrated view state management into the application workflow:
- Calls `restore_view_state()` when opening a diagram
- Calls `save_view_state()` when closing a diagram tab
- Saves all open diagram view states before saving the project
- Saves all diagram view states when closing the application
- Added `_save_all_diagram_view_states()` helper method

### 3. `src/k2_designer/models/diagram.py` (No changes needed)
The Diagram model already had support for storing:
- `zoom_level` - The zoom/scale factor (default: 1.0)
- `scroll_x` - Horizontal scroll position (default: 0.0)
- `scroll_y` - Vertical scroll position (default: 0.0)

These values are automatically serialized in `to_dict()` and deserialized in `from_dict()`.

## How It Works

### When Opening a Diagram
1. User opens a diagram (from Object Browser or menu)
2. `DiagramView` is created with the diagram
3. `restore_view_state()` is called immediately
4. The saved zoom level is applied to the graphics view
5. After a short delay (10ms), the scroll position is applied

### When Closing a Diagram Tab
1. User clicks the close button on a diagram tab
2. `save_view_state()` is called on the diagram view
3. Current zoom level is read from the graphics view transform
4. Current scroll positions are read from the scrollbars
5. Values are saved to the diagram model
6. Tab is closed

### When Saving the Project
1. User saves the project (Save or Save As)
2. `_save_all_diagram_view_states()` is called
3. All currently open diagram tabs have their view states saved
4. Project is serialized to JSON (including diagram view states)
5. File is written to disk

### When Closing the Application
1. User closes the application
2. `closeEvent()` is triggered
3. All diagram view states are saved
4. Last opened project path is saved
5. Application exits

## User Experience

### Before This Feature
- Diagrams always opened at default zoom (1.0x) and scroll position (0, 0)
- Users had to manually zoom and pan to find their tables each time
- Work position was lost between sessions

### After This Feature
- Diagrams open exactly as you left them
- Zoom level is preserved
- Scroll position is preserved
- Consistent experience across sessions

## Technical Details

### Zoom Level Storage
The zoom level is stored as the horizontal scale factor (m11) of the QGraphicsView's transformation matrix:
```python
transform = self.graphics_view.transform()
self.diagram.zoom_level = transform.m11()
```

### Scroll Position Storage
Scroll positions are read from the horizontal and vertical scrollbars:
```python
horizontal_scrollbar = self.graphics_view.horizontalScrollBar()
vertical_scrollbar = self.graphics_view.verticalScrollBar()
self.diagram.scroll_x = horizontal_scrollbar.value()
self.diagram.scroll_y = vertical_scrollbar.value()
```

### Restoration Timing
Scroll position restoration uses `QTimer.singleShot(10, ...)` to ensure the scene is fully rendered before applying the scroll position. This prevents race conditions where the scrollbars aren't ready yet.

## Testing

### Test Script
`test_diagram_view_state.py` - Verifies serialization and deserialization of view state

### Test Results
```
✓ Initial state is correct (zoom: 1.0, scroll: 0.0, 0.0)
✓ Modified state is saved (zoom: 1.5, scroll: 100.0, 200.0)
✓ Serialization includes view state
✓ Deserialization restores view state correctly
```

## Example Scenarios

### Scenario 1: Working on a Large Diagram
1. Open a diagram with many tables
2. Zoom in to 200% to focus on specific tables
3. Pan to a specific area of interest
4. Save the project
5. Close the application
6. **Result**: When reopening, the diagram shows the same view at 200% zoom

### Scenario 2: Multiple Open Diagrams
1. Open three diagrams in tabs
2. Set different zoom levels for each (1.0x, 1.5x, 2.0x)
3. Pan each to different positions
4. Save the project
5. Close all tabs
6. Reopen each diagram
7. **Result**: Each diagram opens with its individual zoom and position

### Scenario 3: Switching Between Diagrams
1. Open "HR Schema Overview" diagram
2. Zoom in and pan to EMPLOYEES table
3. Switch to another diagram tab
4. Edit some tables
5. Switch back to "HR Schema Overview"
6. **Result**: The EMPLOYEES table is still visible at the same zoom level

## Benefits

✅ **Saves Time**: No need to manually zoom and pan every time  
✅ **Maintains Context**: Work exactly where you left off  
✅ **Professional UX**: Matches behavior of modern diagramming tools  
✅ **Automatic**: No user action required  
✅ **Reliable**: State is saved on multiple occasions (close tab, save project, exit app)

## Edge Cases Handled

1. **Diagram with no saved state**: Uses defaults (zoom: 1.0, scroll: 0, 0)
2. **Invalid scroll values**: Scrollbars constrain to valid ranges
3. **Extreme zoom levels**: Graphics view handles naturally
4. **Scene not ready**: Timer delay ensures proper rendering before scroll

## Future Enhancements (Optional)

Potential improvements for future versions:
- Save selected items (restore selection state)
- Save viewport center instead of scroll values (more intuitive)
- Allow resetting view state to defaults (right-click menu option)
- Show zoom level percentage in UI (e.g., "150%")
- Keyboard shortcuts for zoom levels (1, 2, 3 keys for 100%, 200%, 300%)

## Backward Compatibility

✅ **Fully backward compatible**
- Old project files without view state values will use defaults
- The `Diagram.from_dict()` method uses `.get('zoom_level', 1.0)` with defaults
- No migration needed for existing projects

## Summary

This feature significantly improves the user experience by automatically preserving and restoring the diagram view state (zoom and scroll position). Users can now work on diagrams without losing their context between sessions, making the tool more professional and efficient to use.

