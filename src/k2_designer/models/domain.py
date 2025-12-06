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


from typing import Optional
from .base import DatabaseObject


class Domain(DatabaseObject):
    """Domain definition for used data types."""
    
    def __init__(self, name: str, data_type: str, comment: Optional[str] = None, guid: Optional[str] = None):
        super().__init__(name, comment, guid)
        self.data_type = data_type
    
    def to_dict(self) -> dict:
        return {
            'guid': self.guid,
            'name': self.name,
            'data_type': self.data_type,
            'comment': self.comment
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data['name'],
            data_type=data['data_type'],
            comment=data.get('comment'),
            guid=data.get('guid')
        )
    
    def __str__(self) -> str:
        return f"Domain({self.name}: {self.data_type})"
    
    def __repr__(self) -> str:
        return f"Domain(name='{self.name}', data_type='{self.data_type}', comment='{self.comment}')"