# JSON Export/Import Feature

## Overview

The K2 Designer now supports exporting and importing project data in JSON format, in addition to the existing SQLite (`.k2p`) format. This provides better portability, readability, and integration with version control systems.

## Features

### Export to JSON
- Export your entire project to a human-readable JSON file
- Includes all project data: tables, columns, sequences, diagrams, domains, owners, stereotypes, and foreign keys
- Preserves diagram layouts and positions
- File extension: `.json`

### Import from JSON
- Load project data from a JSON file
- Automatically reconstructs all project objects and relationships
- Opens all diagrams that were saved in the JSON file
- Shows a summary of imported objects

## Usage

### From the Menu

#### Exporting to JSON
1. Open or create a project
2. Go to **File → Export to JSON...**
3. Choose a location and filename (defaults to `<project_name>.json`)
4. Click **Save**
5. A success message will confirm the export

#### Importing from JSON
1. Go to **File → Import from JSON...**
2. Select a `.json` file
3. Click **Open**
4. The project will be loaded and all diagrams will open automatically
5. A summary shows the number of imported objects

### Programmatic Usage

```python
from k2_designer.controllers.project_manager import ProjectManager

# Create or load a project
pm = ProjectManager()
project = pm.new_project("My Project")

# ... add tables, sequences, etc. ...

# Export to JSON
pm.save_project_to_json("/path/to/project.json")

# Import from JSON
imported_project = pm.load_project_from_json("/path/to/project.json")
```

## JSON Structure

The exported JSON file has the following structure:

```json
{
  "name": "Project Name",
  "description": "Project description",
  "last_active_diagram": "Main Diagram",
  "domains": [
    {
      "name": "ID_DOMAIN",
      "data_type": "NUMBER(10)",
      "comment": "Domain for IDs"
    }
  ],
  "owners": [
    {
      "name": "SCHEMA_NAME",
      "default_tablespace": "USERS",
      "temp_tablespace": "TEMP",
      "default_index_tablespace": "USERS",
      "editionable": false,
      "comment": "Schema comment"
    }
  ],
  "stereotypes": [
    {
      "name": "Business",
      "stereotype_type": "table",
      "description": "Business domain table",
      "background_color": "#4A90E2"
    }
  ],
  "tables": [
    {
      "name": "EMPLOYEES",
      "owner": "SCHEMA_NAME",
      "tablespace": "USERS",
      "stereotype": "Business",
      "color": "#4A90E2",
      "domain": null,
      "editionable": false,
      "comment": "Employee table",
      "columns": [
        {
          "name": "ID",
          "data_type": "NUMBER(10)",
          "nullable": false,
          "default": null,
          "comment": "Employee ID",
          "domain": "ID_DOMAIN",
          "stereotype": null
        }
      ],
      "keys": [
        {
          "name": "PK_EMPLOYEES",
          "columns": ["ID"]
        }
      ],
      "indexes": [],
      "partitioning": null
    }
  ],
  "sequences": [
    {
      "name": "EMP_SEQ",
      "owner": "SCHEMA_NAME",
      "start_with": 1,
      "increment_by": 1,
      "min_value": null,
      "max_value": null,
      "cache_size": 20,
      "cycle": false,
      "comment": "Employee sequence"
    }
  ],
  "foreign_keys": [
    {
      "source_key": "SCHEMA_NAME.EMPLOYEES.DEPT_ID",
      "target_table": "SCHEMA_NAME.DEPARTMENTS",
      "target_column": "ID"
    }
  ],
  "diagrams": [
    {
      "name": "Main Diagram",
      "description": "Main database diagram",
      "is_active": true,
      "zoom_level": 1.0,
      "scroll_x": 0.0,
      "scroll_y": 0.0,
      "items": [
        {
          "object_type": "table",
          "object_name": "SCHEMA_NAME.EMPLOYEES",
          "x": 100.0,
          "y": 100.0,
          "width": null,
          "height": null
        }
      ],
      "connections": []
    }
  ]
}
```

## Benefits

### 1. **Version Control Friendly**
- JSON files are text-based and work well with Git
- Easy to see diffs between versions
- Can review changes in pull requests

### 2. **Human Readable**
- Easy to inspect and understand project structure
- Can be manually edited if needed (use with caution)
- Good for documentation and sharing

### 3. **Portable**
- Share projects easily via email, cloud storage, or messaging
- No database driver required to view the file
- Cross-platform compatible

### 4. **Integration**
- Easy to integrate with CI/CD pipelines
- Can be parsed by other tools and scripts
- Enables automation and batch processing

### 5. **Backup and Recovery**
- Simple text-based backup format
- Easy to archive and restore
- Can be compressed efficiently

## Use Cases

### 1. **Collaboration**
Export your project to JSON and share it with team members via Git or file sharing.

### 2. **Version Control**
Store JSON files in Git repositories to track schema evolution over time.

### 3. **Documentation**
Use JSON export as a machine-readable documentation format.

### 4. **Migration**
Export from one environment and import into another.

### 5. **Backup**
Create periodic JSON backups of your database designs.

### 6. **Automation**
Write scripts to process or generate K2 Designer projects programmatically.

## Comparison: SQLite vs JSON

| Feature | SQLite (.k2p) | JSON (.json) |
|---------|---------------|--------------|
| **Format** | Binary database | Text file |
| **Size** | Smaller | Larger |
| **Human Readable** | No | Yes |
| **Version Control** | Poor | Excellent |
| **Editing** | Requires app | Text editor |
| **Performance** | Faster | Slower |
| **Primary Use** | Working format | Sharing/archiving |

## Best Practices

1. **Use SQLite for daily work**: It's faster and more compact
2. **Export to JSON for version control**: Commit JSON files to Git
3. **Export before major changes**: Create a JSON backup before restructuring
4. **Validate after import**: Check that all data imported correctly
5. **Use descriptive filenames**: e.g., `project_v2.1_2025-11-11.json`

## Technical Details

### Export Process
1. Converts the entire project object to a nested dictionary
2. Serializes all objects (tables, columns, diagrams, etc.)
3. Writes to JSON file with 2-space indentation
4. Uses UTF-8 encoding for international characters

### Import Process
1. Reads JSON file and parses into Python dictionary
2. Creates a new Project object
3. Reconstructs all objects in correct order (domains → owners → tables → etc.)
4. Rebuilds relationships (foreign keys, diagram items, etc.)
5. Validates data integrity

### Data Integrity
- All object relationships are preserved
- Diagram layouts and positions are maintained
- Colors, stereotypes, and metadata are retained
- Foreign key relationships are reconstructed

## Troubleshooting

### Export Failed
- **Cause**: No project loaded
- **Solution**: Open or create a project first

### Import Failed
- **Cause**: Invalid JSON format
- **Solution**: Ensure the file is valid JSON and follows the expected structure

### Missing Objects After Import
- **Cause**: JSON file may be corrupted or incomplete
- **Solution**: Use a validated backup or re-export from the original source

### Large File Size
- **Cause**: Complex projects with many objects
- **Solution**: This is normal; JSON is less compact than SQLite

## Testing

A test script is provided to verify JSON export/import functionality:

```bash
python3 test_json_export_import.py
```

This script:
- Creates a test project with sample data
- Exports it to JSON
- Imports it back
- Verifies data integrity
- Shows success/failure status

## Future Enhancements

Potential future improvements:
- Compression support for large projects
- Partial import/export (selected objects only)
- JSON schema validation
- Import merge (add to existing project)
- Export templates for specific use cases

## Conclusion

The JSON export/import feature provides flexibility and enhances collaboration capabilities in K2 Designer. Use it alongside the SQLite format to get the best of both worlds: fast performance for active work and easy sharing/versioning for collaboration.

