# Project Settings Feature

## Overview

K2 Designer now includes a comprehensive project settings dialog that allows you to configure global settings for your database design projects. These settings are saved with your project and can be exported/imported via JSON.

## Features

### Settings Available

1. **Author** - Name or organization responsible for the project
2. **Template Directory** - Directory containing Jinja2 template files for SQL generation
3. **Output Directory** - Default directory where generated SQL files will be saved

### Key Capabilities

✅ **Persistent Storage** - Settings are saved in both SQLite (.k2p) and JSON formats  
✅ **Per-Project Configuration** - Each project can have its own settings  
✅ **JSON Export/Import** - Settings are included in JSON exports  
✅ **User-Friendly UI** - Easy-to-use dialog with browse buttons  
✅ **Default Values** - Empty by default, no mandatory fields  

---

## Usage

### Opening Project Settings

**Via Menu:**
1. Open or create a project
2. Go to **Tools → Project Settings...**
3. The Project Settings dialog opens

**Keyboard Shortcut:**
- Menu access key: `Alt+T` then `S`

### Configuring Settings

#### Author Field
- Enter your name or organization name
- Used for documentation and SQL comments
- Example: "John Doe" or "Acme Corporation"

#### Template Directory
- Click **Browse...** to select a directory
- Should contain `.j2` (Jinja2) template files
- Used for custom SQL generation templates
- Example: `/home/user/k2-templates`

#### Output Directory
- Click **Browse...** to select a directory
- Default location for generated SQL scripts
- Used by the SQL generation dialog
- Example: `/home/user/generated-sql`

### Saving Settings

1. Configure the desired settings
2. Click **OK** to apply and save
3. Settings are immediately saved to the project
4. A confirmation message appears in the status bar

### Canceling Changes

- Click **Cancel** to discard changes
- The dialog closes without saving

---

## Storage and Persistence

### SQLite Storage (.k2p files)

Settings are stored in the `project_settings` table:

```sql
CREATE TABLE project_settings (
    id INTEGER PRIMARY KEY,
    author TEXT,
    template_directory TEXT,
    output_directory TEXT
)
```

**When Saved:**
- Every time you save the project (Ctrl+S or File → Save)
- When you save as a new project (File → Save As...)

**When Loaded:**
- Automatically when you open a project (File → Open)

### JSON Storage (.json files)

Settings are included in the JSON export as a top-level `settings` object:

```json
{
  "name": "My Project",
  "description": "...",
  "settings": {
    "author": "John Doe",
    "template_directory": "/path/to/templates",
    "output_directory": "/path/to/output"
  },
  "tables": [...],
  "sequences": [...]
}
```

**When Exported:**
- File → Export to JSON...
- Settings are automatically included

**When Imported:**
- File → Import from JSON...
- Settings are automatically loaded

---

## Use Cases

### 1. Team Collaboration

**Scenario:** Multiple developers working on the same database design

```
Settings:
- Author: "Database Team"
- Template Directory: "/shared/templates"
- Output Directory: "/project/sql-scripts"
```

**Benefits:**
- Consistent SQL generation across the team
- Shared template location
- Standardized output location

### 2. Custom SQL Templates

**Scenario:** Organization with specific SQL standards

```
Settings:
- Author: "Acme Corp"
- Template Directory: "/templates/acme-standards"
- Output Directory: "/builds/sql"
```

**Benefits:**
- Custom templates for company standards
- Automated compliance with SQL guidelines
- Centralized template management

### 3. Multiple Projects

**Scenario:** Designer working on multiple database projects

```
Project A Settings:
- Author: "Client A Team"
- Template Directory: "/templates/client-a"
- Output Directory: "/projects/client-a/sql"

Project B Settings:
- Author: "Client B Team"
- Template Directory: "/templates/client-b"
- Output Directory: "/projects/client-b/sql"
```

**Benefits:**
- Different templates per client
- Organized output directories
- Easy project switching

---

## Integration with Other Features

### SQL Generation Dialog

The **Output Directory** setting is used as the default location in the SQL generation dialog:

1. Go to Tools → Generate SQL
2. The output directory is pre-filled from settings
3. Can be overridden for one-time generation

### Template System

The **Template Directory** setting points to custom Jinja2 templates:

- Templates override default SQL generation
- Allows organization-specific SQL formatting
- Supports custom header comments with author name

### JSON Export/Import

Settings are automatically included in:
- Project exports (File → Export to JSON)
- Project imports (File → Import from JSON)
- Version control workflows

---

## Technical Details

### Data Structure

In Python/Project model:
```python
project.settings = {
    'author': '',                    # String
    'template_directory': '',        # String (file path)
    'output_directory': ''          # String (file path)
}
```

### Default Values

All settings default to empty strings:
```python
{
    'author': '',
    'template_directory': '',
    'output_directory': ''
}
```

### Validation

- No validation is performed (all fields are optional)
- Empty values are perfectly valid
- Invalid paths don't prevent saving
- Path validation happens at usage time (SQL generation)

### Database Schema

**Table:** `project_settings`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `author` | TEXT | Author name |
| `template_directory` | TEXT | Template path |
| `output_directory` | TEXT | Output path |

---

## Dialog UI Layout

```
┌─────────────────────────────────────────────────────┐
│  Project Settings                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  General                                            │
│  ┌───────────────────────────────────────────────┐ │
│  │ Author: [_____________________________]       │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Paths                                              │
│  ┌───────────────────────────────────────────────┐ │
│  │ Template Directory:                           │ │
│  │ [________________________________] [Browse...] │ │
│  │ 📁 This directory should contain .j2 files    │ │
│  │                                               │ │
│  │ Output Directory:                             │ │
│  │ [________________________________] [Browse...] │ │
│  │ 💾 Generated SQL scripts saved here           │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ℹ️ Settings are saved with project and can be     │
│     exported/imported via JSON                      │
│                                                     │
│  [  OK  ]  [Cancel]                                 │
└─────────────────────────────────────────────────────┘
```

---

## Testing

A comprehensive test script is provided: `test_project_settings.py`

**Run tests:**
```bash
python3 test_project_settings.py
```

**Tests performed:**
1. ✅ Create project with settings
2. ✅ Save to SQLite and load back
3. ✅ Export to JSON and import back
4. ✅ Verify default values
5. ✅ Verify data integrity

**Expected output:**
```
🧪 Testing Project Settings Feature

1️⃣  Creating test project with settings...
   ✓ Project created with settings
2️⃣  Testing SQLite save/load...
   ✓ Settings match original!
3️⃣  Testing JSON export/import...
   ✓ Settings match original!
4️⃣  Testing default settings...
   ✓ Default settings are empty

✅ All project settings tests passed!
```

---

## Files Modified/Created

### New Files:
- `src/k2_designer/dialogs/project_settings_dialog.py` - Settings dialog UI
- `test_project_settings.py` - Test script

### Modified Files:
- `src/k2_designer/models/project.py` - Added settings property
- `src/k2_designer/views/main_window.py` - Added menu item and handler
- `src/k2_designer/controllers/project_manager.py` - Added save/load logic
- `src/k2_designer/dialogs/__init__.py` - Exported new dialog

### Database Changes:
- New table: `project_settings` in .k2p files

### JSON Format Changes:
- New field: `"settings"` in .json exports

---

## Backwards Compatibility

### Opening Old Projects

✅ **SQLite (.k2p) files:**
- Old projects without settings table work fine
- Settings default to empty values
- No migration errors

✅ **JSON files:**
- Old JSON exports without settings field work fine
- Settings default to empty values
- No import errors

### Saving Compatibility

✅ **Forward compatible:**
- Projects saved with settings can be opened in newer versions

⚠️ **Not backward compatible:**
- Projects with settings table might cause issues in older K2 Designer versions
- JSON exports with settings field work in older versions (field is ignored)

---

## Future Enhancements

Potential improvements for future versions:

1. **More Settings**
   - Database connection defaults
   - Code generation preferences
   - Diagram display preferences

2. **Validation**
   - Check if template directory exists
   - Validate template files (.j2)
   - Check write permissions for output directory

3. **Templates Management**
   - Browse and preview templates
   - Template editor integration
   - Template marketplace/sharing

4. **Output Management**
   - Auto-create output directory
   - Organize by schema/owner
   - Timestamp-based folders

5. **Profiles**
   - Multiple setting profiles
   - Quick switch between profiles
   - Import/export profiles separately

---

## Troubleshooting

### Settings Not Saving

**Problem:** Changes don't persist after closing and reopening

**Solutions:**
1. Make sure to save the project (Ctrl+S)
2. Check file permissions on .k2p file
3. Verify no errors in status bar

### Browse Button Not Working

**Problem:** Browse dialog doesn't open

**Solutions:**
1. Check you have a project open
2. Verify file system permissions
3. Try typing path manually

### Settings Lost After JSON Import

**Problem:** Settings are empty after importing JSON

**Solutions:**
1. Check if JSON file contains "settings" field
2. Verify JSON is valid (use JSON validator)
3. Re-export from original project

---

## Conclusion

The Project Settings feature provides a centralized location for managing project-wide configuration. It integrates seamlessly with the existing save/load and export/import functionality, making it easy to maintain consistent settings across projects and teams.

**Key Points:**
- ✅ Easy to use dialog interface
- ✅ Persistent storage in both SQLite and JSON
- ✅ Backwards compatible with existing projects
- ✅ Fully tested and validated
- ✅ Ready for production use

