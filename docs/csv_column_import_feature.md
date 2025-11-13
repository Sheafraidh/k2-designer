# CSV Column Import Feature

## ✅ **Feature Complete**

You can now import columns from CSV data in the table dialog! Paste from clipboard or load from files with support for various delimiters and quote styles.

---

## 🎯 **Overview**

### **Access Point**
Table Dialog → Columns tab → **"Import from CSV..."** button

### **Capabilities**
- ✅ **Paste from clipboard** - Copy from Excel, spreadsheets, etc.
- ✅ **Load from file** - Import .csv, .txt files
- ✅ **Multiple delimiters** - Comma, tab, semicolon, pipe
- ✅ **Quote support** - Double quotes, single quotes, or none
- ✅ **Header detection** - With or without header row
- ✅ **Live preview** - See parsed data before importing
- ✅ **Append or replace** - Choose to add to existing or replace all
- ✅ **Smart parsing** - Handles nullable values intelligently

---

## 🎨 **User Interface**

### **CSV Import Dialog**

```
┌─────────────────────────────────────────────┐
│  Import Columns from CSV                    │
├─────────────────────────────────────────────┤
│  Import Options                             │
│  ┌─────────────────────────────────────┐   │
│  │ Delimiter: [▼ Comma (,)       ]     │   │
│  │ Quote character: [▼ Double quote (")]│   │
│  │ ☑ First row contains headers         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  CSV Data                                   │
│  [Paste from Clipboard] [Load from File...] │
│  ┌─────────────────────────────────────┐   │
│  │ name,data_type,nullable,default,...  │   │
│  │ ID,NUMBER(10),NO,,Primary key        │   │
│  │ NAME,VARCHAR2(100),NO,,Full name     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Preview                                    │
│  ┌─────────────────────────────────────┐   │
│  │ Col Name | Data Type  | Null | ...  │   │
│  │ ID       | NUMBER(10) | NO   | ...  │   │
│  │ NAME     | VARCHAR2.. | NO   | ...  │   │
│  └─────────────────────────────────────┘   │
│  ✓ Preview: 2 columns will be imported     │
│                                             │
│  [  OK  ]  [Cancel]                         │
└─────────────────────────────────────────────┘
```

---

## 📋 **CSV Format**

### **Expected Columns**
```
column_name, data_type, nullable, default, comment
```

### **Example with Headers**
```csv
name,data_type,nullable,default,comment
ID,NUMBER(10),NO,,Primary key identifier
NAME,VARCHAR2(100),NO,,Employee full name
EMAIL,VARCHAR2(100),YES,,Email address
HIRE_DATE,DATE,NO,SYSDATE,Date of hire
SALARY,NUMBER(10,2),YES,,Annual salary
```

### **Example without Headers**
```csv
ID,NUMBER(10),NO,,Primary key identifier
NAME,VARCHAR2(100),NO,,Employee full name
EMAIL,VARCHAR2(100),YES,,Email address
```

### **With Tab Delimiter**
```
name	data_type	nullable	default	comment
USER_ID	NUMBER(10)	NO		User identifier
USERNAME	VARCHAR2(50)	NO		Login username
```

### **With Pipe Delimiter**
```
name|data_type|nullable|default|comment
ACCOUNT_ID|NUMBER(10)|NO||Account ID
ACCOUNT_NAME|VARCHAR2(200)|NO||Account name
```

### **With Quotes**
```csv
"name","data_type","nullable","default","comment"
"ORDER_ID","NUMBER(10)","NO","","Order identifier"
"NOTES","VARCHAR2(4000)","YES","","May contain, commas"
```

---

## 💡 **Usage**

### **Method 1: Paste from Clipboard**

1. **Copy data from Excel/spreadsheet**
   ```
   Select columns → Ctrl+C
   ```

2. **Open table dialog**
   - Create new table or edit existing
   - Go to Columns tab
   - Click **"Import from CSV..."**

3. **Paste data**
   - Click **"Paste from Clipboard"**
   - Or Ctrl+V in text area

4. **Configure options**
   - Select delimiter (comma, tab, etc.)
   - Choose quote character
   - Check/uncheck "First row contains headers"

5. **Preview**
   - View parsed columns in preview table
   - Verify data looks correct

6. **Import**
   - Click **OK**
   - Choose append or replace if existing columns
   - Columns added to table!

### **Method 2: Load from File**

1. **Open table dialog**
   - Columns tab → **"Import from CSV..."**

2. **Load file**
   - Click **"Load from File..."**
   - Select .csv or .txt file
   - File content appears in text area

3. **Configure and import**
   - Same as Method 1

### **Method 3: Type/Edit Directly**

1. **Open import dialog**
2. **Type or edit CSV data** directly in text area
3. **Configure and import**

---

## ⚙️ **Import Options**

### **Delimiter Options**
- **Comma (,)** - Standard CSV format
- **Tab** - TSV format, good for Excel copy-paste
- **Semicolon (;)** - European CSV format
- **Pipe (|)** - Database export format

### **Quote Character**
- **Double quote (")** - Standard, protects commas in data
- **Single quote (')** - Alternative quoting
- **None** - No quote protection (careful with delimiters in data)

### **Header Row**
- **☑ First row contains headers** - Skip first row (recommended)
- **☐ First row contains headers** - Import first row as data

---

## 🧠 **Smart Features**

### **1. Nullable Value Parsing**

Automatically interprets various nullable representations:

| Input | Interpreted As |
|-------|----------------|
| YES, Y, TRUE, T, 1, NULL | `nullable = True` |
| NO, N, FALSE, F, 0, NOT NULL | `nullable = False` |
| (empty) | `nullable = True` (default) |

**Case insensitive!**

### **2. Missing Fields**

- Missing data_type → defaults to `VARCHAR2(50)`
- Missing nullable → defaults to `YES`
- Missing default → empty string
- Missing comment → empty string

### **3. Empty Rows**

Automatically skips:
- Completely empty rows
- Rows with only whitespace
- Rows without a column name

### **4. Append or Replace**

If table has existing columns:
- **Append** - Add imported columns to end
- **Replace** - Remove all existing, add imported
- **Cancel** - Cancel the import

---

## 📊 **Examples**

### **Example 1: Basic Employee Table**

**CSV:**
```csv
name,data_type,nullable,default,comment
EMPLOYEE_ID,NUMBER(10),NO,,Primary key
FIRST_NAME,VARCHAR2(50),NO,,First name
LAST_NAME,VARCHAR2(50),NO,,Last name
EMAIL,VARCHAR2(100),YES,,Email address
PHONE,VARCHAR2(20),YES,,Phone number
HIRE_DATE,DATE,NO,SYSDATE,Date hired
SALARY,NUMBER(10,2),YES,,Annual salary
DEPARTMENT_ID,NUMBER(10),YES,,Department reference
```

**Result:** 8 columns imported with proper types and constraints

---

### **Example 2: From Excel**

**Copy from Excel:**
```
ID      NUMBER(10)      N               Primary key
NAME    VARCHAR2(100)   N               Full name
STATUS  VARCHAR2(20)    Y       ACTIVE  Status flag
```

**Settings:**
- Delimiter: **Tab**
- Quote: **None**
- Headers: **No** ☐

**Result:** 3 columns imported correctly

---

### **Example 3: Complex Data Types**

**CSV:**
```csv
name,data_type,nullable,default,comment
AMOUNT,"NUMBER(15,2)",NO,0,Decimal with comma in type
JSON_DATA,CLOB,YES,,Large text field
BLOB_DATA,BLOB,YES,,Binary data
CREATED_TS,TIMESTAMP,NO,SYSTIMESTAMP,Timestamp with default
```

**Settings:**
- Delimiter: **Comma**
- Quote: **Double quote** (protects comma in NUMBER(15,2))

**Result:** All types parsed correctly including commas in types

---

### **Example 4: Minimal Format**

**CSV (no headers, minimal fields):**
```csv
ID,NUMBER(10)
NAME,VARCHAR2(100)
EMAIL,VARCHAR2(100)
```

**Settings:**
- Headers: **No** ☐

**Result:**
- Column names: ID, NAME, EMAIL
- Data types: As specified
- Nullable: All YES (default)
- Default: All empty
- Comment: All empty

---

## 🔧 **Technical Details**

### **Implementation**

#### **New Dialog:** `csv_import_dialog.py`
- Full CSV parsing with Python's `csv` module
- Live preview with QTableWidget
- Clipboard integration
- File loading
- Configurable parsing options

#### **Modified:** `table_dialog.py`
- Added "Import from CSV..." button
- New handler: `_import_from_csv()`
- New helper: `_add_imported_column()`
- Integrates with existing column management

### **Data Flow**

```
User Action (Paste/Load)
    ↓
CSV Text in Dialog
    ↓
Parse with Selected Options
    ↓
Preview in Table
    ↓
User Clicks OK
    ↓
Convert to Column Data
    ↓
Append or Replace Existing
    ↓
Columns Added to Table Dialog
```

### **Error Handling**

- **Invalid CSV** - Shows parse error in status
- **Empty data** - Warns user, doesn't import
- **Missing required fields** - Uses defaults
- **File read error** - Shows error dialog

---

## 📝 **Example Files Created**

Test run created these examples in `examples/` directory:

1. **columns_basic.csv**
   - Simple 4-column example
   - Good starting template

2. **columns_advanced.csv**
   - Comprehensive 13-column example
   - Shows various data types and features

3. **columns_tab_delimited.txt**
   - Tab-separated format
   - Good for Excel copy-paste

4. **columns_pipe_delimited.txt**
   - Pipe-separated format
   - Common in database exports

---

## 🎯 **Use Cases**

### **1. Bulk Column Import**
```
Scenario: Adding 50 columns to a table
Old way: Click Add Column 50 times, fill each
New way: Prepare CSV, import in seconds ✓
```

### **2. Excel to Database**
```
Scenario: Designer gives you Excel with column specs
Old way: Manually type each column
New way: Copy from Excel → Paste → Import ✓
```

### **3. Database Reverse Engineering**
```
Scenario: Recreating a table from documentation
Old way: Type each column from PDF/doc
New way: Copy table from doc → Import ✓
```

### **4. Template Reuse**
```
Scenario: Many tables share common columns (audit fields)
Old way: Type them in each table
New way: Save audit_columns.csv → Import in each table ✓
```

### **5. Migration Scripts**
```
Scenario: Converting from another DB tool's format
Old way: Manual translation
New way: Export → Format as CSV → Import ✓
```

---

## ⚠️ **Tips & Best Practices**

### **1. Use Headers**
Always include header row for clarity:
```csv
name,data_type,nullable,default,comment
```

### **2. Quote Data with Delimiters**
If your data contains commas:
```csv
"AMOUNT","NUMBER(15,2)","NO","0","Amount with, commas"
```

### **3. Test with Preview**
Always check preview before importing:
- Verify delimiter is correct
- Check columns parse as expected
- Ensure nullable values interpreted correctly

### **4. Save Templates**
Create CSV templates for common patterns:
- `audit_columns.csv` - Created/Updated fields
- `address_columns.csv` - Address components
- `contact_columns.csv` - Contact information

### **5. Excel → CSV**
When copying from Excel:
- Use Tab delimiter
- Uncheck quote character or set to None
- Tab naturally separates cells

---

## 🐛 **Troubleshooting**

### **Columns Not Parsing Correctly**

**Problem:** Data in wrong columns

**Solution:**
- Check delimiter matches your data
- Try different delimiter options
- Look at preview - shows how it's parsed

### **Extra Columns/Missing Data**

**Problem:** Too many or too few columns

**Solution:**
- Ensure 5 columns: name, type, nullable, default, comment
- Can omit trailing columns (will default)
- Can't have more than 5 (extras ignored)

### **Nullable Not Working**

**Problem:** All columns nullable or not nullable

**Solution:**
- Check nullable column values
- Use: YES/NO, Y/N, TRUE/FALSE, 1/0
- Case doesn't matter

### **Quote Issues**

**Problem:** Quotes appear in data

**Solution:**
- If data has quotes, select appropriate quote char
- If data doesn't have quotes, select "None"

### **File Won't Load**

**Problem:** Error loading CSV file

**Solution:**
- Check file encoding (should be UTF-8)
- Verify file isn't corrupted
- Try opening in text editor first

---

## ✅ **Benefits**

### **Time Savings**
- **50 columns:** Hours → Minutes
- **Bulk import:** Click once vs 50 times
- **No typos:** Copy exact data

### **Accuracy**
- **Exact copy:** From specs/docs
- **Preview:** Verify before import
- **Consistent:** Same format every time

### **Flexibility**
- **Multiple sources:** Excel, text files, database exports
- **Various formats:** CSV, TSV, pipe-delimited
- **Quoted or not:** Handles both

### **Productivity**
- **Reusable templates:** Save common patterns
- **Quick iterations:** Easy to modify and reimport
- **Less tedious:** No repetitive clicking

---

## 🚀 **Summary**

The CSV Column Import feature provides a powerful way to bulk-import column definitions into table dialogs. Whether copying from Excel, loading from files, or using saved templates, you can now add dozens of columns in seconds instead of minutes.

### **Key Features:**
✅ Paste from clipboard or load from file  
✅ Multiple delimiter support (comma, tab, semicolon, pipe)  
✅ Quote character handling  
✅ Header row detection  
✅ Live preview before import  
✅ Smart nullable parsing  
✅ Append or replace existing columns  

### **Access:**
Table Dialog → Columns Tab → **"Import from CSV..."** button

**Status:** ✅ **Ready to Use!**

No more tedious manual column entry - import them all at once! 🎉

