# K2 Designer

A Python Qt6 application for creating database ER diagrams and generating SQL scripts based on the database model.

## Features

- **MDI Interface**: Multiple diagram windows with dockable panels
- **Object Browser**: Tree view for managing database objects (owners, tables, sequences, domains)
- **Properties Panel**: Dynamic properties editor for selected objects
- **Diagram Drawing**: Visual ER diagram with table representations and foreign key connections
- **Project Management**: Save/load projects using SQLite storage
- **SQL Generation**: Jinja2-based templates for generating SQL scripts
- **Database Support**: Initially supports Oracle database with extensible design for other engines

## Architecture

### Data Models
- **Domain**: Data type definitions
- **Owner**: Database schema owners/users with tablespace settings  
- **Table**: Database tables with columns, keys, indexes, and partitioning
- **Sequence**: Database sequences with all attributes
- **Project**: Container for all database objects

### Views
- **MainWindow**: MDI main window with menus and toolbars
- **ObjectBrowser**: Tree view for browsing database objects
- **PropertiesPanel**: Dynamic properties editor
- **DiagramView**: Graphics view for drawing ER diagrams

### Controllers
- **ProjectManager**: Handles file operations and SQLite persistence

### Dialogs
- **DomainDialog**: Add/edit domain objects
- **OwnerDialog**: Add/edit owner/user objects  
- **TableDialog**: Add/edit table objects with columns

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
├── docs/
│   └── description.md         # Project specification
├── src/k2_designer/
│   ├── __init__.py
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── base.py           # Base classes and enums
│   │   ├── domain.py         # Domain model
│   │   ├── owner.py          # Owner model  
│   │   ├── table.py          # Table model
│   │   ├── sequence.py       # Sequence model
│   │   └── project.py        # Project container
│   ├── views/                # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main MDI window
│   │   ├── object_browser.py # Object tree view
│   │   ├── properties_panel.py # Properties editor
│   │   └── diagram_view.py   # ER diagram view
│   ├── controllers/          # Business logic
│   │   ├── __init__.py
│   │   └── project_manager.py # Project file operations
│   ├── dialogs/              # Add/edit dialogs
│   │   ├── __init__.py
│   │   ├── domain_dialog.py
│   │   ├── owner_dialog.py
│   │   └── table_dialog.py
│   └── resources/            # UI resources
├── templates/                # Jinja2 SQL templates
│   ├── create_table.sql
│   └── create_sequence.sql
└── tests/                    # Unit tests
```

## Usage

### Creating a New Project
1. Launch the application
2. A new empty project is created automatically
3. Use the Object Browser to add owners, domains, tables, and sequences

### Adding Database Objects
- **Right-click** in the Object Browser to access context menus
- **Add Owner**: Create database schema owners with tablespace settings
- **Add Domain**: Define reusable data types
- **Add Table**: Create tables with columns, keys, and indexes
- **Add Sequence**: Create database sequences

### Working with Diagrams
1. Go to **View > New Diagram** to create a diagram window
2. Tables from your project will be displayed automatically
3. Use toolbar buttons to zoom and arrange the view
4. Select objects to view their properties in the Properties Panel

### Saving Projects
- **File > Save Project**: Save to SQLite database (.k2p files)
- **File > Save Project As**: Save with a new name
- Projects include all objects, relationships, and diagram layouts

## Technical Details

### Database Storage
Projects are stored in SQLite databases with normalized schema:
- `project_info`: Project metadata
- `domains`, `owners`, `tables`, `sequences`: Object definitions
- `columns`, `table_keys`, `table_indexes`: Detailed table structures
- `foreign_keys`: Relationship information

### Extensibility
The application is designed for easy extension:
- **New Database Engines**: Inherit from base model classes
- **Custom SQL Generation**: Add new Jinja2 templates
- **Additional Object Types**: Extend the data model and UI

### Dependencies
- **PyQt6**: Modern Qt6 bindings for Python
- **oracledb**: Oracle database connectivity
- **jinja2**: Template engine for SQL generation
- **sqlite3**: Built-in Python SQLite support

## Future Enhancements

- Reverse engineering from existing databases
- Additional database engine support (PostgreSQL, MySQL, SQL Server)
- More SQL script templates (DROP, ALTER, etc.)
- Advanced diagram features (auto-layout, export to image)
- Plugin system for custom extensions

## License

This project is open source. See the license file for details.