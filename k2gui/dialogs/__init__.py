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


from .about_dialog import AboutDialog, SplashScreen
from .diagram_dialog import DiagramDialog
from .domain_dialog import DomainDialog
from .generate_dialog import GenerateDialog
from .key_dialog import KeyDialog
from .new_project_dialog import NewProjectDialog
from .owner_dialog import OwnerDialog
from .project_settings_dialog import ProjectSettingsDialog
from .sequence_dialog import SequenceDialog
from .table_dialog import TableDialog

__all__ = ['DomainDialog', 'OwnerDialog', 'TableDialog', 'SequenceDialog',
           'DiagramDialog', 'NewProjectDialog', 'GenerateDialog', 'ProjectSettingsDialog',
           'AboutDialog', 'SplashScreen', 'KeyDialog']
