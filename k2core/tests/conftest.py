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

import json
from pathlib import Path

import pytest

from k2core.models.base import Column, Index, Key, KeyType, Partitioning, PartitionType
from k2core.models.table import Table

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def minimal_column():
    return Column(name="ID", data_type="NUMBER")


@pytest.fixture
def full_column():
    return Column(
        name="USERNAME",
        data_type="VARCHAR2(100)",
        nullable=False,
        comment="Login name",
        default="'guest'",
        domain="VARCHAR2(100)",
        stereotype="Business",
        guid="c0000000-0000-0000-0000-000000000001",
    )


@pytest.fixture
def pk_key():
    return Key(
        name="PK_USERS",
        columns=["ID"],
        key_type=KeyType.PRIMARY,
        guid="k0000000-0000-0000-0000-000000000001",
    )


@pytest.fixture
def fk_key():
    return Key(
        name="FK_ORDERS_USER",
        columns=["USER_ID"],
        key_type=KeyType.FOREIGN,
        referenced_table="APP.USERS",
        referenced_columns=["ID"],
        on_delete="CASCADE",
        guid="k0000000-0000-0000-0000-000000000002",
    )


@pytest.fixture
def multi_col_index():
    return Index(
        name="IDX_COMPOSITE",
        columns=["LAST_NAME", "FIRST_NAME"],
        tablespace="INDX",
        guid="i0000000-0000-0000-0000-000000000001",
    )


@pytest.fixture
def range_partitioning():
    return Partitioning(columns=["CREATED_AT"], partition_type=PartitionType.RANGE)


@pytest.fixture
def simple_table():
    t = Table(name="USERS", owner="APP", guid="t0000000-0000-0000-0000-000000000001")
    t.add_column(Column(name="ID", data_type="NUMBER", nullable=False))
    t.add_column(Column(name="USERNAME", data_type="VARCHAR2(100)", nullable=False))
    t.add_key(Key(name="PK_USERS", columns=["ID"], key_type=KeyType.PRIMARY))
    t.add_index(Index(name="IDX_USERS_USERNAME", columns=["USERNAME"], tablespace="INDX"))
    return t


@pytest.fixture
def fixture_project_dict():
    return json.loads((FIXTURES_DIR / "test_project.k2p").read_text())
