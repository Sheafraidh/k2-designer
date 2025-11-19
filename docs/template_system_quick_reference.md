# Template System Quick Reference

## For Users

### Opening the Generator
**Tools → Generate SQL**

### Selecting Templates
1. **Choose object type tab** (Tables/Sequences/Users)
2. **Check objects** you want to generate
3. **Check templates** in the left panel
4. Click **Generate SQL**

### Template Tree
- **Organized by directory** (tables/, sequences/, users/)
- **Auto-filters** based on selected tab
- **Grayed out** = not compatible with current object type
- **Check multiple** for same object = multiple files generated

### Output Files
Format: `{object_name}_{template_name}.sql`

Example:
- `employees_create_table.sql`
- `employees_archive_table.sql`
- `employees_audit_trigger.sql`

---

## For Template Authors

### Creating a New Template

#### 1. Choose Directory
```
templates/tables/      → for table templates
templates/sequences/   → for sequence templates
templates/users/       → for user templates
```

#### 2. Create File
Filename: `my_template.sql.j2`

#### 3. Add Header
```jinja2
{#
name: My Template Name
description: What this template does
object_type: table
#}
```

#### 4. Write Template
Use Jinja2 syntax with context variables.

### Available Variables

#### Tables (`object_type: table`)
```jinja2
{{ table.name }}
{{ table.owner }}
{{ table.tablespace }}
{{ table.comment }}
{{ table.columns }}        # List of Column objects
{{ table.keys }}           # List of Key objects
{{ table.indexes }}        # List of Index objects
```

**Column properties:**
```jinja2
{% for column in table.columns %}
  {{ column.name }}
  {{ column.data_type }}
  {{ column.nullable }}     # boolean
  {{ column.default }}
  {{ column.comment }}
  {{ column.domain }}
{% endfor %}
```

**Key properties:**
```jinja2
{% for key in table.keys %}
  {{ key.name }}
  {{ key.columns }}         # List of column names
{% endfor %}
```

#### Sequences (`object_type: sequence`)
```jinja2
{{ sequence.name }}
{{ sequence.owner }}
{{ sequence.start_with }}
{{ sequence.increment_by }}
{{ sequence.min_value }}
{{ sequence.max_value }}
{{ sequence.cache_size }}
{{ sequence.cycle }}        # boolean
{{ sequence.comment }}
```

#### Users (`object_type: user`)
```jinja2
{{ owner.name }}
{{ owner.default_tablespace }}
{{ owner.temp_tablespace }}
{{ owner.default_index_tablespace }}
{{ owner.editionable }}    # boolean
{{ owner.comment }}
```

### Jinja2 Tips

#### Loops
```jinja2
{% for column in table.columns %}
  {{ column.name }} {{ column.data_type }}
  {%- if not loop.last %},{% endif %}
{% endfor %}
```

#### Conditionals
```jinja2
{% if table.comment %}
COMMENT ON TABLE {{ table.owner }}.{{ table.name }} IS '{{ table.comment }}';
{% endif %}
```

#### Loop Variables
- `loop.first` - True on first iteration
- `loop.last` - True on last iteration
- `loop.index` - Current iteration (1-indexed)
- `loop.index0` - Current iteration (0-indexed)

### Example Templates

#### View Generator
```jinja2
{#
name: Create View
description: Creates a simple view over the table
object_type: table
#}
CREATE OR REPLACE VIEW {{ table.owner }}.V_{{ table.name }} AS
SELECT
{%- for column in table.columns %}
    {{ column.name }}{% if not loop.last %},{% endif %}
{%- endfor %}
FROM {{ table.owner }}.{{ table.name }};
```

#### Grant Script
```jinja2
{#
name: Grant Permissions
description: Grants SELECT and INSERT to a role
object_type: table
#}
GRANT SELECT, INSERT ON {{ table.owner }}.{{ table.name }} TO APP_ROLE;
```

#### Drop Script
```jinja2
{#
name: Drop Table
description: Drops the table with CASCADE CONSTRAINTS
object_type: table
#}
DROP TABLE {{ table.owner }}.{{ table.name }} CASCADE CONSTRAINTS;
```

---

## Troubleshooting

### Template Not Showing
- Check filename ends with `.sql.j2`
- Check header format (must be Jinja2 comment)
- Check `object_type` matches (table/sequence/user)
- Restart application

### Template Error During Generation
- Check Jinja2 syntax
- Check variable names match available context
- Check for proper escaping of SQL strings

### Multiple Templates Not Working
- Make sure you're selecting objects first
- Then check templates in left panel
- Templates apply to all selected objects

---

## Best Practices

### Template Naming
✅ Descriptive: `archive_table.sql.j2`  
✅ Lowercase with underscores  
✅ Extension: `.sql.j2`

❌ Avoid: `template1.sql.j2`, `ARCHIVE.SQL`, `test.txt`

### Metadata
✅ Clear name: "Archive Table"  
✅ Descriptive description  
✅ Correct object_type

### Template Content
✅ Include comments  
✅ Handle NULL/optional values  
✅ Use consistent formatting  
✅ Test with sample data

### Organization
✅ Group related templates in same directory  
✅ Use subdirectories if needed: `templates/tables/archive/`  
✅ Keep templates simple and focused

---

## Status

🟢 **Active Feature** - Ready for production use

