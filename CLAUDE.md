# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

K2 Designer is a PySide6 desktop application for designing Oracle database schemas visually. It lets users define owners (schemas), tables, columns, sequences, domains, and stereotypes, draw ER diagrams, and generate SQL via Jinja2 templates. Projects are saved as JSON with a `.k2p` extension.

## Running the Application

```bash
# Activate the virtual environment first
source .venv/bin/activate

# Run the application
python main.py
```

The `.venv` is the project's virtual environment (excluded from git). Dependencies: `PySide6>=6.5.0`, `jinja2>=3.1.0`, `oracledb>=1.4.0`.

```bash
pip install -r requirements.txt
```

There is no test suite. The `tests/` directory is empty and `test_datagrid.py` in the root is a standalone scratch file.

## Architecture

The app follows a layered MVC pattern rooted at `src/k2_designer/`:

### Models (`models/`)
Pure Python dataclasses representing the database schema. All models implement `to_dict()` / `from_dict()` for JSON serialization, and carry a `guid` (UUID) for stable identity across renames.

- `base.py` — `DatabaseObject` (abstract base with `name`, `comment`, `guid`), `Stereotype`, `StereotypeType`, `Column`, `Key`, `Index`, `Partitioning`, `LegacyStereotype`
- `project.py` — `Project`: top-level container holding lists of `Owner`, `Table`, `Sequence`, `Domain`, `Diagram`, `Stereotype`, plus a `foreign_keys` dict keyed by `"owner.table.column"`
- `table.py` — `Table(DatabaseObject)` with columns, keys, indexes, partitioning
- `diagram.py` — `Diagram` with `DiagramItem` positions (x, y per table GUID) and zoom/scroll state

### Controllers (`controllers/`)
Business logic that keeps models and UI in sync:

- `project_manager.py` — `ProjectManager`: loads/saves `.k2p` JSON files, holds `current_project`
- `user_settings.py` — `UserSettingsManager`: reads/writes `~/.k2designer/settings.json` (theme, author, directories, last project path, window geometry)
- `template_manager.py` — `TemplateManager`: scans the `templates/` directory tree and discovers `.j2` files grouped by subdirectory (`tables/`, `sequences/`, `users/`)
- `naming_rules_engine.py` — `NamingRulesEngine`: renders `templates/naming_rules.j2` to suggest names for keys, indexes, etc.
- `test_data_generator.py` — `TestDataGenerator`: generates sample INSERT data for testing

### Views (`views/`)
PySide6 widgets:

- `main_window.py` — `MainWindow(QMainWindow)`: orchestrates the whole app. Hosts a `QTabWidget` of `DiagramView` tabs and a docked `ObjectBrowser`. Owns `ProjectManager` and `UserSettingsManager`. `initialize_content()` is called after the splash screen appears (loads last project, applies theme).
- `object_browser.py` — `ObjectBrowser(QWidget)`: tree view showing all project objects grouped by type (Owners → Tables, Sequences; Domains; Stereotypes). Supports drag-to-diagram and double-click-to-edit.
- `diagram_view.py` — `DiagramView(QWidget)` wrapping a `QGraphicsView`/`QGraphicsScene`. Contains `TableGraphicsItem` and `ConnectionItem` graphics objects. Handles drag-drop from the Object Browser, pan (middle-click or Space+drag), zoom (Ctrl+scroll or Alt+scroll), and multiple selection.
- `properties_panel.py` — Properties inspector panel (shown for selected objects).

### Dialogs (`dialogs/`)
Modal editors for each model type: `TableDialog`, `OwnerDialog`, `DomainDialog`, `SequenceDialog`, `DiagramDialog`, `StereotypeDialog`, `GenerateDialog`, `ProjectSettingsDialog`, `NewProjectDialog`, `KeyDialog`, `CsvImportDialog`, `about_dialog.py` (also contains `SplashScreen`).

### Templates (`templates/`)
Jinja2 `.j2` files organized by subdirectory matching the object type. The `GenerateDialog` uses `TemplateManager` to discover these. Custom template directories can be set in User Settings. The `naming_rules.j2` file is used by `NamingRulesEngine` for automatic name suggestions.

## Project File Format

`.k2p` files are plain JSON (human-readable, git-diffable). The top-level keys match `Project.to_dict()`:
`name`, `description`, `domains`, `owners`, `tables`, `sequences`, `diagrams`, `stereotypes`, `foreign_keys`, `last_active_diagram`.

To migrate old SQLite `.k2p` files: `python migrate_sqlite_to_json.py --all`

## Key Conventions

- **GUIDs everywhere**: Every model object has a `guid` field (UUID4 string). Use GUIDs when referencing objects across the model (e.g., diagram positions store table GUIDs, not names).
- **Owner-qualified names**: Tables and sequences are always identified by `(name, owner)` pair. Foreign key dict keys are `"owner.table.column"` strings.
- **`to_dict` / `from_dict`**: All models serialize via these methods. When adding fields to a model, add them to both methods and handle missing keys with `.get()` for backwards compatibility with existing `.k2p` files.
- **License headers**: Every source file must include the AGPL/Commercial dual-license header block. The `add_license_headers.py` script can add them in bulk.
- **No test framework**: There are no pytest or unittest tests. Manual testing via running the app is the current approach.
- **macOS warnings suppressed**: `main.py` filters `NSOpenPanel` warnings on Darwin — don't remove this.

## Python Style
- Pythonic code preferred over Java/C++ style
- Use `@property` only when there's logic or Signal emission needed
- Direct attribute access is fine for simple data
- `snake_case` everywhere, no `getCamelCase` methods
- Prefer dataclasses for pure data containers
- List comprehensions over loops where readable
- Qt signals/slots are fine but keep them minimal
