"""
Test script to verify DataGridWidget can be imported and instantiated.
"""

import sys

def test_imports():
    """Test that all components can be imported."""
    print("Testing imports...")

    try:
        from src.k2_designer.widgets import DataGridWidget, ColumnConfig
        print("✓ DataGridWidget and ColumnConfig imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False

    try:
        from PyQt6.QtWidgets import QHeaderView
        print("✓ PyQt6 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyQt6: {e}")
        return False

    return True


def test_column_config():
    """Test ColumnConfig creation."""
    print("\nTesting ColumnConfig...")

    from src.k2_designer.widgets import ColumnConfig
    from PyQt6.QtWidgets import QHeaderView

    try:
        col = ColumnConfig(
            name="Test Column",
            width=150,
            resize_mode=QHeaderView.ResizeMode.Interactive,
            editor_type="text",
            filter_type="text"
        )
        print(f"✓ ColumnConfig created: {col.name}")
        print(f"  - Width: {col.width}")
        print(f"  - Editor type: {col.editor_type}")
        print(f"  - Filter type: {col.filter_type}")
        return True
    except Exception as e:
        print(f"✗ Failed to create ColumnConfig: {e}")
        return False


def test_structure():
    """Test DataGridWidget structure without GUI."""
    print("\nTesting DataGridWidget structure...")

    from src.k2_designer.widgets import DataGridWidget

    # Check that the class has expected methods
    expected_methods = [
        'configure',
        'add_row',
        'remove_selected_rows',
        'get_row_data',
        'get_all_data',
        'set_row_data',
        'clear_data',
        'set_add_callback',
        'set_edit_callback',
        'set_remove_callback',
        'set_cell_setup_callback'
    ]

    all_good = True
    for method in expected_methods:
        if hasattr(DataGridWidget, method):
            print(f"✓ Method '{method}' exists")
        else:
            print(f"✗ Method '{method}' missing")
            all_good = False

    # Check for expected signals
    expected_signals = ['data_changed', 'row_added', 'row_removed', 'row_moved']
    for signal in expected_signals:
        if hasattr(DataGridWidget, signal):
            print(f"✓ Signal '{signal}' exists")
        else:
            print(f"✗ Signal '{signal}' missing")
            all_good = False

    return all_good


def main():
    """Run all tests."""
    print("=" * 60)
    print("DataGridWidget Test Suite")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("ColumnConfig", test_column_config),
        ("Structure", test_structure),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(result for _, result in results)
    print("\n" + ("=" * 60))
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

