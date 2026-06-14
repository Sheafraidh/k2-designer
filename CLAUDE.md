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

## Dependencies

Managed via `uv` and `pyproject.toml`. To install:

```bash
uv sync
```

Main dependencies: `PySide6`, `pydantic`, `jinja2`, `oracledb`.

## Architecture

The app follows a layered MVC pattern rooted at `k2gui/`:

### Models (`models/`)
Python dataclasses representing the database schema. All models implement `to_dict()` / `from_dict()` for JSON serialization, and carry a `guid` (UUID) for stable identity across renames.

- `base.py` — `DatabaseObject` (abstract base with `name`, `comment`, `guid`), `Stereotype`, `StereotypeType`, `Column`, `Key`, `Index`, `Partitioning`, `LegacyStereotype`
- `project.py` — `Project`: top-level container holding lists of `Owner`, `Table`, `Sequence`, `Domain`, `Diagram`, `Stereotype`, plus a `foreign_keys` dict keyed by `"owner.table.column"`
- `table.py` — `Table(DatabaseObject)` with columns, keys, indexes, partitioning
- `diagram.py` — `Diagram` with `DiagramItem` positions (x, y per table GUID) and zoom/scroll state

### Controllers (`controllers/`)
Business logic that keeps models and UI in sync:

- `project_manager.py` — `ProjectManager`: loads/saves `.k2p` JSON files, holds `current_project`
- `user_settings.py` — `UserSettingsManager`: reads/writes `~/.k2designer/settings.json`
- `template_manager.py` — `TemplateManager`: scans `templates/` directory for `.j2` files
- `naming_rules_engine.py` — `NamingRulesEngine`: renders `templates/naming_rules.j2` to suggest names for keys, indexes etc.
- `test_data_generator.py` — `TestDataGenerator`: generates sample INSERT data for testing

### Views (`views/`)
PySide6 widgets:

- `main_window.py` — `MainWindow(QMainWindow)`: orchestrates the whole app
- `object_browser.py` — `ObjectBrowser(QWidget)`: tree view of all project objects
- `diagram_view.py` — `DiagramView(QWidget)`: canvas with `QGraphicsView`/`QGraphicsScene`
- `properties_panel.py` — Properties inspector panel

### Dialogs (`dialogs/`)
Modal editors: `TableDialog`, `OwnerDialog`, `DomainDialog`, `SequenceDialog`, `DiagramDialog`, `StereotypeDialog`, `GenerateDialog`, `ProjectSettingsDialog`, `NewProjectDialog`, `KeyDialog`, `CsvImportDialog`, `about_dialog.py`.

### Templates (`templates/`)
Jinja2 `.j2` files organized by subdirectory matching object type. `naming_rules.j2` used by `NamingRulesEngine`.

## Project File Format

`.k2p` files are plain JSON (human-readable, git-diffable). Top-level keys match `Project.to_dict()`:
`name`, `description`, `domains`, `owners`, `tables`, `sequences`, `diagrams`, `stereotypes`, `foreign_keys`, `last_active_diagram`.

To migrate old SQLite `.k2p` files: `python migrate_sqlite_to_json.py --all`

## Key Conventions

- **GUIDs everywhere**: Every model object has a `guid` field (UUID4 string).
- **Owner-qualified names**: Tables and sequences identified by `(name, owner)` pair. Foreign key dict keys are `"owner.table.column"` strings.
- **`to_dict` / `from_dict`**: All models serialize via these methods. Handle missing keys with `.get()` for backwards compatibility.
- **License headers**: Every source file must include the AGPL/Commercial dual-license header. Use `add_license_headers.py` to add in bulk.
- **macOS warnings suppressed**: `main.py` filters `NSOpenPanel` warnings on Darwin — don't remove this.

## Tooling

- **Python**: 3.13 (managed via uv)
- **Package manager**: uv
- **Linter/Formatter**: ruff
- **Version control**: git + GitHub, PR-based workflow

## Roadmap / Current Direction

Current priorities based on code review (see `REVIEW.md`):

### P0 — Highest ROI
- Rozdělit `TableDialog` (1 694 řádků) na tab-komponenty (`ColumnsTab`, `KeysTab`, `IndexesTab`)
- Přidat `BaseDialog` — eliminovat duplicitní boilerplate v jednoduchých dialozích
- Přesunout state backup/restore a naming logiku z `TableDialog` do service vrstvy

### P1 — Čistší architektura
- Migrovat `Column`, `Key`, `Index`, `Partitioning` na Pydantic modely
- `KeyType` jako `Enum` místo string konstant
- Nahradit `print()` za `logging`

### P2 — Core/GUI oddělení
- Identifikovat soubory bez PySide6 závislostí → kandidáti na core
- Vytvořit `k2core/` jako separátní Python package (monorepo)
- Přidat pytest testy na core vrstvu (bez GUI)

## Python Style

- Pythonic kód preferován před Java/C++ stylem
- `@property` jen kde je logika nebo Signal emise
- Přímý přístup k atributům pro jednoduchá data
- `snake_case` všude, žádné `getCamelCase` metody
- Pydantic pro datové modely, dataclasses pro jednoduché kontejnery
- List comprehensions místo smyček kde je to čitelné
- Qt signals/slots minimálně