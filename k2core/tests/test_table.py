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

import pytest

from k2core.models.base import Column, Index, Key, KeyType, Partitioning, PartitionType
from k2core.models.table import Table


class TestTableCreation:
    def test_basic_attributes(self, simple_table):
        assert simple_table.name == "USERS"
        assert simple_table.owner == "APP"
        assert simple_table.guid == "t0000000-0000-0000-0000-000000000001"

    def test_full_name(self, simple_table):
        assert simple_table.full_name == "APP.USERS"

    def test_default_color(self):
        t = Table(name="T", owner="O")
        assert t.color == "#4C4C4C"

    def test_editionable_defaults_false(self):
        t = Table(name="T", owner="O")
        assert t.editionable is False

    def test_collections_start_empty(self):
        t = Table(name="T", owner="O")
        assert t.columns == []
        assert t.keys == []
        assert t.indexes == []
        assert t.partitioning is None


class TestTableColumns:
    def test_add_column(self, simple_table):
        assert len(simple_table.columns) == 2
        assert simple_table.columns[0].name == "ID"
        assert simple_table.columns[1].name == "USERNAME"

    def test_column_order_preserved(self):
        t = Table(name="T", owner="O")
        for name in ["C", "A", "B"]:
            t.add_column(Column(name=name, data_type="NUMBER"))
        assert [c.name for c in t.columns] == ["C", "A", "B"]

    def test_get_column_found(self, simple_table):
        col = simple_table.get_column("ID")
        assert col is not None
        assert col.data_type == "NUMBER"

    def test_get_column_not_found(self, simple_table):
        assert simple_table.get_column("NONEXISTENT") is None

    def test_remove_column(self, simple_table):
        removed = simple_table.remove_column("USERNAME")
        assert removed is True
        assert len(simple_table.columns) == 1
        assert simple_table.get_column("USERNAME") is None

    def test_remove_nonexistent_column(self, simple_table):
        assert simple_table.remove_column("GHOST") is False
        assert len(simple_table.columns) == 2


class TestTableKeysAndIndexes:
    def test_keys_loaded(self, simple_table):
        assert len(simple_table.keys) == 1
        assert simple_table.keys[0].name == "PK_USERS"
        assert simple_table.keys[0].key_type == KeyType.PRIMARY

    def test_indexes_loaded(self, simple_table):
        assert len(simple_table.indexes) == 1
        assert simple_table.indexes[0].name == "IDX_USERS_USERNAME"

    def test_remove_key(self, simple_table):
        removed = simple_table.remove_key("PK_USERS")
        assert removed is True
        assert simple_table.keys == []

    def test_remove_nonexistent_key(self, simple_table):
        assert simple_table.remove_key("GHOST") is False

    def test_remove_index(self, simple_table):
        removed = simple_table.remove_index("IDX_USERS_USERNAME")
        assert removed is True
        assert simple_table.indexes == []


class TestTablePartitioning:
    def test_set_partitioning(self, simple_table):
        p = Partitioning(columns=["CREATED_AT"], partition_type=PartitionType.RANGE)
        simple_table.set_partitioning(p)
        assert simple_table.partitioning is not None
        assert simple_table.partitioning.partition_type == PartitionType.RANGE

    def test_clear_partitioning(self, simple_table):
        p = Partitioning(columns=["X"], partition_type=PartitionType.LIST)
        simple_table.set_partitioning(p)
        simple_table.set_partitioning(None)
        assert simple_table.partitioning is None


class TestTableRoundTrip:
    def test_roundtrip_simple(self, simple_table):
        d = simple_table.to_dict()
        t2 = Table.from_dict(d)
        assert t2.name == simple_table.name
        assert t2.owner == simple_table.owner
        assert t2.guid == simple_table.guid

    def test_roundtrip_columns_preserved(self, simple_table):
        d = simple_table.to_dict()
        t2 = Table.from_dict(d)
        assert len(t2.columns) == 2
        assert t2.columns[0].name == "ID"
        assert t2.columns[1].name == "USERNAME"
        # Column type is still Column (Pydantic model)
        assert isinstance(t2.columns[0], Column)

    def test_roundtrip_keys_preserved(self, simple_table):
        d = simple_table.to_dict()
        t2 = Table.from_dict(d)
        assert len(t2.keys) == 1
        assert t2.keys[0].name == "PK_USERS"
        assert t2.keys[0].key_type == KeyType.PRIMARY

    def test_roundtrip_indexes_preserved(self, simple_table):
        d = simple_table.to_dict()
        t2 = Table.from_dict(d)
        assert len(t2.indexes) == 1
        assert t2.indexes[0].name == "IDX_USERS_USERNAME"
        assert t2.indexes[0].tablespace == "INDX"

    def test_roundtrip_with_partitioning(self, simple_table):
        simple_table.set_partitioning(
            Partitioning(columns=["REGION"], partition_type=PartitionType.LIST)
        )
        d = simple_table.to_dict()
        t2 = Table.from_dict(d)
        assert t2.partitioning is not None
        assert t2.partitioning.partition_type == PartitionType.LIST
        assert t2.partitioning.columns == ["REGION"]

    def test_roundtrip_without_partitioning(self, simple_table):
        d = simple_table.to_dict()
        t2 = Table.from_dict(d)
        assert t2.partitioning is None

    def test_to_dict_is_json_serializable(self, simple_table):
        simple_table.set_partitioning(
            Partitioning(columns=["X"], partition_type=PartitionType.RANGE)
        )
        d = simple_table.to_dict()
        json.dumps(d)  # must not raise

    def test_roundtrip_fk_table(self):
        t = Table(name="ORDERS", owner="APP")
        t.add_column(Column(name="ID", data_type="NUMBER", nullable=False))
        t.add_column(Column(name="USER_ID", data_type="NUMBER", nullable=False))
        t.add_key(Key(
            name="FK_ORDERS_USER",
            columns=["USER_ID"],
            key_type=KeyType.FOREIGN,
            referenced_table="APP.USERS",
            referenced_columns=["ID"],
            on_delete="CASCADE",
        ))
        d = t.to_dict()
        t2 = Table.from_dict(d)
        fk = t2.keys[0]
        assert fk.key_type == KeyType.FOREIGN
        assert fk.referenced_table == "APP.USERS"
        assert fk.referenced_columns == ["ID"]
        assert fk.on_delete == "CASCADE"


class TestTableBackwardCompat:
    def test_missing_optional_fields_ok(self):
        t = Table.from_dict({
            "name": "T", "owner": "O",
            "columns": [], "keys": [], "indexes": [],
        })
        assert t.tablespace is None
        assert t.stereotype is None
        assert t.domain is None
        assert t.partitioning is None

    def test_columns_without_guid_auto_generate(self):
        t = Table.from_dict({
            "name": "T", "owner": "O",
            "columns": [{"name": "ID", "data_type": "NUMBER"}],
            "keys": [], "indexes": [],
        })
        assert t.columns[0].guid
