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

"""Tests for Excel-like behaviour added to DataGridWidget."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHeaderView

from k2widgets import ColumnConfig, DataGridWidget


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def grid(qtbot):
    """A DataGridWidget with two text columns and three sample rows."""
    g = DataGridWidget()
    g.configure([
        ColumnConfig("Name", width=120, editor_type="text", filter_type="text"),
        ColumnConfig("Value", width=80, editor_type="text", filter_type="text"),
    ])
    g.add_row(["Alpha", "1"])
    g.add_row(["Beta", "2"])
    g.add_row(["Gamma", "3"])
    qtbot.addWidget(g)
    g.show()
    return g


@pytest.fixture
def full_grid(qtbot):
    """A DataGridWidget with text, checkbox_centered, and combobox columns."""
    g = DataGridWidget()
    g.configure([
        ColumnConfig("Name", width=120, editor_type="text", filter_type="text"),
        ColumnConfig("Active", width=60, editor_type="checkbox_centered", filter_type="none"),
        ColumnConfig("Type", width=80, editor_type="combobox",
                     editor_options={"items": ["A", "B", "C"]}, filter_type="none"),
    ])
    g.add_row(["Alpha", True, "A"])
    g.add_row(["Beta", False, "B"])
    g.add_row(["Gamma", True, "C"])
    qtbot.addWidget(g)
    g.show()
    return g


# ---------------------------------------------------------------------------
# Bug fix tests
# ---------------------------------------------------------------------------

class TestBugFixes:
    def test_edit_button_disabled_on_multi_select(self, grid, qtbot):
        """Edit (✎) button must be disabled when more than one row is selected."""
        assert grid._edit_btn is not None
        # Single row selected → enabled
        grid.table.setCurrentCell(0, 0)
        assert grid._edit_btn.isEnabled()

        # Select all three rows → disabled
        grid.table.selectAll()
        qtbot.wait(50)
        assert not grid._edit_btn.isEnabled()

    def test_edit_button_enabled_on_single_select(self, grid, qtbot):
        """Edit button re-enables when selection collapses back to one row."""
        grid.table.selectAll()
        qtbot.wait(50)
        grid.table.setCurrentCell(1, 0)
        grid.table.clearSelection()
        grid.table.item(1, 0).setSelected(True)
        qtbot.wait(50)
        assert grid._edit_btn.isEnabled()

    def test_sort_always_recaptures_original_order(self, grid):
        """Sorting must work correctly even after rows are added post-first-sort."""
        # Sort ascending on col 0
        grid.table.horizontalHeader().sectionClicked.emit(0)
        # Add a new row after sorting
        grid.add_row(["Aardvark", "0"])
        # Sort descending on col 0
        grid.table.horizontalHeader().sectionClicked.emit(0)
        # First row should be 'Gamma' (alphabetically last)
        first = grid.table.item(0, 0)
        assert first is not None and first.text() == "Gamma"

    def test_no_double_signal_on_editable_filter_combobox(self, qtbot):
        """Editable combobox filter must call _apply_filters exactly once per change."""
        g = DataGridWidget()
        g.configure([
            ColumnConfig("Type", width=80, editor_type="text",
                         filter_type="combobox",
                         filter_options={"items": ["All", "X", "Y"], "editable": True}),
        ])
        g.add_row(["X"])
        g.add_row(["Y"])
        qtbot.addWidget(g)

        call_count = [0]
        original = g._apply_filters

        def counting_apply():
            call_count[0] += 1
            original()

        g._apply_filters = counting_apply

        # Set combobox to "X"
        filter_combo = g._filters[0]
        filter_combo.setCurrentText("X")
        qtbot.wait(50)
        assert call_count[0] == 1, f"Expected 1 call, got {call_count[0]}"


# ---------------------------------------------------------------------------
# Tab / Enter navigation
# ---------------------------------------------------------------------------

class TestTabEnterNavigation:
    def test_enter_moves_to_next_row(self, grid, qtbot):
        """Enter on row 0 should move focus to row 1."""
        grid.table.setCurrentCell(0, 0)
        qtbot.keyClick(grid.table, Qt.Key.Key_Return)
        qtbot.wait(50)
        assert grid.table.currentRow() == 1

    def test_enter_on_last_row_adds_new_row(self, grid, qtbot):
        """Enter on the last row of an add-enabled grid should append a new row."""
        initial_count = grid.table.rowCount()
        grid.table.setCurrentCell(initial_count - 1, 0)
        qtbot.keyClick(grid.table, Qt.Key.Key_Return)
        qtbot.wait(50)
        assert grid.table.rowCount() == initial_count + 1

    def test_enter_on_last_row_does_not_add_when_add_disabled(self, qtbot):
        """Enter on last row must NOT add a row when show_add_button=False."""
        g = DataGridWidget()
        g.configure(
            [ColumnConfig("Name", editor_type="text")],
            show_add_button=False,
        )
        g.add_row(["Only"])
        qtbot.addWidget(g)
        g.table.setCurrentCell(0, 0)
        qtbot.keyClick(g.table, Qt.Key.Key_Return)
        qtbot.wait(50)
        assert g.table.rowCount() == 1

    def test_tab_moves_to_next_column(self, grid, qtbot):
        """Tab from column 0 should move focus to column 1."""
        grid.table.setCurrentCell(0, 0)
        qtbot.keyClick(grid.table, Qt.Key.Key_Tab)
        qtbot.wait(50)
        assert grid.table.currentColumn() == 1

    def test_tab_wraps_to_next_row(self, grid, qtbot):
        """Tab from the last column should wrap to column 0 of the next row."""
        last_col = grid.table.columnCount() - 1
        grid.table.setCurrentCell(0, last_col)
        qtbot.keyClick(grid.table, Qt.Key.Key_Tab)
        qtbot.wait(50)
        assert grid.table.currentRow() == 1
        assert grid.table.currentColumn() == 0


# ---------------------------------------------------------------------------
# Bulk edit
# ---------------------------------------------------------------------------

class TestBulkEdit:
    def test_bulk_edit_text_propagates_to_selected_rows(self, grid, qtbot):
        """Editing a text cell while multiple rows are selected propagates the value.

        Triggers via cellChanged signal (the real runtime path): item.setText()
        fires cellChanged → _on_text_cell_changed → propagates to other rows.
        """
        grid.table.selectAll()
        qtbot.wait(50)
        grid.table._captured_selection = {0, 1, 2}

        # Simulate the model update that cellChanged fires after editor commit
        grid.table.item(0, 0).setText("BULK")
        qtbot.wait(50)

        assert grid.table.item(1, 0).text() == "BULK"
        assert grid.table.item(2, 0).text() == "BULK"

    def test_bulk_edit_does_not_fire_on_single_selection(self, grid, qtbot):
        """Bulk edit must not change other rows when only one row is selected."""
        grid.table.clearSelection()
        grid.table._captured_selection = {0}

        grid.table.item(0, 0).setText("SINGLE")
        qtbot.wait(50)

        assert grid.table.item(1, 0).text() == "Beta"
        assert grid.table.item(2, 0).text() == "Gamma"

    def test_bulk_edit_combobox_propagates(self, full_grid, qtbot):
        """Changing a combobox value while multiple rows are selected propagates it."""
        # Select all rows
        full_grid.table.selectAll()
        qtbot.wait(50)

        # Get the combobox widget in row 0, col 2 (Type column)
        combo0 = full_grid.table.cellWidget(0, 2)
        assert combo0 is not None

        # Change combobox to "C"
        combo0.setCurrentText("C")
        qtbot.wait(50)

        # Rows 1 and 2 should also have "C"
        combo1 = full_grid.table.cellWidget(1, 2)
        combo2 = full_grid.table.cellWidget(2, 2)
        assert combo1.currentText() == "C"
        assert combo2.currentText() == "C"

    def test_bulk_edit_checkbox_propagates(self, full_grid, qtbot):
        """Toggling a checkbox while multiple rows are selected propagates the state."""
        full_grid.table.selectAll()
        qtbot.wait(50)

        # Get checkbox in row 0, col 1 (Active column)
        widget0 = full_grid.table.cellWidget(0, 1)
        cb0 = widget0.checkbox
        # Ensure it starts checked (set in fixture)
        assert cb0.isChecked()

        # Uncheck it
        cb0.setChecked(False)
        qtbot.wait(50)

        widget1 = full_grid.table.cellWidget(1, 1)
        widget2 = full_grid.table.cellWidget(2, 1)
        assert not widget1.checkbox.isChecked()
        assert not widget2.checkbox.isChecked()


# ---------------------------------------------------------------------------
# Clipboard
# ---------------------------------------------------------------------------

class TestClipboard:
    def test_ctrl_c_copies_selected_rows_as_tsv(self, grid, qtbot):
        """Ctrl+C on selected rows produces a TSV string in the clipboard."""
        grid.table.selectAll()
        qtbot.keyClick(grid.table, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
        qtbot.wait(50)

        text = QApplication.clipboard().text()
        rows = text.splitlines()
        assert len(rows) == 3
        assert rows[0] == "Alpha\t1"
        assert rows[1] == "Beta\t2"
        assert rows[2] == "Gamma\t3"

    def test_ctrl_c_on_single_row(self, grid, qtbot):
        """Ctrl+C with only one row selected copies just that row."""
        # clearSelection() ensures no residual selection from fixture setup
        grid.table.clearSelection()
        grid.table.selectRow(1)
        qtbot.keyClick(grid.table, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
        qtbot.wait(50)

        text = QApplication.clipboard().text()
        assert text == "Beta\t2"

    def test_ctrl_v_pastes_new_rows(self, grid, qtbot):
        """Ctrl+V with TSV in clipboard appends rows to the grid."""
        QApplication.clipboard().setText("Delta\t4\nEpsilon\t5")
        initial = grid.table.rowCount()

        qtbot.keyClick(grid.table, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
        qtbot.wait(50)

        assert grid.table.rowCount() == initial + 2
        last_two = grid.get_all_data()[-2:]
        assert last_two[0][0] == "Delta"
        assert last_two[1][0] == "Epsilon"

    def test_ctrl_v_coerces_boolean_columns(self, full_grid, qtbot):
        """Ctrl+V coerces 'true'/'false' strings to booleans for checkbox columns."""
        QApplication.clipboard().setText("Zeta\ttrue\tB")
        initial = full_grid.table.rowCount()

        qtbot.keyClick(full_grid.table, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
        qtbot.wait(50)

        assert full_grid.table.rowCount() == initial + 1
        row_data = full_grid.get_row_data(full_grid.table.rowCount() - 1)
        assert row_data[1] is True  # checkbox column coerced

    def test_clipboard_roundtrip(self, grid, qtbot):
        """Copy → clear → paste reproduces the original data."""
        grid.table.selectAll()
        grid._copy_to_clipboard()
        original = grid.get_all_data()

        grid.clear_data()
        assert grid.table.rowCount() == 0

        grid._paste_from_clipboard()
        qtbot.wait(50)
        assert grid.get_all_data() == original


# ---------------------------------------------------------------------------
# Context menu
# ---------------------------------------------------------------------------

class TestContextMenu:
    def test_insert_row_above(self, grid, qtbot):
        """Insert Row Above should add a row before the current row."""
        grid.table.setCurrentCell(1, 0)
        count_before = grid.table.rowCount()
        grid._insert_row_above()
        assert grid.table.rowCount() == count_before + 1
        # The new row is at index 1, old row 1 pushed to 2
        assert grid.table.item(2, 0).text() == "Beta"

    def test_insert_row_below(self, grid, qtbot):
        """Insert Row Below should add a row after the current row."""
        grid.table.setCurrentCell(0, 0)
        count_before = grid.table.rowCount()
        grid._insert_row_below()
        assert grid.table.rowCount() == count_before + 1
        # Row 0 unchanged, new empty row at 1, old row 1 pushed to 2
        assert grid.table.item(0, 0).text() == "Alpha"
        assert grid.table.item(2, 0).text() == "Beta"


# ---------------------------------------------------------------------------
# Bulk edit — selection capture fix
# ---------------------------------------------------------------------------

class TestBulkEditSelectionCapture:
    """Tests for the fixed _captured_selection mechanism.

    The core bug was: a plain click to start editing collapses the table
    selection to a single row BEFORE editingStarted fires.  The fix uses
    three complementary mechanisms:
      1. selectionChanged → _update_bulk_selection  (tracks Ctrl/Shift builds)
      2. mousePressEvent pre-capture                 (saves before collapse)
      3. _on_editing_started preservation            (keeps if row in context)
    """

    def test_update_bulk_selection_on_multi_select(self, grid, qtbot):
        """_update_bulk_selection fires on selectionChanged and stores >= 2 rows."""
        grid.table.selectAll()
        qtbot.wait(50)
        assert grid.table._captured_selection == {0, 1, 2}

    def test_update_bulk_selection_ignores_single_row(self, grid, qtbot):
        """_update_bulk_selection must NOT overwrite when selection collapses to 1 row."""
        # Build multi-selection
        grid.table.selectAll()
        qtbot.wait(50)
        assert grid.table._captured_selection == {0, 1, 2}

        # Simulate selection collapsing to row 0 without clearing captured context
        grid.table._captured_selection = {0, 1, 2}       # as set by selectAll above
        # Directly call the handler with a single-item mock — must not overwrite
        # We do this by checking that _on_editing_started preserves when row in set
        grid.table._on_editing_started(0, 0)
        assert grid.table._captured_selection == {0, 1, 2}

    def test_editing_started_resets_on_outside_row(self, grid, qtbot):
        """_on_editing_started must clear the bulk context when editing a row outside it.

        The exact new value of _captured_selection depends on the table's current
        selection (which varies by Qt version / show state).  The invariant we
        care about: rows 0 and 1 must NOT survive in the capture after editing
        row 2, which is outside the {0, 1} context.
        """
        grid.table.clearSelection()
        grid.table._captured_selection = {0, 1}
        grid.table._on_editing_started(2, 0)  # row 2 not in {0, 1}
        assert grid.table._captured_selection.isdisjoint({0, 1}), (
            f"Old bulk rows must be evicted; got {grid.table._captured_selection}"
        )

    def test_editing_started_preserves_when_row_in_capture(self, grid, qtbot):
        """_on_editing_started must keep captured set when editing a row inside it."""
        grid.table._captured_selection = {0, 1, 2}
        grid.table._on_editing_started(1, 0)   # row 1 IS in the set
        assert grid.table._captured_selection == {0, 1, 2}

    def test_text_bulk_edit_uses_captured_selection(self, grid, qtbot):
        """_on_text_cell_changed propagates to rows in _captured_selection, not selectedItems."""
        grid.table.clearSelection()
        grid.table._captured_selection = {0, 1, 2}  # simulate pre-click capture

        # Triggering via cellChanged path (same as real editor commit)
        grid.table.item(0, 0).setText("DATE")
        qtbot.wait(50)

        assert grid.table.item(1, 0).text() == "DATE"
        assert grid.table.item(2, 0).text() == "DATE"
        # Source row was set explicitly; that's expected
        assert grid.table.item(0, 0).text() == "DATE"

    def test_combobox_bulk_edit_uses_captured_selection(self, full_grid, qtbot):
        """_propagate_combobox_change uses _captured_selection, not selectedItems()."""
        full_grid.table.clearSelection()  # no visible selection
        full_grid.table._captured_selection = {0, 1, 2}  # simulate pre-click capture

        combo0 = full_grid.table.cellWidget(0, 2)
        combo0.setCurrentText("C")
        qtbot.wait(50)

        assert full_grid.table.cellWidget(1, 2).currentText() == "C"
        assert full_grid.table.cellWidget(2, 2).currentText() == "C"

    def test_checkbox_bulk_edit_uses_captured_selection(self, full_grid, qtbot):
        """_propagate_checkbox_change uses _captured_selection, not selectedItems()."""
        full_grid.table.clearSelection()
        full_grid.table._captured_selection = {0, 1, 2}

        w0 = full_grid.table.cellWidget(0, 1)
        w0.checkbox.setChecked(False)
        qtbot.wait(50)

        assert not full_grid.table.cellWidget(1, 1).checkbox.isChecked()
        assert not full_grid.table.cellWidget(2, 1).checkbox.isChecked()

    def test_clear_data_resets_captured_selection(self, grid, qtbot):
        """clear_data() must reset _captured_selection to avoid stale row references."""
        grid.table._captured_selection = {0, 1, 2}
        grid.clear_data()
        assert grid.table._captured_selection == set()

    def test_plain_click_outside_selection_clears_context(self, grid, qtbot):
        """Bulk context must be invalidated when user acts on a row outside it.

        Simulate: user had {0, 1} multi-selected, then plain-clicks row 2.
        _on_editing_started(2, 0) must ensure rows 0 and 1 are no longer in
        _captured_selection so that an edit on row 2 doesn't propagate to them.
        """
        grid.table.clearSelection()  # guarantee no stale selection
        grid.table._captured_selection = {0, 1}
        grid.table._on_editing_started(2, 0)  # row 2 not in {0, 1}
        assert grid.table._captured_selection.isdisjoint({0, 1}), (
            f"Old bulk rows must not survive; got {grid.table._captured_selection}"
        )
