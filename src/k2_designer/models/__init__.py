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


from .base import Column, DatabaseObject, Index, Key, Partitioning, PartitionType, Stereotype
from .diagram import Diagram, DiagramItem
from .domain import Domain
from .owner import Owner
from .project import Project
from .sequence import Sequence
from .table import Table

__all__ = [
    'DatabaseObject', 'Column', 'Key', 'Index', 'Partitioning',
    'Stereotype', 'PartitionType', 'Domain', 'Owner',
    'Table', 'Sequence', 'Diagram', 'DiagramItem', 'Project'
]
