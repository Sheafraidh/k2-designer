#!/usr/bin/env python3
"""
Script to add license headers to all Python source files in K2 Designer.

Copyright (c) 2025 Karel Švejnoha
"""

import os
import glob

LICENSE_HEADER = '''"""
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
'''

def add_license_header(file_path):
    """Add license header to a Python file if it doesn't already have one."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has copyright notice
    if 'Copyright (c) 2025 Karel Švejnoha' in content:
        print(f"✓ Already has license: {file_path}")
        return False

    # Find existing docstring
    lines = content.split('\n')

    # Check if file starts with docstring
    if lines and lines[0].startswith('"""'):
        # Find end of docstring
        docstring_end = -1
        for i in range(1, len(lines)):
            if '"""' in lines[i]:
                docstring_end = i
                break

        if docstring_end > 0:
            # Replace the docstring with license header + rest of file
            rest_of_file = '\n'.join(lines[docstring_end + 1:])
            new_content = LICENSE_HEADER + '\n' + rest_of_file
        else:
            # Malformed docstring, just prepend
            new_content = LICENSE_HEADER + '\n' + content
    else:
        # No docstring, just prepend
        new_content = LICENSE_HEADER + '\n' + content

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✓ Added license: {file_path}")
    return True

def main():
    """Add license headers to all Python files."""

    # Find all Python files in src/
    py_files = glob.glob('src/**/*.py', recursive=True)

    # Also add to test files and scripts
    py_files.extend(glob.glob('*.py'))
    # py_files.extend(glob.glob('tests/**/*.py', recursive=True))
    # py_files.extend(glob.glob('scripts/**/*.py', recursive=True))

    # Remove duplicates
    py_files = list(set(py_files))

    print(f"Found {len(py_files)} Python files")
    print("=" * 60)

    updated = 0
    skipped = 0

    for py_file in sorted(py_files):
        if add_license_header(py_file):
            updated += 1
        else:
            skipped += 1

    print("=" * 60)
    print(f"✓ Updated: {updated} files")
    print(f"✓ Skipped: {skipped} files (already had license)")
    print(f"✓ Total: {len(py_files)} files")

if __name__ == '__main__':
    main()

