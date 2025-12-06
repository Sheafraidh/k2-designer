# K2 Designer

A modern Python Qt6 application for designing database schemas, creating ER diagrams, and generating SQL scripts. Features a rich visual interface with support for Oracle database modeling.

---

## 📜 License

**Copyright (c) 2025 Karel Švejnoha. All rights reserved.**

This project is **dual-licensed**:

### 1. AGPL-3.0 (Open Source)
✅ **Free for:**
- Personal use, education, and research
- Internal company use (non-commercial)
- Open-source projects

⚠️ **Requirements:**
- Any modifications or derivative works must remain open-source under AGPL-3.0
- Complete source code must be made publicly available
- See [LICENSE](LICENSE) file for full terms

### 2. Commercial License
💼 **Required for:**
- Closed-source products
- Commercial distribution or resale
- SaaS hosting/deployment
- Proprietary systems
- Use without releasing source code

📧 **Contact for commercial licensing:** sheafraidh@gmail.com

**Important:** You MAY use this internally at your company at no cost. You MAY NOT sell, sublicense, or redistribute it as a proprietary product without a commercial license agreement.

---

## Features

### Core Functionality
- **Tabbed Diagram Interface**: Multiple diagrams in tabs with close buttons and keyboard navigation (Ctrl+Tab)
- **Object Browser**: Hierarchical tree view for managing all database objects (owners, tables, sequences, domains, stereotypes)
- **Visual ER Diagrams**: Interactive diagrams with drag-and-drop tables, foreign key connections, and visual relationships
- **Project Management**: Save/load projects using JSON (.k2p) storage with full data persistence and human-readable format
- **SQL Generation**: Jinja2-based templates for generating CREATE scripts (tables, sequences, users)

### Advanced Features
- **Object GUIDs**: Every object has a unique GUID for consistent JSON ordering and better git diffs (renames are trackable)
- **Stereotypes**: Define and manage table/column stereotypes with custom colors for visual categorization
- **Domains**: Reusable data type definitions that can be applied to columns
- **Multiple Selection**: Select and manipulate multiple objects simultaneously in diagrams
- **Diagram Management**: Create multiple diagrams per project, each with custom layouts and views
- **Foreign Key Visualization**: Automatic connection lines between related tables with relationship labels

### User Interface
- **Dark/Light/System Theme**: Choose your preferred theme (saved per-user)
- **User Settings**: Persistent user preferences for author, template directory, output directory, and theme
- **Object Browser Filtering**: Filter tables, columns, and other objects by various criteria
- **Double-Click Editing**: Quick access to edit dialogs by double-clicking objects
- **Context Menus**: Right-click menus throughout the interface for quick actions
- **Zoom Controls**: Zoom in/out, fit to view, and refresh diagram buttons in toolbar
- **Canvas Panning**: Pan diagrams with middle mouse button or Space+drag
- **Alt+Scroll Zoom**: Alternative zoom method using Alt+scroll wheel

### Diagram Features
- **Drag-and-Drop**: Drag tables from Object Browser onto diagrams
- **Table Positioning**: Freely position and arrange tables on canvas
- **Connection Drawing**: Visual foreign key relationships with automatic routing
- **Color Coding**: Tables colored by stereotype for easy visual identification
- **Diagram Refresh**: Manual refresh button to reload table structures
- **Duplicate Prevention**: Smart detection to prevent adding same table twice
- **Layout Persistence**: Diagram layouts saved with zoom level and scroll position

### Data Modeling
- **Tables**: Full table definition with columns, primary keys, unique constraints, indexes, partitioning
- **Columns**: Detailed column properties including data type, nullable, default, domain, stereotype
- **Sequences**: Oracle sequence objects with all standard attributes
- **Owners/Schemas**: Database users with tablespace configurations
- **Domains**: Reusable data type definitions with comments
- **Foreign Keys**: Define relationships between tables with source/target column mapping

### Quality of Life
- **New Project Dialog**: Start with custom project name and description
- **Keyboard Shortcuts**: Full keyboard navigation support (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+Tab, etc.)
- **Status Messages**: Clear feedback in status bar for all operations
- **Undo-Friendly**: Non-destructive operations where possible
- **Compact UI**: Minimal padding and margins for maximum workspace
- **Column Filtering**: Advanced filtering in table dialog for finding specific columns

## Architecture

### Data Models
- **Project**: Container for all database objects with metadata
- **Domain**: Reusable data type definitions with comments
- **Owner**: Database schema owners/users with tablespace settings
- **Table**: Database tables with columns, keys, indexes, partitioning, and stereotypes
- **Column**: Table columns with data types, constraints, domains, and stereotypes
- **Sequence**: Database sequences with all Oracle attributes
- **Diagram**: Visual diagram layouts with table positions and connections
- **Stereotype**: Visual categorization with custom colors for tables and columns

### Views
- **MainWindow**: Main application window with tabbed interface and dockable panels
- **ObjectBrowser**: Hierarchical tree view for browsing and managing all database objects
- **DiagramView**: Interactive graphics view for drawing and editing ER diagrams with zoom/pan controls
- **TableGraphicsItem**: Visual representation of tables in diagrams with columns and keys
- **ConnectionItem**: Visual lines representing foreign key relationships

### Controllers
- **ProjectManager**: Handles JSON-based project persistence and file operations
- **UserSettingsManager**: Manages user-specific preferences (theme, directories, author)

### Dialogs
- **NewProjectDialog**: Create new project with name and description
- **DomainDialog**: Add/edit domain objects with data type definitions
- **OwnerDialog**: Add/edit owner/user objects with tablespace settings
- **TableDialog**: Comprehensive table editor with columns, keys, indexes, partitioning, and filtering
- **SequenceDialog**: Add/edit sequence objects with all attributes
- **DiagramDialog**: Create new diagrams with custom names
- **StereotypeDialog**: Manage table and column stereotypes with colors
- **GenerateDialog**: SQL script generation with template selection
- **ProjectSettingsDialog**: Configure user settings (theme, author, directories)

## Installation

1. Install Python 3.11 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## Project Structure

```
k2-designer/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── docs/                       # Feature documentation
│   ├── description.md         # Original specification
│   ├── json_export_import_feature.md
│   ├── theme_feature.md
│   ├── user_settings_refactoring.md
│   └── ...                    # Other feature docs
├── src/k2_designer/
│   ├── __init__.py
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── base.py           # Base classes, Stereotype, StereotypeType
│   │   ├── domain.py         # Domain model
│   │   ├── owner.py          # Owner model  
│   │   ├── table.py          # Table, Column, Key, Index models
│   │   ├── sequence.py       # Sequence model
│   │   ├── diagram.py        # Diagram and DiagramItem models
│   │   └── project.py        # Project container
│   ├── views/                # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main window with tabs
│   │   ├── object_browser.py # Object tree view
│   │   └── diagram_view.py   # ER diagram view with graphics
│   ├── controllers/          # Business logic
│   │   ├── __init__.py
│   │   ├── project_manager.py      # Project file operations
│   │   └── user_settings.py        # User preferences manager
│   ├── dialogs/              # Add/edit dialogs
│   │   ├── __init__.py
│   │   ├── new_project_dialog.py   # New project wizard
│   │   ├── domain_dialog.py        # Domain editor
│   │   ├── owner_dialog.py         # Owner editor
│   │   ├── table_dialog.py         # Table editor (advanced)
│   │   ├── sequence_dialog.py      # Sequence editor
│   │   ├── diagram_dialog.py       # Diagram creator
│   │   ├── stereotype_dialog.py    # Stereotype manager
│   │   ├── generate_dialog.py      # SQL generation wizard
│   │   └── project_settings_dialog.py  # User settings
│   └── resources/            # UI resources (if any)
├── templates/                # Jinja2 SQL templates
│   ├── create_table.sql.j2
│   ├── create_sequence.sql.j2
│   └── create_user.sql.j2
├── tests/                    # Test scripts
│   └── (various test files)
└── generated/                # Example SQL output
    └── (generated SQL files)
```

## Usage

### First Time Setup
1. Launch the application
2. Go to **Tools → User Settings**
3. Configure your preferences:
   - **Author**: Your name or organization
   - **Template Directory**: Path to custom Jinja2 templates (optional)
   - **Output Directory**: Default location for generated SQL files
   - **Theme**: Choose Dark, Light, or System theme
4. Click OK to save (stored in `~/.k2designer/settings.json`)

### Creating a New Project
1. **File → New Project** (or Ctrl+N)
2. Enter project name and description
3. Click Create
4. Start adding database objects

### Adding Database Objects
- **Right-click** in the Object Browser to access context menus
- **Add Owner**: Create database schema owners with tablespace settings
- **Add Domain**: Define reusable data types
- **Add Table**: Create tables with columns, keys, and indexes
- **Add Sequence**: Create database sequences
- **Double-click** any object to edit it

### Working with Diagrams
1. **View → New Diagram** to create a diagram
2. **Drag tables** from Object Browser onto the diagram
3. **Use toolbar buttons**:
   - **[+]** Zoom in
   - **[−]** Zoom out
   - **[⊡]** Fit to view
   - **[⟳]** Refresh diagram (reload table structures)
4. **Middle-click drag** or **Space+drag** to pan
5. **Alt+Scroll** to zoom
6. **Select multiple tables** by Ctrl+click or drag selection box

### Managing Stereotypes
1. **Tools → Manage Stereotypes**
2. Add or edit stereotypes with custom colors
3. Assign stereotypes to tables and columns
4. Visual color coding appears in diagrams

### Saving Projects
- **File → Save Project** (Ctrl+S): Save to SQLite (.k2p files)
- **File → Save Project As**: Save with a new name
- **File → Export to JSON**: Export for version control or sharing
- **File → Import from JSON**: Import projects from JSON files

### Generating SQL Scripts
1. **Tools → Generate SQL**
2. Select objects to generate
3. Choose template and output location
4. Click Generate
5. SQL scripts created for selected objects

## Technical Details

### Database Storage
Projects are stored in SQLite databases (.k2p files) with normalized schema:
- `project_info`: Project metadata (name, description)
- `domains`: Reusable data type definitions
- `owners`: Database schema owners with tablespace configurations
- `tables`, `columns`: Table definitions and column details
- `table_keys`, `table_indexes`, `table_partitioning`: Table constraints and features
- `sequences`: Sequence definitions
- `foreign_keys`: Relationship information between tables
- `diagrams`, `diagram_items`, `diagram_connections`: Visual diagram layouts
- `stereotypes`: Table and column stereotype definitions

### JSON Export Format
Projects can be exported to JSON for:
- **Version Control**: Track schema changes in Git
- **Sharing**: Collaborate with team members
- **Backup**: Human-readable backup format
- **Integration**: Parse with external tools

JSON includes all project data: tables, columns, relationships, diagrams, stereotypes, etc.

### User Settings Storage
User preferences are stored separately in `~/.k2designer/settings.json`:
- Author name
- Template directory path
- Output directory path
- Theme preference (dark/light/system)

These settings apply to all projects and are personal to each user.

### Extensibility
The application is designed for easy extension:
- **New Database Engines**: Inherit from base model classes
- **Custom SQL Generation**: Add new Jinja2 templates
- **Additional Object Types**: Extend the data model and UI
- **Theme Customization**: Modify color palettes in code

### Dependencies
- **PyQt6**: Modern Qt6 bindings for Python (UI framework)
- **oracledb**: Oracle database connectivity (optional)
- **jinja2**: Template engine for SQL generation

### Project Storage
Projects are stored in JSON format with the `.k2p` extension. This human-readable format is:
- **Version Control Friendly**: Easy to diff and merge in Git
- **Portable**: Works across different systems and Python versions
- **Future-Proof**: No dependency on SQLite library versions
- **Readable**: Can be inspected and edited in any text editor

To migrate old SQLite `.k2p` files to JSON format, use the included migration script:
```bash
python migrate_sqlite_to_json.py old_project.k2p new_project.k2p
# Or migrate all .k2p files in current directory:
python migrate_sqlite_to_json.py --all
```

## Future Enhancements

- Reverse engineering from existing databases
- Additional database engine support (PostgreSQL, MySQL, SQL Server)
- More SQL script templates (DROP, ALTER, etc.)
- Advanced diagram features (auto-layout, export to image)
- Plugin system for custom extensions

## License

This project is open source. See the license file for details.