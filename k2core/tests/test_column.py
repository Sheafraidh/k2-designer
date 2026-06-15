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

import pytest
from pydantic import ValidationError

from k2core.models.base import Column


class TestColumnCreation:
    def test_minimal_params(self, minimal_column):
        assert minimal_column.name == "ID"
        assert minimal_column.data_type == "NUMBER"

    def test_minimal_guid_auto_generated(self, minimal_column):
        assert minimal_column.guid
        assert len(minimal_column.guid) == 36  # UUID4 format

    def test_minimal_defaults(self, minimal_column):
        assert minimal_column.nullable is True
        assert minimal_column.comment is None
        assert minimal_column.default is None
        assert minimal_column.domain is None
        assert minimal_column.stereotype is None

    def test_all_params(self, full_column):
        assert full_column.name == "USERNAME"
        assert full_column.data_type == "VARCHAR2(100)"
        assert full_column.nullable is False
        assert full_column.comment == "Login name"
        assert full_column.default == "'guest'"
        assert full_column.domain == "VARCHAR2(100)"
        assert full_column.stereotype == "Business"
        assert full_column.guid == "c0000000-0000-0000-0000-000000000001"

    def test_two_columns_get_different_guids(self):
        c1 = Column(name="A", data_type="NUMBER")
        c2 = Column(name="B", data_type="VARCHAR2")
        assert c1.guid != c2.guid


class TestColumnDefaults:
    def test_nullable_defaults_to_true(self):
        c = Column(name="X", data_type="VARCHAR2(10)")
        assert c.nullable is True

    def test_optional_fields_default_to_none(self):
        c = Column(name="X", data_type="NUMBER")
        assert c.comment is None
        assert c.default is None
        assert c.domain is None
        assert c.stereotype is None


class TestColumnRoundTrip:
    def test_roundtrip_minimal(self, minimal_column):
        d = minimal_column.model_dump(mode="json")
        c2 = Column.model_validate(d)
        assert c2.name == minimal_column.name
        assert c2.data_type == minimal_column.data_type
        assert c2.guid == minimal_column.guid
        assert c2.nullable == minimal_column.nullable

    def test_roundtrip_full(self, full_column):
        d = full_column.model_dump(mode="json")
        c2 = Column.model_validate(d)
        assert c2.name == full_column.name
        assert c2.data_type == full_column.data_type
        assert c2.nullable == full_column.nullable
        assert c2.comment == full_column.comment
        assert c2.default == full_column.default
        assert c2.domain == full_column.domain
        assert c2.stereotype == full_column.stereotype
        assert c2.guid == full_column.guid

    def test_model_dump_contains_all_fields(self, full_column):
        d = full_column.model_dump(mode="json")
        assert set(d.keys()) == {"name", "data_type", "nullable", "comment", "default", "domain", "stereotype", "guid"}

    def test_model_dump_values_are_json_serializable(self, full_column):
        import json
        d = full_column.model_dump(mode="json")
        json.dumps(d)  # must not raise


class TestColumnBackwardCompat:
    def test_none_guid_auto_generates(self):
        c = Column.model_validate({"name": "X", "data_type": "NUMBER", "guid": None})
        assert c.guid
        assert len(c.guid) == 36

    def test_missing_guid_auto_generates(self):
        c = Column.model_validate({"name": "X", "data_type": "NUMBER"})
        assert c.guid

    def test_missing_optional_fields_use_defaults(self):
        c = Column.model_validate({"name": "X", "data_type": "NUMBER"})
        assert c.nullable is True
        assert c.comment is None

    def test_nullable_none_raises_validation_error(self):
        # Old .k2p files omit the key entirely (not null). Explicit null for a non-optional bool
        # is a data error and should raise ValidationError rather than silently coerce.
        with pytest.raises(ValidationError):
            Column.model_validate({"name": "X", "data_type": "NUMBER", "nullable": None})


class TestColumnValidation:
    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            Column.model_validate({"data_type": "NUMBER"})

    def test_missing_data_type_raises(self):
        with pytest.raises(ValidationError):
            Column.model_validate({"name": "ID"})

    def test_wrong_type_for_nullable_raises(self):
        with pytest.raises(ValidationError):
            Column(name="ID", data_type="NUMBER", nullable="yes_please")
