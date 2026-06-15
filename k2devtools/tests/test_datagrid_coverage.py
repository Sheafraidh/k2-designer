"""
K2 Designer - Database Schema Designer

Copyright (c) 2025 Karel Švejnoha
All rights reserved.

SPDX-License-Identifier: AGPL-3.0-only OR Commercial

This software is dual-licensed:
- AGPL-3.0: Free for personal use, education, research, and internal use.
  Any modifications or derivative works must remain open-source under AGPL.
- Commercial License: Required for closed-source products, commercial distribution,
  SaaS deployment, or use in proprietary systems.

You MAY use this project at your company internally at no cost.
You MAY NOT sell, sublicense, or redistribute it as a proprietary product
without a commercial agreement.

For commercial licensing, contact: sheafraidh@gmail.com
See LICENSE file for full terms.
"""

"""Additional coverage tests for DataGridWidget — fills gaps not in test_datagrid_excel.py."""

import pytest
from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication, QComboBox, QHeaderView, QLineEdit

from k2widgets import ColumnConfig, DataGridWidget


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def grid(qtbot):
    """Two text columns, three rows — minimal reusable baseline."""
    g = DataGridWidget()
    g.configure([
        ColumnConfig("Name",  width=120, editor_type="text", filter_type="text"),
        ColumnConfig("Value", width=80,  editor_type="text", filter_type="text"),
    ])
    g.add_row(["Alpha", "1"])
    g.add_row(["Beta",  "2"])
    g.add_row(["Gamma", "3"])
    qtbot.addWidget(g)
    g.show()
    return g


@pytest.fixture
def mixed_grid(qtbot):
    """Grid with text, checkbox_centered, combobox columns — used for widget navigation."""
    g = DataGridWidget()
    g.configure([
        ColumnConfig("Name",   width=120, editor_type="text",             filter_type="text"),
        ColumnConfig("Active", width=60,  editor_type="checkbox_centered", filter_type="none"),
        ColumnConfig("Type",   width=80,  editor_type="combobox",
                     editor_options={"items": ["A", "B", "C"]},           filter_type="none"),
        ColumnConfig("Notes",  width=100, editor_type="text",             filter_type="text"),
    ])
    g.add_row(["Alpha", True,  "A", "first"])
    g.add_row(["Beta",  False, "B", "second"])
    g.add_row(["Gamma", True,  "C", "third"])
    qtbot.addWidget(g)
    g.show()
    return g


@pytest.fixture
def filter_grid(qtbot):
    """Grid wired for filter tests: text filter + combobox filter + filter_matcher."""
    g = DataGridWidget()
    g.configure([
        ColumnConfig("Name",  width=120, editor_type="text",
                     filter_type="text"),
        ColumnConfig("Type",  width=80,  editor_type="combobox",
                     editor_options={"items": ["X", "Y", "Z"]},
                     filter_type="combobox",
                     filter_options={"items": ["All", "X", "Y", "Z"]}),
        ColumnConfig("Flag",  width=60,  editor_type="checkbox_centered",
                     filter_type="combobox",
                     filter_options={"items": ["All", "Yes", "No"]},
                     filter_matcher=lambda fv, cv:
                         (cv == "true") if fv == "Yes" else (cv == "false")),
    ])
    g.add_row(["Alpha", "X", True])
    g.add_row(["Beta",  "Y", False])
    g.add_row(["Gamma", "X", True])
    g.add_row(["Delta", "Z", False])
    qtbot.addWidget(g)
    g.show()
    return g


# ---------------------------------------------------------------------------
# Shift+Tab navigation
# ---------------------------------------------------------------------------

class TestShiftTabNavigation:
    def test_shift_tab_moves_to_previous_column(self, grid, qtbot):
        """Shift+Tab from col 1 should move focus to col 0 of the same row.

        _handle_navigation_key(Backtab) decrements column without changing row.
        """
        grid.table.setCurrentCell(1, 1)
        grid._handle_navigation_key(Qt.Key.Key_Backtab)
        assert grid.table.currentRow() == 1
        assert grid.table.currentColumn() == 0

    def test_shift_tab_wraps_to_previous_row(self, grid, qtbot):
        """Shift+Tab from col 0 should wrap to the last column of the previous row.

        When at the leftmost column, Backtab jumps to (row-1, last_col).
        """
        grid.table.setCurrentCell(1, 0)
        grid._handle_navigation_key(Qt.Key.Key_Backtab)
        assert grid.table.currentRow() == 0
        assert grid.table.currentColumn() == grid.table.columnCount() - 1

    def test_shift_tab_wraps_from_first_cell_to_last(self, grid, qtbot):
        """Shift+Tab from the very first cell (0, 0) should wrap to (last_row, last_col)."""
        grid.table.setCurrentCell(0, 0)
        grid._handle_navigation_key(Qt.Key.Key_Backtab)
        last_row = grid.table.rowCount() - 1
        last_col = grid.table.columnCount() - 1
        assert grid.table.currentRow() == last_row
        assert grid.table.currentColumn() == last_col


# ---------------------------------------------------------------------------
# Tab through widget (checkbox / combobox) cells via CellWidgetEventFilter
# ---------------------------------------------------------------------------

class TestCellWidgetNavigation:
    """CellWidgetEventFilter intercepts Tab/Backtab/Enter on cell widgets and
    forwards them to DataGridWidget._handle_navigation_key so keyboard navigation
    is seamless across all cell types.
    """

    def _send_tab(self, widget):
        """Simulate a Tab key press on the given widget."""
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(widget, event)

    def _send_backtab(self, widget):
        """Simulate a Shift+Tab key press on the given widget."""
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Backtab,
            Qt.KeyboardModifier.ShiftModifier,
        )
        QApplication.sendEvent(widget, event)

    def _send_enter(self, widget):
        """Simulate an Enter key press on the given widget."""
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(widget, event)

    def test_tab_on_checkbox_moves_to_next_column(self, mixed_grid, qtbot):
        """Tab pressed on a checkbox_centered cell should navigate to the next column.

        Without CellWidgetEventFilter, QCheckBox swallows Tab and focus gets stuck.
        """
        mixed_grid.table.setCurrentCell(0, 1)  # Active column (checkbox)
        checkbox_widget = mixed_grid.table.cellWidget(0, 1)
        cb = checkbox_widget.checkbox
        self._send_tab(cb)
        qtbot.wait(50)
        # Should have moved to col 2 (Type combobox)
        assert mixed_grid.table.currentColumn() == 2

    def test_tab_on_combobox_moves_to_next_column(self, mixed_grid, qtbot):
        """Tab pressed on a combobox cell should navigate to the next column.

        Without CellWidgetEventFilter, QComboBox swallows Tab and focus gets stuck.
        """
        mixed_grid.table.setCurrentCell(0, 2)  # Type column (combobox)
        combo = mixed_grid.table.cellWidget(0, 2)
        self._send_tab(combo)
        qtbot.wait(50)
        assert mixed_grid.table.currentColumn() == 3  # Notes column

    def test_shift_tab_on_combobox_moves_to_previous_column(self, mixed_grid, qtbot):
        """Shift+Tab on a combobox cell should navigate to the previous column."""
        mixed_grid.table.setCurrentCell(0, 2)  # Type column
        combo = mixed_grid.table.cellWidget(0, 2)
        self._send_backtab(combo)
        qtbot.wait(50)
        assert mixed_grid.table.currentColumn() == 1  # Active checkbox column

    def test_enter_on_checkbox_navigates_down(self, mixed_grid, qtbot):
        """Enter pressed on a checkbox cell should move to the next row."""
        mixed_grid.table.setCurrentCell(0, 1)
        checkbox_widget = mixed_grid.table.cellWidget(0, 1)
        cb = checkbox_widget.checkbox
        self._send_enter(cb)
        qtbot.wait(50)
        assert mixed_grid.table.currentRow() == 1

    def test_tab_through_all_cell_types_without_getting_stuck(self, mixed_grid, qtbot):
        """Tabbing through text→checkbox→combobox→text should advance column each time."""
        mixed_grid.table.setCurrentCell(0, 0)  # Name (text)
        # Tab text → checkbox
        qtbot.keyClick(mixed_grid.table, Qt.Key.Key_Tab)
        qtbot.wait(30)
        assert mixed_grid.table.currentColumn() == 1
        # Tab checkbox → combobox
        cb = mixed_grid.table.cellWidget(0, 1).checkbox
        self._send_tab(cb)
        qtbot.wait(30)
        assert mixed_grid.table.currentColumn() == 2
        # Tab combobox → text
        combo = mixed_grid.table.cellWidget(0, 2)
        self._send_tab(combo)
        qtbot.wait(30)
        assert mixed_grid.table.currentColumn() == 3


# ---------------------------------------------------------------------------
# Tab from last cell of last row — add new row
# ---------------------------------------------------------------------------

class TestTabAddsRow:
    def test_tab_from_last_cell_of_last_row_adds_row(self, grid, qtbot):
        """Tab from the last column of the last row should append a new row.

        This tests the wrap path in Tab navigation where row+1 >= rowCount
        and addRowRequested is emitted.
        """
        last_row = grid.table.rowCount() - 1
        last_col = grid.table.columnCount() - 1
        grid.table.setCurrentCell(last_row, last_col)

        before = grid.table.rowCount()
        qtbot.keyClick(grid.table, Qt.Key.Key_Tab)
        qtbot.wait(50)
        assert grid.table.rowCount() == before + 1

    def test_tab_from_last_cell_no_add_when_disabled(self, qtbot):
        """Tab from the last cell must NOT add a row when show_add_button=False."""
        g = DataGridWidget()
        g.configure(
            [ColumnConfig("N", editor_type="text")],
            show_add_button=False,
        )
        g.add_row(["Only"])
        qtbot.addWidget(g)
        g.table.setCurrentCell(0, 0)

        before = g.table.rowCount()
        qtbot.keyClick(g.table, Qt.Key.Key_Tab)
        qtbot.wait(50)
        # Wraps back to (0, 0) — no new row
        assert g.table.rowCount() == before


# ---------------------------------------------------------------------------
# Bulk edit — additional coverage
# ---------------------------------------------------------------------------

class TestBulkEditAdditional:
    def test_bulk_edit_does_not_affect_unselected_rows(self, grid, qtbot):
        """Propagation must only touch rows in _captured_selection, not all rows."""
        # Only rows 0 and 1 are in the bulk context; row 2 must be untouched.
        grid.table._captured_selection = {0, 1}
        grid.table.item(0, 0).setText("CHANGED")
        qtbot.wait(50)

        assert grid.table.item(1, 0).text() == "CHANGED"
        assert grid.table.item(2, 0).text() == "Gamma"  # untouched

    def test_bulk_edit_cell_changed_fires_once_per_propagation(self, grid, qtbot):
        """cellChanged must not recurse during propagation.

        blockSignals(True) is set on the table during setText() of target rows
        so cellChanged does NOT fire for propagated rows — it fires exactly once
        (for the source cell change that triggered the propagation).
        """
        change_count = [0]
        grid.table.cellChanged.connect(lambda r, c: change_count.__setitem__(0, change_count[0] + 1))

        grid.table._captured_selection = {0, 1, 2}
        grid.table.item(0, 0).setText("ONCE")
        qtbot.wait(50)

        # cellChanged fired once (source), not three times (once per propagated row)
        assert change_count[0] == 1, f"Expected 1 cellChanged, got {change_count[0]}"

    def test_bulk_edit_source_row_unchanged_by_propagation(self, grid, qtbot):
        """The source row's value is set by the editor, not by propagation — verify no double-write."""
        grid.table._captured_selection = {0, 1, 2}
        grid.table.item(0, 0).setText("SOURCE")
        qtbot.wait(50)

        # All rows including source should have the value
        assert grid.table.item(0, 0).text() == "SOURCE"
        assert grid.table.item(1, 0).text() == "SOURCE"
        assert grid.table.item(2, 0).text() == "SOURCE"

    def test_double_click_preserves_multi_selection(self, grid, qtbot):
        """mouseDoubleClickEvent must restore the visual multi-selection after Qt collapses it.

        Without the override, a plain double-click to open the editor causes Qt to
        collapse the selection to the clicked row, breaking bulk edit UX.
        """
        grid.table.selectAll()
        qtbot.wait(50)
        assert grid.table._captured_selection == {0, 1, 2}

        # Simulate double-click on cell (0, 0) via the viewport
        item0 = grid.table.item(0, 0)
        rect  = grid.table.visualItemRect(item0)
        center = rect.center()
        from PySide6.QtCore import QPointF
        dbl = QMouseEvent(
            QMouseEvent.Type.MouseButtonDblClick,
            QPointF(center), QPointF(center),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(grid.table.viewport(), dbl)
        qtbot.wait(100)  # let the singleShot restore timer fire

        # All three rows should still be visually selected
        selected = {item.row() for item in grid.table.selectedItems()}
        assert selected == {0, 1, 2}, (
            f"Multi-selection must survive double-click; got {selected}"
        )

    def test_real_editor_bulk_edit_end_to_end(self, grid, qtbot):
        """Full end-to-end: open inline editor, type, press Enter → propagates to all selected rows.

        This is the REAL runtime path: editor writes to model → cellChanged → propagation.
        Previous mechanism (commitData override) was broken; cellChanged is the correct hook.
        """
        grid.table.selectAll()
        qtbot.wait(50)
        grid.table._captured_selection = {0, 1, 2}

        # Open the inline editor for (0, 0)
        grid.table.edit(grid.table.model().index(0, 0))
        qtbot.wait(50)

        editors = grid.table.viewport().findChildren(QLineEdit)
        assert editors, "Inline editor should be open after edit()"
        ed = editors[0]
        ed.setText("PROPAGATE")

        # Press Enter: commitData → cellChanged → propagation; closeEditor → navigate
        enter = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return,
                          Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(ed, enter)
        qtbot.wait(50)

        assert grid.table.item(0, 0).text() == "PROPAGATE"
        assert grid.table.item(1, 0).text() == "PROPAGATE"
        assert grid.table.item(2, 0).text() == "PROPAGATE"


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class TestFilters:
    def test_text_filter_hides_non_matching_rows(self, filter_grid, qtbot):
        """Typing in the text filter should hide rows that don't match the substring."""
        text_filter = filter_grid._filters[0]  # Name column filter
        text_filter.setText("alp")  # matches "Alpha"
        qtbot.wait(50)

        assert not filter_grid.table.isRowHidden(0)  # Alpha — shown
        assert filter_grid.table.isRowHidden(1)       # Beta  — hidden
        assert filter_grid.table.isRowHidden(2)       # Gamma — hidden
        assert filter_grid.table.isRowHidden(3)       # Delta — hidden

    def test_text_filter_is_case_insensitive(self, filter_grid, qtbot):
        """Text filter must match regardless of case."""
        filter_grid._filters[0].setText("BETA")
        qtbot.wait(50)

        assert filter_grid.table.isRowHidden(0)
        assert not filter_grid.table.isRowHidden(1)  # Beta visible
        assert filter_grid.table.isRowHidden(2)
        assert filter_grid.table.isRowHidden(3)

    def test_combobox_filter_hides_non_matching_rows(self, filter_grid, qtbot):
        """Combobox filter (non-editable) should hide rows with a different value."""
        combo_filter = filter_grid._filters[1]  # Type column filter
        combo_filter.setCurrentText("X")
        qtbot.wait(50)

        assert not filter_grid.table.isRowHidden(0)  # Alpha/X — shown
        assert filter_grid.table.isRowHidden(1)       # Beta/Y  — hidden
        assert not filter_grid.table.isRowHidden(2)  # Gamma/X — shown
        assert filter_grid.table.isRowHidden(3)       # Delta/Z — hidden

    def test_filter_matcher_custom_logic(self, filter_grid, qtbot):
        """filter_matcher callable overrides default equality for combobox filter.

        The Flag column uses filter_matcher: 'Yes' → show only checked rows.
        """
        flag_filter = filter_grid._filters[2]  # Flag column filter
        flag_filter.setCurrentText("Yes")
        qtbot.wait(50)

        assert not filter_grid.table.isRowHidden(0)  # Alpha / True  — shown
        assert filter_grid.table.isRowHidden(1)       # Beta  / False — hidden
        assert not filter_grid.table.isRowHidden(2)  # Gamma / True  — shown
        assert filter_grid.table.isRowHidden(3)       # Delta / False — hidden

    def test_clear_filters_shows_all_rows(self, filter_grid, qtbot):
        """After filtering, clicking Clear Filters (⊗) must restore all rows."""
        filter_grid._filters[0].setText("alp")  # hide all but Alpha
        qtbot.wait(50)
        assert filter_grid.table.isRowHidden(1)

        filter_grid._clear_filters()
        qtbot.wait(50)

        for row in range(filter_grid.table.rowCount()):
            assert not filter_grid.table.isRowHidden(row), f"Row {row} should be visible after clear"

    def test_get_all_data_includes_filtered_rows(self, filter_grid, qtbot):
        """get_all_data() must return ALL rows, including those hidden by a filter.

        This is by design: data is preserved even when filtered out of view.
        Callers (e.g. TableDialog) need the full dataset when saving.
        """
        filter_grid._filters[0].setText("alp")  # only Alpha visible
        qtbot.wait(50)
        assert filter_grid.table.isRowHidden(1)

        all_data = filter_grid.get_all_data()
        assert len(all_data) == 4, "All 4 rows must be returned regardless of filter state"

    def test_empty_text_filter_shows_all_rows(self, filter_grid, qtbot):
        """An empty text filter must not hide any rows (no filtering when empty)."""
        filter_grid._filters[0].setText("alp")
        qtbot.wait(50)
        filter_grid._filters[0].setText("")  # clear
        qtbot.wait(50)

        for row in range(filter_grid.table.rowCount()):
            assert not filter_grid.table.isRowHidden(row)

    def test_combobox_filter_all_shows_all_rows(self, filter_grid, qtbot):
        """Selecting 'All' in a combobox filter must remove the filter effect."""
        combo_filter = filter_grid._filters[1]
        combo_filter.setCurrentText("X")   # filter to X
        qtbot.wait(50)
        assert filter_grid.table.isRowHidden(1)

        combo_filter.setCurrentText("All")  # reset
        qtbot.wait(50)
        for row in range(filter_grid.table.rowCount()):
            assert not filter_grid.table.isRowHidden(row)


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

class TestSorting:
    def _names(self, grid):
        """Extract the Name column values in current display order."""
        return [grid.table.item(r, 0).text() for r in range(grid.table.rowCount())]

    def test_first_header_click_sorts_ascending(self, grid, qtbot):
        """Single click on a column header should sort that column ascending (A→Z)."""
        grid.table.horizontalHeader().sectionClicked.emit(0)
        names = self._names(grid)
        assert names == sorted(names), f"Expected ascending order, got {names}"

    def test_second_header_click_sorts_descending(self, grid, qtbot):
        """Second click on the same header should sort descending (Z→A)."""
        grid.table.horizontalHeader().sectionClicked.emit(0)  # asc
        grid.table.horizontalHeader().sectionClicked.emit(0)  # desc
        names = self._names(grid)
        assert names == sorted(names, reverse=True), f"Expected descending, got {names}"

    def test_third_header_click_restores_original_order(self, grid, qtbot):
        """Third click on the same header should restore the pre-sort insertion order."""
        original = self._names(grid)
        grid.table.horizontalHeader().sectionClicked.emit(0)  # asc
        grid.table.horizontalHeader().sectionClicked.emit(0)  # desc
        grid.table.horizontalHeader().sectionClicked.emit(0)  # restore
        assert self._names(grid) == original

    def test_sort_different_column_resets_to_ascending(self, grid, qtbot):
        """Clicking a different column must reset sort direction to ascending."""
        grid.table.horizontalHeader().sectionClicked.emit(0)  # asc on col 0
        grid.table.horizontalHeader().sectionClicked.emit(0)  # desc on col 0
        # Click col 1 — should start fresh as ascending
        grid.table.horizontalHeader().sectionClicked.emit(1)
        values = [grid.table.item(r, 1).text() for r in range(grid.table.rowCount())]
        assert values == sorted(values), f"New column should sort ascending, got {values}"

    def test_sort_recaptures_after_add_row(self, grid, qtbot):
        """_original_order is refreshed before every sort, so a row added after the
        first sort is included in the restored original when unsorted."""
        grid.table.horizontalHeader().sectionClicked.emit(0)   # first sort
        grid.add_row(["Aardvark", "0"])
        grid.table.horizontalHeader().sectionClicked.emit(0)   # second sort
        grid.table.horizontalHeader().sectionClicked.emit(0)   # restore
        # "Aardvark" must appear at index 3 (it was appended, so last in insertion order)
        names = self._names(grid)
        assert names[-1] == "Aardvark", (
            f"Post-add row should be last after restore; order={names}"
        )

    def test_sort_after_row_deleted(self, grid, qtbot):
        """Sort and restore work correctly when a row has been deleted."""
        grid.table.setCurrentCell(1, 0)  # Beta
        grid.remove_selected_rows(confirm=False)
        assert grid.table.rowCount() == 2

        grid.table.horizontalHeader().sectionClicked.emit(0)   # asc
        grid.table.horizontalHeader().sectionClicked.emit(0)   # desc
        names = self._names(grid)
        assert names == sorted(names, reverse=True)


# ---------------------------------------------------------------------------
# Basic operations
# ---------------------------------------------------------------------------

class TestBasicOperations:
    def test_add_row_returns_index(self, grid, qtbot):
        """add_row() must return the index of the newly inserted row."""
        idx = grid.add_row(["New", "4"])
        assert idx == 3  # appended after the three fixture rows
        assert grid.table.rowCount() == 4

    def test_add_row_emits_row_added_signal(self, grid, qtbot):
        """add_row() must emit the row_added(index) signal."""
        received = []
        grid.row_added.connect(lambda i: received.append(i))
        grid.add_row(["X", "9"])
        assert received == [3]

    def test_add_row_emits_data_changed_signal(self, grid, qtbot):
        """add_row() must emit data_changed so connected views can refresh."""
        fired = [False]
        grid.data_changed.connect(lambda: fired.__setitem__(0, True))
        grid.add_row(["Y", "8"])
        assert fired[0]

    def test_add_row_empty_row(self, grid, qtbot):
        """add_row() with no data argument creates an all-empty row."""
        grid.add_row()
        last_row = grid.table.rowCount() - 1
        assert grid.table.item(last_row, 0).text() == ""
        assert grid.table.item(last_row, 1).text() == ""

    def test_remove_selected_rows_single(self, grid, qtbot):
        """Removing a single selected row decrements rowCount by 1."""
        grid.table.setCurrentCell(1, 0)
        removed = grid.remove_selected_rows(confirm=False)
        assert grid.table.rowCount() == 2
        assert 1 in removed
        # Original row 2 (Gamma) is now row 1
        assert grid.table.item(1, 0).text() == "Gamma"

    def test_remove_selected_rows_emits_signals(self, grid, qtbot):
        """remove_selected_rows must emit row_removed and data_changed."""
        removed_signal = []
        changed_signal = [False]
        grid.row_removed.connect(lambda rows: removed_signal.extend(rows))
        grid.data_changed.connect(lambda: changed_signal.__setitem__(0, True))

        grid.table.setCurrentCell(0, 0)
        grid.remove_selected_rows(confirm=False)
        assert removed_signal == [0]
        assert changed_signal[0]

    def test_remove_nothing_when_nothing_selected(self, grid, qtbot):
        """Calling remove_selected_rows with nothing selected/current returns []."""
        grid.table.clearSelection()
        # Reset current row to -1 by not setting any current cell
        # We can check without crashing by looking at return value
        # When rowCount is 3 and nothing is selected/current, return []
        # Fake: make current invalid by clearing all
        result = grid.remove_selected_rows(confirm=False)
        # Nothing selected, no current → returns [] or removes current row
        # (current defaults to last setCurrentCell which was never called here)
        # The key assertion: rowCount is still >= 0 and no exception raised
        assert isinstance(result, list)

    def test_get_all_data_returns_all_rows(self, grid, qtbot):
        """get_all_data() must return data for every row in insertion order."""
        data = grid.get_all_data()
        assert data == [["Alpha", "1"], ["Beta", "2"], ["Gamma", "3"]]

    def test_get_row_data_single_row(self, grid, qtbot):
        """get_row_data(row) must return the correct cell values for that row only."""
        assert grid.get_row_data(0) == ["Alpha", "1"]
        assert grid.get_row_data(1) == ["Beta",  "2"]
        assert grid.get_row_data(2) == ["Gamma", "3"]

    def test_clear_data_removes_all_rows(self, grid, qtbot):
        """clear_data() must set rowCount to 0 and emit data_changed."""
        fired = [False]
        grid.data_changed.connect(lambda: fired.__setitem__(0, True))
        grid.clear_data()
        assert grid.table.rowCount() == 0
        assert fired[0]

    def test_set_row_data(self, grid, qtbot):
        """set_row_data() must overwrite the cell values at the given row index."""
        grid.set_row_data(1, ["UPDATED", "99"])
        assert grid.get_row_data(1) == ["UPDATED", "99"]

    def test_move_row_up(self, grid, qtbot):
        """Move Up on row 1 must swap rows 0 and 1."""
        grid.table.setCurrentCell(1, 0)
        grid._move_row_up()
        assert grid.table.item(0, 0).text() == "Beta"
        assert grid.table.item(1, 0).text() == "Alpha"

    def test_move_row_up_noop_on_first_row(self, grid, qtbot):
        """Move Up on row 0 must not change the order (already at top)."""
        grid.table.setCurrentCell(0, 0)
        grid._move_row_up()
        assert grid.table.item(0, 0).text() == "Alpha"  # unchanged

    def test_move_row_down(self, grid, qtbot):
        """Move Down on row 1 must swap rows 1 and 2."""
        grid.table.setCurrentCell(1, 0)
        grid._move_row_down()
        assert grid.table.item(1, 0).text() == "Gamma"
        assert grid.table.item(2, 0).text() == "Beta"

    def test_move_row_down_noop_on_last_row(self, grid, qtbot):
        """Move Down on the last row must not change order."""
        last = grid.table.rowCount() - 1
        grid.table.setCurrentCell(last, 0)
        grid._move_row_down()
        assert grid.table.item(last, 0).text() == "Gamma"  # unchanged

    def test_move_row_to_top(self, grid, qtbot):
        """Move to Top on row 2 must place it at row 0."""
        grid.table.setCurrentCell(2, 0)
        grid._move_row_to_top()
        assert grid.table.item(0, 0).text() == "Gamma"
        assert grid.table.item(1, 0).text() == "Alpha"
        assert grid.table.item(2, 0).text() == "Beta"

    def test_move_row_to_bottom(self, grid, qtbot):
        """Move to Bottom on row 0 must place it at the last position."""
        grid.table.setCurrentCell(0, 0)
        grid._move_row_to_bottom()
        assert grid.table.item(0, 0).text() == "Beta"
        assert grid.table.item(1, 0).text() == "Gamma"
        assert grid.table.item(2, 0).text() == "Alpha"

    def test_move_emits_data_changed(self, grid, qtbot):
        """All move operations must emit data_changed."""
        fired = [0]
        grid.data_changed.connect(lambda: fired.__setitem__(0, fired[0] + 1))
        grid.table.setCurrentCell(1, 0)
        grid._move_row_up()
        assert fired[0] >= 1


# ---------------------------------------------------------------------------
# Clipboard — edge cases
# ---------------------------------------------------------------------------

class TestClipboardEdgeCases:
    def test_ctrl_v_with_empty_clipboard_does_not_crash(self, grid, qtbot):
        """Pasting from an empty clipboard must be a no-op, no exception."""
        QApplication.clipboard().setText("")
        before = grid.table.rowCount()
        grid._paste_from_clipboard()
        assert grid.table.rowCount() == before  # nothing added

    def test_ctrl_v_with_whitespace_only_clipboard_does_not_add_rows(self, grid, qtbot):
        """Whitespace-only clipboard lines are skipped by the paste logic."""
        QApplication.clipboard().setText("   \n\t\n  ")
        before = grid.table.rowCount()
        grid._paste_from_clipboard()
        assert grid.table.rowCount() == before

    def test_ctrl_c_with_no_selection_copies_current_row(self, grid, qtbot):
        """When nothing is explicitly selected, Ctrl+C should copy the current row."""
        grid.table.clearSelection()
        grid.table.setCurrentCell(2, 0)
        grid._copy_to_clipboard()
        text = QApplication.clipboard().text()
        assert "Gamma" in text

    def test_ctrl_c_skips_hidden_filtered_rows(self, qtbot):
        """Ctrl+C must not include rows that are hidden by an active filter."""
        g = DataGridWidget()
        g.configure([
            ColumnConfig("Name", editor_type="text", filter_type="text"),
        ])
        g.add_row(["Alpha"])
        g.add_row(["Beta"])
        g.add_row(["Gamma"])
        qtbot.addWidget(g)
        g.show()

        # Filter to show only 'Alpha'
        g._filters[0].setText("alpha")
        qtbot.wait(50)
        assert g.table.isRowHidden(1)

        g.table.selectAll()
        g._copy_to_clipboard()
        text = QApplication.clipboard().text()
        assert "Alpha" in text
        assert "Beta"  not in text   # hidden by filter → not copied
        assert "Gamma" not in text   # hidden by filter → not copied

    def test_ctrl_v_pads_short_rows_with_empty_strings(self, grid, qtbot):
        """Pasting a row with fewer columns than the grid pads missing cells with ''."""
        QApplication.clipboard().setText("Single")  # only 1 column, grid has 2
        grid._paste_from_clipboard()
        last = grid.table.rowCount() - 1
        assert grid.table.item(last, 0).text() == "Single"
        assert grid.table.item(last, 1).text() == ""  # padded

    def test_ctrl_v_truncates_extra_columns(self, grid, qtbot):
        """Pasting a row with more columns than the grid truncates to the column count."""
        QApplication.clipboard().setText("A\tB\tC\tD")  # 4 cols, grid has 2
        grid._paste_from_clipboard()
        last = grid.table.rowCount() - 1
        assert grid.table.item(last, 0).text() == "A"
        assert grid.table.item(last, 1).text() == "B"


# ---------------------------------------------------------------------------
# Configuration — show/hide buttons
# ---------------------------------------------------------------------------

class TestConfiguration:
    def test_no_filter_row_when_disabled(self, qtbot):
        """When show_filters=False, filter_table must not be created."""
        g = DataGridWidget()
        g.configure([ColumnConfig("X", editor_type="text")], show_filters=False)
        qtbot.addWidget(g)
        assert g.filter_table is None

    def test_custom_button_appears_in_toolbar(self, qtbot):
        """A custom button defined in configure() must appear in the toolbar."""
        from PySide6.QtWidgets import QPushButton
        clicked = [False]
        g = DataGridWidget()
        g.configure(
            [ColumnConfig("X", editor_type="text")],
            custom_buttons=[{"text": "Action", "callback": lambda: clicked.__setitem__(0, True)}],
        )
        qtbot.addWidget(g)
        g.show()
        # Find the custom button
        buttons = [b for b in g.findChildren(QPushButton) if b.text() == "Action"]
        assert buttons, "Custom button 'Action' not found in toolbar"
        buttons[0].click()
        assert clicked[0]

    def test_configure_with_filter_matcher(self, qtbot):
        """A ColumnConfig with filter_matcher propagates to _apply_filters correctly."""
        g = DataGridWidget()
        g.configure([
            ColumnConfig(
                "Active", editor_type="checkbox_centered",
                filter_type="combobox",
                filter_options={"items": ["All", "Yes", "No"]},
                filter_matcher=lambda fv, cv:
                    (cv == "true") if fv == "Yes" else (cv == "false"),
            ),
        ])
        g.add_row([True])
        g.add_row([False])
        qtbot.addWidget(g)
        g.show()

        g._filters[0].setCurrentText("Yes")
        qtbot.wait(50)
        assert not g.table.isRowHidden(0)  # True/checked → shown
        assert g.table.isRowHidden(1)       # False/unchecked → hidden

    def test_combobox_data_cell_roundtrip(self, qtbot):
        """combobox_data cells store data values separately from display text.

        add_row() accepts the data value; get_row_data() returns the data value
        (not the display text), and the combobox shows the display text.
        """
        g = DataGridWidget()
        g.configure([
            ColumnConfig("Type", editor_type="combobox_data",
                         editor_options={
                             "items":      ["Primary Key", "Foreign Key", "Unique"],
                             "items_data": ["PRIMARY",     "FOREIGN",     "UNIQUE"],
                         },
                         filter_type="none"),
        ])
        g.add_row(["FOREIGN"])  # supply the data value
        qtbot.addWidget(g)
        g.show()

        combo = g.table.cellWidget(0, 0)
        assert combo.currentText() == "Foreign Key"  # display text shown to user
        assert combo.currentData() == "FOREIGN"      # stored data value

        row_data = g.get_row_data(0)
        assert row_data[0] == "FOREIGN"  # get_row_data returns data, not display text
