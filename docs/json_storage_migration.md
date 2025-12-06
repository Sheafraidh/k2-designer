# JSON Storage Migration

## Overview

K2 Designer has been migrated from SQLite-based storage to JSON-based storage for project files (.k2p). This change brings several benefits while maintaining backward compatibility through a migration tool.

## Changes Made

### 1. Project Manager (`src/k2_designer/controllers/project_manager.py`)

**Removed:**
- All SQLite-related imports (`import sqlite3`)
- `_create_database_schema()` method (~150 lines)
- `_migrate_database_schema()` method (~30 lines)
- `_clear_database()` method (~10 lines)
- `_save_project_data()` method (~150 lines)
- `_load_project_data()` method (~200 lines)
- `save_project_to_json()` method (redundant)
- `load_project_from_json()` method (redundant)

**Modified:**
- `save_project()`: Now directly saves to JSON format
- `load_project()`: Now directly loads from JSON format

**Result:** Reduced from ~1046 lines to ~387 lines (60% reduction)

### 2. Main Window (`src/k2_designer/views/main_window.py`)

**Removed:**
- Export to JSON menu action
- Import from JSON menu action
- `_export_to_json()` method
- `_import_from_json()` method

**Reason:** JSON is now the native format, so separate export/import is unnecessary.

### 3. README.md

**Updated:**
- Changed storage description from "SQLite (.k2p)" to "JSON (.k2p)"
- Removed "JSON Export/Import" from features (now native)
- Added "Project Storage" section explaining JSON benefits
- Added migration instructions for old SQLite files
- Removed `sqlite3` from dependencies

## Benefits of JSON Storage

### 1. **Version Control Friendly**
- Human-readable text format
- Easy to diff and merge in Git
- Clear visibility of changes in commits

### 2. **Portable**
- Works across different operating systems
- No dependency on SQLite library versions
- Plain text is universally compatible

### 3. **Future-Proof**
- No binary format lock-in
- Easy to parse with any JSON library
- Simple schema evolution

### 4. **Debuggable**
- Can inspect files in any text editor
- Easy to manually fix corrupted data
- Better error messages

### 5. **Lightweight**
- No SQLite library overhead
- Simpler codebase (60% less code)
- Faster for small-to-medium projects

## File Format

Projects are saved as JSON with the `.k2p` extension. Example structure:

```json
{
  "name": "My Project",
  "description": "Project description",
  "last_active_diagram": "Main Diagram",
  "domains": [...],
  "owners": [...],
  "tables": [
    {
      "name": "USERS",
      "owner": "APP_OWNER",
      "columns": [
        {
          "name": "ID",
          "data_type": "NUMBER(18,0)",
          "nullable": false
        }
      ],
      "keys": [...],
      "indexes": [...]
    }
  ],
  "sequences": [...],
  "foreign_keys": [...],
  "diagrams": [...]
}
```

## Migration Guide

### For Users with Existing SQLite Files

A migration script is provided to convert old SQLite `.k2p` files to JSON format:

```bash
# Migrate a single file
python migrate_sqlite_to_json.py old_project.k2p new_project.k2p

# Migrate all .k2p files in current directory
python migrate_sqlite_to_json.py --all
```

The migration script:
1. Detects SQLite files automatically
2. Loads all data from SQLite database
3. Saves to JSON format
4. Preserves all project data including:
   - Domains, owners, tables, sequences
   - Columns with all attributes
   - Keys, indexes, partitioning
   - Foreign key relationships
   - Diagrams with positions and connections
   - Stereotypes and color settings

### Migration Script Features

- **Automatic Detection**: Checks file header to identify SQLite files
- **Batch Processing**: Can migrate multiple files at once with `--all`
- **Data Validation**: Reports counts of migrated objects
- **Error Handling**: Provides clear error messages if migration fails

## Testing

### Test Script

A test script (`test_json_format.py`) verifies:
- Creating new projects
- Saving to JSON format
- Loading from JSON format
- Data integrity (all objects preserved)
- File format validation

Run the test:
```bash
python test_json_format.py
```

Expected output:
```
🧪 Testing JSON save/load functionality...
📝 Saving project to test_project.k2p...
✅ Project saved successfully
🔍 Verifying file format...
✅ File is valid JSON
📂 Loading project from test_project.k2p...
✅ Project loaded successfully
✅ All verifications passed!
```

## Backward Compatibility

### Old Files

Old SQLite `.k2p` files cannot be directly opened in the new version. Users must:
1. Use the migration script to convert files to JSON
2. Keep the SQLite version as backup if needed
3. Use the new JSON files going forward

### Why No Automatic Migration?

Automatic migration was not implemented to:
- Avoid accidental data loss
- Give users control over the migration process
- Allow keeping both formats during transition
- Prevent silent failures on corrupted files

## Performance Considerations

### JSON vs SQLite

**JSON Advantages:**
- Faster for small-to-medium projects (<1000 tables)
- Simpler codebase, easier to maintain
- No database overhead

**SQLite Advantages (not used anymore):**
- Better for very large projects (>1000 tables)
- Incremental saves possible
- Query optimization available

**Decision:** For K2 Designer's target use case (database design projects with typically <100 tables), JSON provides better developer experience and maintainability.

## Code Quality Improvements

### Lines of Code Reduction

| File | Before | After | Reduction |
|------|--------|-------|-----------|
| project_manager.py | 1046 | 387 | 63% |
| main_window.py | ~1500 | ~1430 | 5% |

### Complexity Reduction

- Removed database schema management
- Removed migration logic
- Removed SQL query construction
- Simplified error handling
- Clearer data flow

## Future Considerations

### Potential Enhancements

1. **Compression**: Add gzip compression for large projects
2. **Encryption**: Optional encryption for sensitive data
3. **Version Field**: Add format version for future migrations
4. **Partial Loading**: Load large projects incrementally
5. **Auto-backup**: Create backups before saving

### Schema Evolution

JSON makes schema evolution easier:
- Add new fields with default values
- Gracefully handle missing fields
- Version-specific loaders
- Clear migration paths

## Conclusion

The migration to JSON storage simplifies K2 Designer's codebase while providing a more maintainable, portable, and version-control-friendly storage format. The included migration script ensures users can seamlessly transition from the old SQLite format to the new JSON format.

## Files Created

1. **migrate_sqlite_to_json.py** - Migration script for converting old files
2. **test_json_format.py** - Test script for validating JSON functionality
3. **docs/json_storage_migration.md** - This documentation

## Files Modified

1. **src/k2_designer/controllers/project_manager.py** - Removed SQLite, simplified to JSON-only
2. **src/k2_designer/views/main_window.py** - Removed export/import menu items
3. **README.md** - Updated documentation to reflect JSON storage

## Migration Checklist

For users upgrading:

- [ ] Backup all existing `.k2p` files
- [ ] Run migration script on all projects
- [ ] Verify migrated projects open correctly
- [ ] Test saving and loading migrated projects
- [ ] Archive old SQLite files (optional)
- [ ] Update any automation/scripts to use new format

