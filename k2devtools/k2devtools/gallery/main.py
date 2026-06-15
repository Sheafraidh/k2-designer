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

"""
Component gallery — launch with:
    uv run python -m k2devtools.gallery.main
    uv run python -m k2devtools.gallery.main --keys
    uv run python -m k2devtools.gallery.main --indexes
    uv run python -m k2devtools.gallery.main --columns  (default)
"""

import sys

from PySide6.QtWidgets import QApplication

from .data_grid_examples import (
    ColumnsGridExample,
    ExcelFeaturesDemo,
    IndexesGridExample,
    KeysGridExample,
)


def main() -> None:
    app = QApplication(sys.argv)

    args = sys.argv[1:]

    if "--keys" in args:
        dialog = KeysGridExample()
    elif "--indexes" in args:
        dialog = IndexesGridExample()
    elif "--excel" in args:
        dialog = ExcelFeaturesDemo()
    else:
        # Default: columns demo (most feature-rich)
        dialog = ColumnsGridExample(
            available_domains=["ID_DOMAIN", "NAME_DOMAIN", "DATE_DOMAIN"],
            available_stereotypes=["PK", "FK", "AUDIT"],
        )

    dialog.exec()
    sys.exit(0)


if __name__ == "__main__":
    main()
