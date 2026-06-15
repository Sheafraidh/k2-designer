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

from k2core.models.base import Column, Key, KeyType, Partitioning, PartitionType
from k2core.models.owner import Owner
from k2core.models.project import Project
from k2core.models.sequence import Sequence
from k2core.models.table import Table


@pytest.fixture
def empty_project():
    return Project(name="Empty", description=None, init_default_stereotypes=False)


@pytest.fixture
def populated_project(empty_project):
    owner = Owner(name="APP", default_tablespace="DATA",
                  guid="a0000000-0000-0000-0000-000000000001")
    empty_project.add_owner(owner)

    users = Table(name="USERS", owner="APP", guid="t0000000-0000-0000-0000-000000000001")
    users.add_column(Column(name="ID", data_type="NUMBER", nullable=False))
    users.add_column(Column(name="USERNAME", data_type="VARCHAR2(100)", nullable=False))
    users.add_key(Key(name="PK_USERS", columns=["ID"], key_type=KeyType.PRIMARY))
    empty_project.add_table(users)

    seq = Sequence(name="SEQ_USERS", owner="APP", start_with=1, increment_by=1,
                   guid="s0000000-0000-0000-0000-000000000001")
    empty_project.add_sequence(seq)

    return empty_project


class TestProjectCreation:
    def test_empty_project_name(self, empty_project):
        assert empty_project.name == "Empty"

    def test_default_name(self):
        p = Project()
        assert p.name == "Untitled Project"

    def test_empty_collections(self, empty_project):
        assert empty_project.owners == []
        assert empty_project.tables == []
        assert empty_project.sequences == []
        assert empty_project.domains == []
        assert empty_project.diagrams == []
        assert empty_project.foreign_keys == {}

    def test_default_stereotypes_initialized(self):
        p = Project()
        assert len(p.stereotypes) == 4

    def test_no_default_stereotypes_when_disabled(self, empty_project):
        assert empty_project.stereotypes == []


class TestProjectOwner:
    def test_add_owner(self, populated_project):
        assert len(populated_project.owners) == 1
        assert populated_project.owners[0].name == "APP"

    def test_get_owner(self, populated_project):
        owner = populated_project.get_owner("APP")
        assert owner is not None
        assert owner.name == "APP"

    def test_get_owner_missing(self, populated_project):
        assert populated_project.get_owner("GHOST") is None

    def test_remove_owner_also_removes_tables(self, populated_project):
        populated_project.remove_owner("APP")
        assert populated_project.owners == []
        assert populated_project.tables == []
        assert populated_project.sequences == []


class TestProjectTable:
    def test_add_table(self, populated_project):
        assert len(populated_project.tables) == 1
        assert populated_project.tables[0].name == "USERS"

    def test_get_table(self, populated_project):
        t = populated_project.get_table("USERS", "APP")
        assert t is not None
        assert t.full_name == "APP.USERS"

    def test_get_table_wrong_owner(self, populated_project):
        assert populated_project.get_table("USERS", "OTHER") is None

    def test_remove_table(self, populated_project):
        removed = populated_project.remove_table("USERS", "APP")
        assert removed is True
        assert populated_project.tables == []

    def test_tables_by_owner(self, populated_project):
        tables = populated_project.get_tables_by_owner("APP")
        assert len(tables) == 1
        assert tables[0].name == "USERS"


class TestProjectSequence:
    def test_add_sequence(self, populated_project):
        assert len(populated_project.sequences) == 1

    def test_get_sequence(self, populated_project):
        seq = populated_project.get_sequence("SEQ_USERS", "APP")
        assert seq is not None
        assert seq.start_with == 1

    def test_sequences_by_owner(self, populated_project):
        seqs = populated_project.get_sequences_by_owner("APP")
        assert len(seqs) == 1


class TestProjectRoundTrip:
    def test_roundtrip_empty(self, empty_project):
        d = empty_project.to_dict()
        p2 = Project.from_dict(d)
        assert p2.name == empty_project.name

    def test_roundtrip_populated(self, populated_project):
        d = populated_project.to_dict()
        p2 = Project.from_dict(d)
        assert p2.name == populated_project.name
        assert len(p2.owners) == 1
        assert len(p2.tables) == 1
        assert len(p2.sequences) == 1

    def test_roundtrip_table_columns_preserved(self, populated_project):
        d = populated_project.to_dict()
        p2 = Project.from_dict(d)
        t = p2.get_table("USERS", "APP")
        assert len(t.columns) == 2
        assert t.columns[0].name == "ID"
        assert isinstance(t.columns[0], Column)

    def test_roundtrip_keys_preserved(self, populated_project):
        d = populated_project.to_dict()
        p2 = Project.from_dict(d)
        t = p2.get_table("USERS", "APP")
        assert t.keys[0].key_type == KeyType.PRIMARY

    def test_to_dict_is_json_serializable(self, populated_project):
        d = populated_project.to_dict()
        json.dumps(d)  # must not raise

    def test_roundtrip_with_partitioned_table(self, empty_project):
        t = Table(name="SALES", owner="APP")
        t.add_column(Column(name="REGION", data_type="VARCHAR2(50)"))
        t.set_partitioning(Partitioning(columns=["REGION"], partition_type=PartitionType.LIST))
        empty_project.add_table(t)

        d = empty_project.to_dict()
        p2 = Project.from_dict(d)
        t2 = p2.get_table("SALES", "APP")
        assert t2.partitioning.partition_type == PartitionType.LIST

    def test_roundtrip_foreign_keys_dict(self, empty_project):
        empty_project.add_foreign_key("APP.ORDERS", "USER_ID", "APP.USERS", "ID")
        d = empty_project.to_dict()
        p2 = Project.from_dict(d)
        assert "APP.ORDERS.USER_ID" in p2.foreign_keys
        assert p2.foreign_keys["APP.ORDERS.USER_ID"]["target_table"] == "APP.USERS"


class TestProjectFixture:
    def test_load_fixture_file(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        assert p.name == "Test Project"

    def test_fixture_owners(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        assert len(p.owners) == 1
        assert p.owners[0].name == "APP"
        assert p.owners[0].default_tablespace == "DATA"

    def test_fixture_tables(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        assert len(p.tables) == 2
        names = {t.name for t in p.tables}
        assert names == {"USERS", "ORDERS"}

    def test_fixture_columns_are_column_instances(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        users = p.get_table("USERS", "APP")
        assert all(isinstance(c, Column) for c in users.columns)

    def test_fixture_primary_key(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        users = p.get_table("USERS", "APP")
        pk = next(k for k in users.keys if k.key_type == KeyType.PRIMARY)
        assert pk.name == "PK_USERS"
        assert pk.columns == ["ID"]

    def test_fixture_foreign_key(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        orders = p.get_table("ORDERS", "APP")
        fk = next(k for k in orders.keys if k.key_type == KeyType.FOREIGN)
        assert fk.referenced_table == "APP.USERS"
        assert fk.on_delete == "CASCADE"

    def test_fixture_partitioning(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        orders = p.get_table("ORDERS", "APP")
        assert orders.partitioning is not None
        assert orders.partitioning.partition_type == PartitionType.LIST
        assert orders.partitioning.columns == ["REGION"]

    def test_fixture_sequence(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        assert len(p.sequences) == 1
        seq = p.sequences[0]
        assert seq.name == "SEQ_USERS"
        assert seq.owner == "APP"

    def test_fixture_foreign_keys_dict(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        assert "APP.ORDERS.USER_ID" in p.foreign_keys

    def test_fixture_index(self, fixture_project_dict):
        p = Project.from_dict(fixture_project_dict)
        users = p.get_table("USERS", "APP")
        assert len(users.indexes) == 1
        assert users.indexes[0].name == "IDX_USERS_USERNAME"


class TestProjectBackwardCompat:
    def test_missing_description_ok(self):
        p = Project.from_dict({"name": "X"})
        assert p.name == "X"
        assert p.description is None

    def test_missing_all_optional_collections_ok(self):
        p = Project.from_dict({"name": "X"})
        assert p.owners == []
        assert p.tables == []
        assert p.sequences == []
        assert p.diagrams == []
        assert p.domains == []
        assert p.foreign_keys == {}

    def test_missing_last_active_diagram_ok(self):
        p = Project.from_dict({"name": "X"})
        assert p.last_active_diagram is None

    def test_table_without_guid_gets_auto_guid(self):
        p = Project.from_dict({
            "name": "X",
            "tables": [{"name": "T", "owner": "O", "columns": [], "keys": [], "indexes": []}]
        })
        assert p.tables[0].guid

    def test_column_without_guid_gets_auto_guid(self):
        p = Project.from_dict({
            "name": "X",
            "tables": [{
                "name": "T", "owner": "O",
                "columns": [{"name": "ID", "data_type": "NUMBER"}],
                "keys": [], "indexes": []
            }]
        })
        assert p.tables[0].columns[0].guid
