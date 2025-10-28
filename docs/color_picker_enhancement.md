# Color Picker Enhancement for Table Dialog

## Overview
The table dialog has been enhanced with a visual color picker that replaces the previous text-based color input field.

## Features

### 1. Visual Color Selection
- **Color Picker Button**: Click "Choose Color" to open PyQt6's native color dialog
- **Color Preview**: A visual preview square showing the currently selected color
- **Tooltip**: Displays the hex color code when hovering over the preview

### 2. Smart Color Management
- **Default Colors**: Automatically sets default colors based on table stereotype:
  - Business tables: Light blue (`#E3F2FD`)
  - Technical tables: Light purple (`#F3E5F5`)
- **Manual Override**: Once a color is manually selected, it won't be overridden by stereotype changes
- **Persistent Colors**: When editing existing tables, the current color is preserved and displayed

### 3. Automatic Color Updates
- **Stereotype Integration**: Changing the table stereotype automatically updates the color (unless manually set)
- **Visual Feedback**: Immediate visual feedback when colors change

## Implementation Details

### New Components
- `QPushButton` for opening the color dialog
- `QLabel` styled as a color preview square
- `QColorDialog` for color selection
- Color state tracking with `_color_manually_set` flag

### Methods Added
- `_choose_color()`: Opens the color picker dialog
- `_set_color(color_hex)`: Updates the color preview and internal state
- `_on_stereotype_changed()`: Handles automatic color updates when stereotype changes

### UI Layout
```
Color: [Choose Color] [Color Preview Square]
```

## Usage

### For New Tables
1. Select the desired stereotype (color auto-updates)
2. Optionally click "Choose Color" to select a custom color
3. The color preview shows the current selection

### For Existing Tables
1. Current table color is displayed in the preview
2. Click "Choose Color" to change the color
3. Color is preserved when saving changes

## Benefits
- **User-Friendly**: Visual color selection is more intuitive than hex codes
- **Consistent**: Uses native system color picker for familiar UX
- **Smart Defaults**: Automatic color assignment based on table purpose
- **Flexible**: Allows both automatic and manual color management

## Technical Notes
- Uses PyQt6's `QColorDialog.getColor()` for color selection
- Colors are stored as hex strings (e.g., "#FF5733")
- Color preview uses CSS styling for visual representation
- Backward compatible with existing table data