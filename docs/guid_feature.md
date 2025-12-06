# GUID Object Sequencing Feature

## Overview

Every object in K2 Designer now has a unique GUID (Globally Unique Identifier) to enable:
- **Consistent JSON ordering** - Objects are always sorted by GUID in the JSON file
- **Easy diff tracking** - Git diffs show what actually changed
- **Rename detection** - When an object is renamed, its GUID stays the same
- **Better code reviews** - Pull requests are easier to review

## What Has GUIDs?

Every object type now includes a `guid` field:

- ✅ **Domains** (`Domain`)
- ✅ **Owners** (`Owner`)
- ✅ **Tables** (`Table`)
- ✅ **Columns** (`Column`)
- ✅ **Keys** (`Key`)
- ✅ **Indexes** (`Index`)
- ✅ **Sequences** (`Sequence`)
- ✅ **Stereotypes** (`Stereotype`)
- ✅ **Diagrams** (`Diagram`)
- ✅ **Diagram Items** (`DiagramItem`)
- ✅ **Diagram Connections** (`DiagramConnection`)

## How It Works

### 1. GUID Generation

When you create a new object, it automatically gets a unique GUID:

```python
table = Table("EMPLOYEES", "HR")
print(table.guid)  # e.g., "a3f2e8c1-4b7d-4e5f-9a8b-1c2d3e4f5a6b"
```

### 2. Consistent Ordering

When saving to JSON, objects are sorted by their GUID:

```json
{
  "tables": [
    {
      "guid": "12345678-1234-1234-1234-123456789abc",
      "name": "EMPLOYEES",
      "columns": [
        {
          "guid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
          "name": "ID"
        },
        {
          "guid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
          "name": "NAME"
        }
      ]
    },
    {
      "guid": "87654321-4321-4321-4321-cba987654321",
      "name": "DEPARTMENTS",
      ...
    }
  ]
}
```

The same project will **always** produce the same JSON output (same order).

### 3. Rename Detection

When you rename an object, the GUID stays the same:

**Before rename:**
```json
{
  "guid": "12345678-1234-1234-1234-123456789abc",
  "name": "EMPLOYEES",
  "owner": "HR"
}
```

**After rename to "STAFF":**
```json
{
  "guid": "12345678-1234-1234-1234-123456789abc",
  "name": "STAFF",
  "owner": "HR"
}
```

**Git diff shows:**
```diff
 {
   "guid": "12345678-1234-1234-1234-123456789abc",
-  "name": "EMPLOYEES",
+  "name": "STAFF",
   "owner": "HR"
 }
```

The unchanged GUID makes it obvious this is a **rename**, not a delete+create!

## Benefits

### 1. Better Git Diffs

**Without GUIDs (old way):**
```diff
  "tables": [
+   {
+     "name": "STAFF",
+     "owner": "HR",
+     "columns": [...all columns repeated...]
+   },
-   {
-     "name": "EMPLOYEES", 
-     "owner": "HR",
-     "columns": [...all columns repeated...]
-   }
  ]
```

❌ Looks like you deleted EMPLOYEES and created STAFF (hard to review)

**With GUIDs (new way):**
```diff
  {
    "guid": "12345678-1234-1234-1234-123456789abc",
-   "name": "EMPLOYEES",
+   "name": "STAFF",
    "owner": "HR",
    "columns": [...]
  }
```

✅ Clearly shows it's just a rename (easy to review)

### 2. Consistent File Format

Every time you save, the JSON is in the same order:
- Makes git history cleaner
- Reduces merge conflicts
- Easier to track changes over time

### 3. Column Reordering Detection

If you reorder columns in the UI, the JSON order doesn't change (sorted by GUID):

```json
{
  "columns": [
    {"guid": "aaa...", "name": "ID"},      // Always first (lowest GUID)
    {"guid": "bbb...", "name": "NAME"},    // Always second
    {"guid": "ccc...", "name": "EMAIL"}    // Always third (highest GUID)
  ]
}
```

Even if you move EMAIL to the top in the UI, the JSON stays sorted by GUID!

### 4. Pull Request Reviews

When reviewing PRs on GitHub:

```diff
+ {
+   "guid": "new-guid-here",
+   "name": "SALARY",
+   "data_type": "NUMBER(10,2)"
+ }
```
✅ New GUID = **new column added**

```diff
  {
    "guid": "existing-guid",
-   "data_type": "VARCHAR2(50)",
+   "data_type": "VARCHAR2(100)"
  }
```
✅ Same GUID = **existing column modified**

```diff
- {
-   "guid": "deleted-guid",
-   "name": "OLD_COLUMN"
- }
```
✅ Missing GUID = **column deleted**

## Implementation Details

### Model Changes

All model classes now:
1. Accept an optional `guid` parameter in `__init__`
2. Generate a GUID if not provided: `self.guid = guid or str(uuid.uuid4())`
3. Include `guid` in `to_dict()` output
4. Accept `guid` in `from_dict()` for loading

### Sorting

The `project_manager.py` sorts all collections by GUID when saving:

```python
"tables": [table.to_dict() for table in sorted(project.tables, key=lambda x: x.guid)]
```

This ensures consistent ordering regardless of insertion order.

### Backward Compatibility

Old JSON files without GUIDs will still load:
- Missing GUIDs are generated automatically
- First save will add GUIDs to all objects
- After that, GUIDs are preserved

## Testing

Run the GUID test:

```bash
python test_guid.py
```

Expected output:
```
======================================================================
Testing GUID Functionality and Consistent JSON Ordering
======================================================================

📝 PHASE 1: Creating objects with GUIDs...
   Domain1 GUID: a3f2e8c1-...
   Domain2 GUID: b4g3f9d2-...
   ...

✅ ALL GUID TESTS PASSED!
```

## Migration

Existing projects without GUIDs:
1. Will load successfully (GUIDs generated on load)
2. Save them once to persist the GUIDs
3. From then on, GUIDs are stable

## Example JSON Output

Here's what a complete object looks like with GUIDs:

```json
{
  "guid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "EMPLOYEES",
  "owner": "HR",
  "tablespace": "USERS",
  "stereotype": "Business",
  "color": "#4A90E2",
  "columns": [
    {
      "guid": "11111111-1111-1111-1111-111111111111",
      "name": "EMPLOYEE_ID",
      "data_type": "NUMBER(18,0)",
      "nullable": false
    },
    {
      "guid": "22222222-2222-2222-2222-222222222222",
      "name": "FIRST_NAME",
      "data_type": "VARCHAR2(50)",
      "nullable": false
    }
  ],
  "keys": [
    {
      "guid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "name": "PK_EMPLOYEES",
      "columns": ["EMPLOYEE_ID"]
    }
  ]
}
```

## Summary

✅ **Every object has a unique GUID**  
✅ **JSON is always sorted by GUID** (consistent output)  
✅ **Renames are easily detectable** (GUID stays same)  
✅ **Better git diffs** (clear what changed)  
✅ **Easier code reviews** (track actual changes)  
✅ **Backward compatible** (old files still work)

This makes K2 Designer projects **much more git-friendly** and easier to work with in teams!

