# Template Grouping and Management Feature

## Overview
Implemented a comprehensive template grouping system based on directory structure with metadata headers for name and description. Templates are organized in subdirectories and can be selected per-object in the SQL generation dialog.

## Implementation Date
November 18, 2025

## Files Created

### 1. Template Manager
**File:** `src/k2_designer/controllers/template_manager.py`
- Scans templates directory recursively
- Parses template metadata from Jinja2 comment headers
- Organizes templates by directory structure
- Provides methods to query templates by group and object type

### 2. New Template Structure
```
templates/
├── tables/
│   ├── create_table.sql.j2          # Standard DDL
│   ├── archive_table.sql.j2         # Creates archive table
│   └── audit_trigger.sql.j2         # Audit trigger
├── sequences/
│   └── create_sequence.sql.j2       # Standard sequence
└── users/
    └── create_user.sql.j2           # Standard user creation
```

### 3. Template Files with Metadata Headers
Each template now has a header like:
```jinja2
{#
name: Create Table DDL
description: Standard CREATE TABLE statement with columns, constraints, and indexes
object_type: table
#}
```

## Files Modified

### 1. `generate_dialog.py`
- Added template tree view on the left side
- Horizontal splitter (30% templates, 70% objects)
- Template selection per object
- Updated SqlGeneratorWorker to use selected templates
- Dynamic template enabling based on object type

## Features

### 1. Directory-Based Organization
- Templates organized in subdirectories (`tables/`, `sequences/`, `users/`)
- Each directory shown as a group in the template tree
- Easy to add new groups by creating new directories

### 2. Template Metadata
Template headers support:
- **name**: Display name in UI
- **description**: Tooltip/description text
- **object_type**: table, sequence, or user (for filtering)

### 3. Template Selection
- Tree view on the left shows all available templates
- Organized by directory groups
- Check multiple templates per object
- Templates filtered by selected object type
- Visual feedback (grayed out for incompatible types)

### 4. Multiple Templates Per Object
Users can select multiple templates for a single object:
- Create table DDL
- Archive table
- Audit trigger
- All generated from one source table

### 5. Flexible Generation
- Filenames include template name: `tablename_archive_table.sql`
- Can generate different scripts for different objects
- Fallback to default templates if none selected

## Usage Example

### For Tables:
1. Select a table in the "Tables" tab
2. In the template tree, check:
   - ✅ Create Table DDL
   - ✅ Archive Table
   - ✅ Audit Trigger
3. Generate SQL
4. Result: 3 files generated:
   - `employees_create_table.sql`
   - `employees_archive_table.sql`
   - `employees_audit_trigger.sql`

### For Sequences:
1. Select a sequence in the "Sequences" tab
2. Template tree shows only sequence templates
3. Check desired template(s)
4. Generate SQL

## Template Metadata Format

```jinja2
{#
name: Template Name
description: What this template does
object_type: table|sequence|user
#}
-- Your SQL template content here
```

## Adding New Templates

### 1. Create Template File
```bash
# For tables
templates/tables/my_custom_script.sql.j2

# For sequences
templates/sequences/my_sequence_script.sql.j2

# For users
templates/users/my_user_script.sql.j2
```

### 2. Add Metadata Header
```jinja2
{#
name: My Custom Script
description: Does something awesome
object_type: table
#}
```

### 3. Write Template Content
Use Jinja2 syntax with context variables:
- Tables: `{{ table.name }}`, `{{ table.owner }}`, `{{ table.columns }}`
- Sequences: `{{ sequence.name }}`, `{{ sequence.owner }}`
- Users: `{{ owner.name }}`, `{{ owner.default_tablespace }}`

### 4. Restart Application
Templates are scanned on dialog creation.

## Example Templates

### Archive Table Template
```jinja2
{#
name: Archive Table
description: Creates an archive table with the same structure plus archiving columns
object_type: table
#}
CREATE TABLE {{ table.owner }}.{{ table.name }}_ARCHIVE (
{%- for column in table.columns %}
    {{ column.name }} {{ column.data_type }},
{%- endfor %}
    ARCHIVE_DATE DATE DEFAULT SYSDATE NOT NULL,
    ARCHIVE_USER VARCHAR2(100) DEFAULT USER NOT NULL,
    ARCHIVE_REASON VARCHAR2(500)
);
```

### Audit Trigger Template
```jinja2
{#
name: Audit Trigger
description: Creates an audit trigger that logs all changes
object_type: table
#}
CREATE OR REPLACE TRIGGER {{ table.owner }}.{{ table.name }}_AUDIT_TRG
    BEFORE INSERT OR UPDATE OR DELETE ON {{ table.owner }}.{{ table.name }}
    FOR EACH ROW
BEGIN
    -- Audit logic here
END;
/
```

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Generate SQL Scripts                                         │
├─────────────────────────────────────────────────────────────┤
│ Output Directory: [/path/to/output          ] [Browse...]   │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────────┬─────────────────────────────────────┐  │
│ │ Available        │ Select Objects to Generate          │  │
│ │ Templates        │                                     │  │
│ │                  │ ┌─────────────────────────────────┐ │  │
│ │ ▼ tables         │ │ [Tables][Sequences][Users]      │ │  │
│ │   ☐ Create Table │ │                                 │ │  │
│ │   ☐ Archive Table│ │ ☐ EMPLOYEES (HR, 11 columns)    │ │  │
│ │   ☐ Audit Trigger│ │ ☐ DEPARTMENTS (HR, 4 columns)   │ │  │
│ │ ▼ sequences      │ │ ☐ JOBS (HR, 4 columns)          │ │  │
│ │   ☐ Create Seq   │ │                                 │ │  │
│ │ ▼ users          │ └─────────────────────────────────┘ │  │
│ │   ☐ Create User  │                                     │  │
│ └──────────────────┴─────────────────────────────────────┘  │
│ [Select All] [Select None]      [Generate SQL] [Close]     │
└─────────────────────────────────────────────────────────────┘
```

## Benefits

### For Users
✅ Visual template selection  
✅ Multiple scripts per object  
✅ Organized by type  
✅ Easy to understand  
✅ Descriptive names  

### For Developers
✅ Easy to add new templates  
✅ Organized directory structure  
✅ Metadata in template files  
✅ No code changes needed  
✅ Jinja2 templating power  

### For Teams
✅ Shared template library  
✅ Standardized scripts  
✅ Customizable per project  
✅ Version controlled templates  

## Technical Details

### TemplateManager Class
```python
class TemplateManager:
    def __init__(self, templates_root_dir: str)
    def get_groups(self) -> List[str]
    def get_templates_for_group(self, group_name: str) -> List[TemplateInfo]
    def get_templates_for_object_type(self, object_type: str) -> Dict[str, List[TemplateInfo]]
```

### TemplateInfo Dataclass
```python
@dataclass
class TemplateInfo:
    name: str
    description: str
    object_type: str
    filepath: str
    filename: str
    group: str
```

### SqlGeneratorWorker Updates
- Accepts `template_selections: Dict[str, List[TemplateInfo]]`
- Generates files using selected templates
- Filename includes template name for uniqueness
- Falls back to defaults if no templates selected

## Migration from Old System

### Old Way
- Fixed templates in root directory
- One template per object type
- Hardcoded template loading

### New Way
- Templates in subdirectories
- Multiple templates per object type
- Dynamic template discovery
- Metadata-driven

### Backward Compatibility
✅ Old templates still work (with defaults)  
✅ Fallback to basic SQL if templates missing  
✅ No breaking changes  

## Future Enhancements

Potential improvements:
- Template categories/tags
- Template variables/parameters
- Template preview
- Template validation
- Import/export template packs
- Template marketplace
- User-specific templates
- Project-specific templates

## Status

✅ **Complete and Ready to Use**

All features implemented, tested, and documented.

