# Code Review — K2 Designer

High-level review of architecture, structure, and code quality. Nothing is fixed here — this is a prioritized list of findings and recommendations.

---

## Architektura a MVC oddělení

### Celkový stav
MVC rozdělení existuje (`models/`, `views/`, `controllers/`, `dialogs/`), ale není čisté. Dialogy převzaly roli kontrolerů a obsahují business logiku, která tam nepatří.

### Konkrétní problémy

**Business logika v dialozích**
- `TableDialog` (1 694 řádků, 47 metod) dělá: setup UI, načítání dat, validaci, zálohu/obnovu stavu, synchronizaci klíčů↔indexů, generování názvů, import CSV, výběr barvy. To jsou minimálně 4 různé zodpovědnosti.
- `NamingRulesEngine` je přímo instanciován v `TableDialog.__init__` — naming logika patří do controlleru, ne do dialogu.
- Záloha stavu přes `copy.deepcopy()` (~řádky 69–135 v `table_dialog.py`) je recovery logika modelu implementovaná v UI vrstvě.

**MainWindow jako orchestrátor**
- `MainWindow` (845 řádků, 35 metod) řídí projekty, diagramy, téma, generování SQL i test data. Část z toho patří do `ProjectManager`.

**Dialogy přistupují přímo k modelům**
- Dialogy importují `Column`, `Key`, `Index`, `Partitioning` přímo a samy je vytvářejí — chybí factory nebo service vrstva.

---

## God třídy

| Třída | Řádky | Metody | Zodpovědnosti |
|---|---|---|---|
| `TableDialog` | 1 694 | 47 | UI setup, data I/O, validace, synchronizace, state management |
| `DiagramView` | 1 631 | 67 | Rendering, zoom, scroll, drag&drop, kontext menu, serialization |
| `DataGridWidget` | 1 242 | 51 | Tabulka, filtrování, řazení, editace buněk, výběr, custom tlačítka |
| `ObjectBrowser` | 716 | 33 | Strom, kontext menu, filtrování, drag&drop, CRUD koordinace |

`DiagramView` a `DataGridWidget` jsou nejhorší — mísí datový model, view rendering a event handling v jedné třídě.

---

## Duplicitní kód

**Vzor lookup-and-remove v `Project` a `Table`**
Totožný pattern se opakuje 8× (domains, owners, tables, sequences, columns, keys, indexes, diagrams):
```python
# project.py — opakuje se pro každý typ objektu
for i, domain in enumerate(self.domains):
    if domain.name == domain_name:
        del self.domains[i]
        return True
return False
```
Pythonic varianta: `next((d for d in self.domains if d.name == name), None)`.

**Struktura dialogů**
`DomainDialog`, `OwnerDialog`, `SequenceDialog` jsou strukturálně identické — `QFormLayout`, ok/cancel tlačítka, `is_edit_mode` branch v titulku, stejný `_on_ok` vzor. Chybí společná base třída `BaseDialog`.

**`UserSettingsManager` properties**
8 identických property párů (author, template_directory, output_directory, theme, last_project_path, window_geometry, window_state) — každý setter okamžitě volá `save_settings()`, tedy zapisuje na disk při každé změně. Chybí batch update.

**`to_dict` / `from_dict` boilerplate**
Každý model (`Domain`, `Owner`, `Table`, `Sequence`, `Stereotype`) implementuje stejný serialization vzor ručně. Mixin nebo serializační utilita by DRY tuto logiku.

---

## Pythonic styl

**Chybějící dataclassy**
`Column`, `Key`, `Index`, `Partitioning` v `base.py` jsou pure data containers s manuálním `__init__` a boilerplatem. Ideální kandidáti pro `@dataclass`. `DiagramItem` a `DiagramConnection` v `diagram.py` už `@dataclass` správně používají — dobrý vzor, nedodržovaný v ostatních modelech.

**String konstanty místo Enum**
`Key` třída v `base.py` definuje typy klíčů jako string konstanty:
```python
PRIMARY = "PRIMARY"
FOREIGN = "FOREIGN"
UNIQUE = "UNIQUE"
```
Měl by to být `class KeyType(Enum)` a `key_type: KeyType` v type hintech.

**`get_setting()` / `set_setting()` v `UserSettingsManager`**
Java-style gettery vedle Python `@property` — zbytečná duplicita API.

**`full_name` property nedodržována konzistentně**
`Table` i `Diagram` mají property `full_name`, ale kód místy stále ručně konstruuje `f"{table.owner}.{table.name}"` (např. `table_dialog.py` řádek 82).

**Pozdní importy uvnitř metod**
`table_dialog.py` importuje `Column`, `Key`, `Index` z `..models.base` na ~20 místech uvnitř metod místo na úrovni modulu. Zpomaluje to každé volání a skrývá závislosti.

**`LegacyStereotype` enum**
`base.py` řádek 73 obsahuje komentář "will be replaced by custom stereotypes" — ale stále tam je. Dead code.

---

## Pojmenování

- `_dict_to_project()` v `ProjectManager` (~172 řádků) — příliš velká privátní metoda, měla by se rozložit na `_load_domains()`, `_load_tables()` atd.
- `test_data_generator.py` je v `controllers/` ale obsahuje jen statické metody bez vazby na project lifecycle — patří spíš do `utils/`.
- `LegacyStereotype` — název s "Legacy" v produkčním kódu je code smell.
- `_build_foreign_keys_index()` v `ProjectManager` — komentář říká "foreign_keys are no longer saved — they're auto-built", ale metoda stále existuje a spouští se.

---

## Specifické code smells

**Signal disconnect pattern**
```python
# table_dialog.py — 4× opakující se blok
with warnings.catch_warnings():
    warnings.simplefilter("ignore", RuntimeWarning)
    some_combo.currentTextChanged.disconnect()
```
Supresování warningu zakrývá fakt, že není jasné, jestli je signal připojen nebo ne. Lepší: explicitně trackovat stav připojení nebo použít `blockSignals()`.

**Tight coupling: dialogy → modely → dialogy**
`TableDialog` drží přímé reference na `Table`, `Column`, `Key`, `Index` a mutuje je uvnitř. Žádný command/undo pattern — záloha přes `deepcopy` je křehká.

**Chybí logging**
Všude `print()` + `traceback.print_exc()` místo `logging`. Produkční ladění je tak nemožné bez připojeného terminálu.

**Immediate save na každý setter**
`UserSettingsManager` — zápis na disk při každé změně property je zbytečně nákladný, zejména při inicializaci nebo batch update.

**`foreign_keys` jako raw dict**
`Project.foreign_keys: dict[str, dict[str, str]]` — nestrukturovaný dict bez typové ochrany. `TypedDict` nebo dataclass by daly statickou analýzu.

---

## Prioritizovaný plán

### P0 — Největší ROI, relativně bezpečné
1. **Rozdělit `TableDialog`** na tab-komponenty (`ColumnsTab`, `KeysTab`, `IndexesTab`) — redukuje 1 694 řádků na ~400 v hlavní třídě
2. **Přesunout state backup/restore a naming logiku** z `TableDialog` do `ProjectManager` nebo dedikované service
3. **Přidat `BaseDialog`** — eliminovat duplicitní boilerplate v `DomainDialog`, `OwnerDialog`, `SequenceDialog`

### P1 — Čistší architektura
4. **Převést `Column`, `Key`, `Index`, `Partitioning` na `@dataclass`** — méně boilerplate, lepší čitelnost
5. **`KeyType` jako `Enum`** místo string konstant
6. **Přesunout late importy** na úroveň modulu v `table_dialog.py`
7. **Smazat `LegacyStereotype`** a dočistit `_build_foreign_keys_index()` komentář

### P2 — Kvalita kódu
8. **Nahradit `print()` za `logging`** v controllers
9. **Batch save v `UserSettingsManager`** — jeden zápis při `__exit__` nebo explicitním `save()`
10. **`TypedDict` pro `foreign_keys`** v `Project`
11. **Sjednotit `full_name` property** — odstranit ruční `f"{owner}.{name}"` konstrukce

### P3 — Refaktoring god tříd (větší zásah)
12. **`DiagramView`** — vyextrahovat rendering, context menu handling a event processing
13. **`DataGridWidget`** — oddělit filtering logic, sorting, editor creation
14. **DI pro `MainWindow`** — injektovat `ProjectManager` a `UserSettingsManager` místo přímé instanciace
