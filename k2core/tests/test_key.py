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
from pydantic import ValidationError

from k2core.models.base import Key, KeyType


class TestKeyType:
    def test_enum_values(self):
        assert KeyType.PRIMARY.value == "PRIMARY"
        assert KeyType.FOREIGN.value == "FOREIGN"
        assert KeyType.UNIQUE.value == "UNIQUE"

    def test_is_str_subclass(self):
        assert isinstance(KeyType.PRIMARY, str)
        assert isinstance(KeyType.FOREIGN, str)
        assert isinstance(KeyType.UNIQUE, str)

    def test_string_comparison(self):
        assert KeyType.PRIMARY == "PRIMARY"
        assert KeyType.FOREIGN == "FOREIGN"
        assert KeyType.UNIQUE == "UNIQUE"

    def test_from_string(self):
        assert KeyType("PRIMARY") is KeyType.PRIMARY
        assert KeyType("FOREIGN") is KeyType.FOREIGN
        assert KeyType("UNIQUE") is KeyType.UNIQUE

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            KeyType("INVALID")


class TestKeyClassAliases:
    """Key.PRIMARY/FOREIGN/UNIQUE class attrs must be intact for GUI backward compat."""

    def test_primary_alias(self):
        assert Key.PRIMARY == KeyType.PRIMARY
        assert Key.PRIMARY == "PRIMARY"

    def test_foreign_alias(self):
        assert Key.FOREIGN == KeyType.FOREIGN
        assert Key.FOREIGN == "FOREIGN"

    def test_unique_alias(self):
        assert Key.UNIQUE == KeyType.UNIQUE
        assert Key.UNIQUE == "UNIQUE"

    def test_aliases_not_in_model_fields(self):
        assert "PRIMARY" not in Key.model_fields
        assert "FOREIGN" not in Key.model_fields
        assert "UNIQUE" not in Key.model_fields


class TestKeyCreation:
    def test_primary_key(self, pk_key):
        assert pk_key.name == "PK_USERS"
        assert pk_key.columns == ["ID"]
        assert pk_key.key_type == KeyType.PRIMARY
        assert pk_key.guid == "k0000000-0000-0000-0000-000000000001"

    def test_foreign_key(self, fk_key):
        assert fk_key.name == "FK_ORDERS_USER"
        assert fk_key.key_type == KeyType.FOREIGN
        assert fk_key.referenced_table == "APP.USERS"
        assert fk_key.referenced_columns == ["ID"]
        assert fk_key.on_delete == "CASCADE"

    def test_default_key_type_is_unique(self):
        k = Key(name="UK_EMAIL", columns=["EMAIL"])
        assert k.key_type == KeyType.UNIQUE

    def test_default_referenced_columns_is_empty_list(self):
        k = Key(name="PK", columns=["ID"], key_type=KeyType.PRIMARY)
        assert k.referenced_columns == []

    def test_guid_auto_generated(self):
        k = Key(name="PK", columns=["ID"])
        assert k.guid
        assert len(k.guid) == 36

    def test_fk_owner_table_column_format(self, fk_key):
        # referenced_table stored as "OWNER.TABLE" — no validation constraint, just data integrity
        parts = fk_key.referenced_table.split(".")
        assert len(parts) == 2
        assert parts[0] == "APP"
        assert parts[1] == "USERS"


class TestKeyRoundTrip:
    def test_roundtrip_primary_key(self, pk_key):
        d = pk_key.model_dump(mode="json")
        k2 = Key.model_validate(d)
        assert k2.name == pk_key.name
        assert k2.columns == pk_key.columns
        assert k2.key_type == pk_key.key_type
        assert k2.guid == pk_key.guid

    def test_roundtrip_foreign_key(self, fk_key):
        d = fk_key.model_dump(mode="json")
        k2 = Key.model_validate(d)
        assert k2.key_type == KeyType.FOREIGN
        assert k2.referenced_table == fk_key.referenced_table
        assert k2.referenced_columns == fk_key.referenced_columns
        assert k2.on_delete == fk_key.on_delete

    def test_model_dump_key_type_is_plain_string(self, pk_key):
        d = pk_key.model_dump(mode="json")
        assert d["key_type"] == "PRIMARY"
        assert type(d["key_type"]) is str

    def test_model_dump_is_json_serializable(self, fk_key):
        d = fk_key.model_dump(mode="json")
        json.dumps(d)  # must not raise


class TestKeyBackwardCompat:
    def test_validate_from_json_string_key_type(self):
        k = Key.model_validate({"name": "PK", "columns": ["ID"], "key_type": "PRIMARY"})
        assert k.key_type == KeyType.PRIMARY

    def test_none_guid_auto_generates(self):
        k = Key.model_validate({"name": "PK", "columns": ["ID"], "guid": None})
        assert k.guid

    def test_missing_guid_auto_generates(self):
        k = Key.model_validate({"name": "PK", "columns": ["ID"]})
        assert k.guid

    def test_missing_optional_fields_default(self):
        k = Key.model_validate({"name": "PK", "columns": ["ID"]})
        assert k.referenced_table is None
        assert k.referenced_columns == []
        assert k.on_delete is None
        assert k.on_update is None
        assert k.associated_index_guid is None


class TestKeyValidation:
    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            Key.model_validate({"columns": ["ID"]})

    def test_missing_columns_raises(self):
        with pytest.raises(ValidationError):
            Key.model_validate({"name": "PK"})

    def test_invalid_key_type_raises(self):
        with pytest.raises(ValidationError):
            Key.model_validate({"name": "PK", "columns": ["ID"], "key_type": "BADTYPE"})
