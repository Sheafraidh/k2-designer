# Naming Rules Engine

## Overview

K2 Designer includes a powerful naming rules engine that automatically generates names for database constraints (keys, indexes, checks) based on customizable Jinja2 templates.

## Features

✅ **Automatic name generation** - Names are auto-generated when you add keys/indexes
✅ **Numbered suffixes** - Automatically increments (FK1, FK2, FK3, etc.)
✅ **Customizable templates** - Define your own naming conventions
✅ **Project-specific** - Different naming rules per project
✅ **Jinja2 powered** - Full template language support

## Quick Start

### 1. Default Naming Convention

Out of the box, K2 Designer uses these naming patterns:

- **Primary Keys**: `TABLE_PK`
- **Foreign Keys**: `TABLE_FK1`, `TABLE_FK2`, etc.
- **Unique Keys**: `TABLE_UK1`, `TABLE_UK2`, etc.
- **Indexes**: `TABLE_I1`, `TABLE_I2`, etc.

### 2. How It Works

When you click the **Add button** (➕) in the Keys or Indexes tab:

1. A new row is created
2. The naming engine automatically generates a name based on:
   - Current table name
   - Key/index type
   - Existing keys/indexes count
   - Referenced table (for foreign keys)
3. The generated name appears in the Name field
4. You can manually edit it if needed

### 3. Customizing Naming Rules

Edit the template file: `templates/naming_rules.j2`

## Template Reference

### Available Variables

In your templates, you have access to:

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `table_name` | string | Name of the table | `"EMPLOYEES"` |
| `owner` | string | Owner/schema name | `"HR"` |
| `columns` | list | Column names in constraint | `["EMP_ID", "DEPT_ID"]` |
| `number` | int | Sequential number | `1`, `2`, `3`, ... |
| `key_type` | string | Type of key | `"PRIMARY"`, `"FOREIGN"`, `"UNIQUE"` |
| `referenced_table` | string | Referenced table (FK only) | `"HR.DEPARTMENTS"` |

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `abbreviate(n)` | Truncate to n characters | `"EMPLOYEES"\|abbreviate(3)` → `"EMP"` |
| `upper` | Convert to uppercase | `"name"\|upper` → `"NAME"` |
| `lower` | Convert to lowercase | `"NAME"\|lower` → `"name"` |
| `join(sep)` | Join list with separator | `["A","B"]\|join("_")` → `"A_B"` |

## Template Examples

### Example 1: Standard Naming (Default)

```jinja2
{% macro primary_key(table_name, columns, number) -%}
{{ table_name }}_PK
{%- endmacro %}

{% macro foreign_key(table_name, columns, number, referenced_table) -%}
{{ table_name }}_FK{{ number }}
{%- endmacro %}

{% macro unique_key(table_name, columns, number) -%}
{{ table_name }}_UK{{ number }}
{%- endmacro %}

{% macro index_name(table_name, columns, number) -%}
{{ table_name }}_I{{ number }}
{%- endmacro %}
```

**Results**:
- PK: `EMPLOYEES_PK`
- FK: `EMPLOYEES_FK1`, `EMPLOYEES_FK2`
- UK: `EMPLOYEES_UK1`
- Index: `EMPLOYEES_I1`

### Example 2: Prefixed Style

```jinja2
{% macro primary_key(table_name, columns, number) -%}
PK_{{ table_name }}
{%- endmacro %}

{% macro foreign_key(table_name, columns, number, referenced_table) -%}
FK_{{ table_name }}_{{ number }}
{%- endmacro %}

{% macro unique_key(table_name, columns, number) -%}
UK_{{ table_name }}_{{ number }}
{%- endmacro %}

{% macro index_name(table_name, columns, number) -%}
IDX_{{ table_name }}_{{ number }}
{%- endmacro %}
```

**Results**:
- PK: `PK_EMPLOYEES`
- FK: `FK_EMPLOYEES_1`, `FK_EMPLOYEES_2`
- UK: `UK_EMPLOYEES_1`
- Index: `IDX_EMPLOYEES_1`

### Example 3: Include Column Names

```jinja2
{% macro primary_key(table_name, columns, number) -%}
{{ table_name }}_{{ columns[0] }}_PK
{%- endmacro %}

{% macro foreign_key(table_name, columns, number, referenced_table) -%}
{{ table_name }}_{{ columns[0] }}_FK
{%- endmacro %}

{% macro unique_key(table_name, columns, number) -%}
{{ table_name }}_{{ columns|join('_') }}_UK
{%- endmacro %}

{% macro index_name(table_name, columns, number) -%}
{{ table_name }}_{{ columns|join('_')|abbreviate(20) }}_IDX
{%- endmacro %}
```

**Results** (for columns `EMP_ID`):
- PK: `EMPLOYEES_EMP_ID_PK`
- FK: `EMPLOYEES_DEPT_ID_FK`
- UK: `EMPLOYEES_EMAIL_UK`
- Index: `EMPLOYEES_LAST_NAME_FIRST_NAME_IDX`

### Example 4: Include Referenced Table (FK)

```jinja2
{% macro foreign_key(table_name, columns, number, referenced_table) -%}
{% if referenced_table %}
{{ table_name }}_{{ referenced_table.split('.')[-1] }}_FK
{% else %}
{{ table_name }}_FK{{ number }}
{% endif %}
{%- endmacro %}
```

**Results**:
- FK referencing `HR.DEPARTMENTS`: `EMPLOYEES_DEPARTMENTS_FK`
- FK without reference: `EMPLOYEES_FK1`

### Example 5: Oracle-style Short Abbreviations

```jinja2
{% macro primary_key(table_name, columns, number) -%}
{{ table_name|abbreviate(26) }}_PK
{%- endmacro %}

{% macro foreign_key(table_name, columns, number, referenced_table) -%}
{{ table_name|abbreviate(23) }}_FK{{ '%02d'|format(number) }}
{%- endmacro %}

{% macro unique_key(table_name, columns, number) -%}
{{ table_name|abbreviate(23) }}_UK{{ '%02d'|format(number) }}
{%- endmacro %}

{% macro index_name(table_name, columns, number) -%}
{{ table_name|abbreviate(23) }}_I{{ '%02d'|format(number) }}
{%- endmacro %}
```

**Results** (Oracle 30-char limit friendly):
- PK: `EMPLOYEES_PK` (max 28 chars)
- FK: `EMPLOYEES_FK01`, `EMPLOYEES_FK02` (max 28 chars)
- UK: `EMPLOYEES_UK01`
- Index: `EMPLOYEES_I01`

## Advanced Usage

### Conditional Logic

```jinja2
{% macro foreign_key(table_name, columns, number, referenced_table) -%}
{% if columns|length == 1 %}
  {# Single column FK #}
  {{ table_name }}_{{ columns[0] }}_FK
{% else %}
  {# Multi-column FK #}
  {{ table_name }}_FK{{ number }}
{% endif %}
{%- endmacro %}
```

### Using Owner/Schema

```jinja2
{% macro primary_key(table_name, columns, number) -%}
{% if owner %}
{{ owner }}_{{ table_name }}_PK
{% else %}
{{ table_name }}_PK
{% endif %}
{%- endmacro %}
```

### Custom Abbreviations

```jinja2
{% macro index_name(table_name, columns, number) -%}
{% set short_name = table_name|replace('EMPLOYEE', 'EMP')|replace('DEPARTMENT', 'DEPT') %}
{{ short_name }}_IDX{{ number }}
{%- endmacro %}
```

## Tips & Best Practices

### 1. Keep Names Short
Oracle has a 30-character limit for object names (128 in 12.2+). Consider abbreviating long table names.

### 2. Be Consistent
Use the same pattern across all your databases for easier maintenance.

### 3. Make It Readable
Include enough information to understand what the constraint does without making it too long.

### 4. Test Your Rules
After changing the template, test by creating a few keys/indexes to verify the output.

### 5. Version Control
Keep your `naming_rules.j2` in version control along with your project.

### 6. Project-Specific Rules
You can have different templates for different projects by placing `naming_rules.j2` in each project's templates directory.

## Troubleshooting

### Names Not Auto-Generating

**Problem**: Names remain empty when adding keys/indexes

**Solution**: 
- Check that `naming_rules.j2` exists in `templates/` directory
- Verify the template syntax is valid Jinja2
- Check console for error messages

### Template Syntax Errors

**Problem**: Error loading naming rules template

**Solution**:
- Validate your Jinja2 syntax
- Ensure all macros are properly closed with `{%- endmacro %}`
- Check that variable names match those provided

### Wrong Numbers in Names

**Problem**: FK1 appears instead of FK2 when you already have FK1

**Solution**:
- This is calculated from existing keys in the table
- Make sure keys are being properly saved to the table
- Try closing and reopening the table dialog

## File Location

Template file: `templates/naming_rules.j2`

Create this file in your K2 Designer installation directory or in your project-specific templates folder.

## Related Features

- **Stereotype System**: Apply consistent styling to tables/columns
- **Template Engine**: Generate SQL DDL from templates
- **Project Settings**: Configure project-wide settings

---

**Need help?** The naming engine will fall back to sensible defaults if the template is missing or has errors, so your workflow won't be interrupted.

