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

from k2core.models.base import Index


class TestIndexCreation:
    def test_single_column(self):
        idx = Index(name="IDX_EMAIL", columns=["EMAIL"])
        assert idx.name == "IDX_EMAIL"
        assert idx.columns == ["EMAIL"]
        assert idx.tablespace is None

    def test_multiple_columns(self, multi_col_index):
        assert multi_col_index.columns == ["LAST_NAME", "FIRST_NAME"]
        assert len(multi_col_index.columns) == 2

    def test_with_tablespace(self, multi_col_index):
        assert multi_col_index.tablespace == "INDX"

    def test_guid_preserved(self, multi_col_index):
        assert multi_col_index.guid == "i0000000-0000-0000-0000-000000000001"

    def test_guid_auto_generated(self):
        idx = Index(name="IDX_X", columns=["X"])
        assert idx.guid
        assert len(idx.guid) == 36

    def test_two_indexes_get_different_guids(self):
        i1 = Index(name="IDX_A", columns=["A"])
        i2 = Index(name="IDX_B", columns=["B"])
        assert i1.guid != i2.guid


class TestIndexRoundTrip:
    def test_roundtrip_single_column(self):
        idx = Index(name="IDX_EMAIL", columns=["EMAIL"], tablespace="INDX",
                    guid="i0000000-0000-0000-0000-000000000099")
        d = idx.model_dump(mode="json")
        idx2 = Index.model_validate(d)
        assert idx2.name == idx.name
        assert idx2.columns == idx.columns
        assert idx2.tablespace == idx.tablespace
        assert idx2.guid == idx.guid

    def test_roundtrip_multiple_columns(self, multi_col_index):
        d = multi_col_index.model_dump(mode="json")
        idx2 = Index.model_validate(d)
        assert idx2.columns == ["LAST_NAME", "FIRST_NAME"]

    def test_roundtrip_no_tablespace(self):
        idx = Index(name="IDX_X", columns=["X"])
        d = idx.model_dump(mode="json")
        idx2 = Index.model_validate(d)
        assert idx2.tablespace is None

    def test_model_dump_contains_all_fields(self, multi_col_index):
        d = multi_col_index.model_dump(mode="json")
        assert set(d.keys()) == {"name", "columns", "tablespace", "guid"}

    def test_model_dump_is_json_serializable(self, multi_col_index):
        d = multi_col_index.model_dump(mode="json")
        json.dumps(d)  # must not raise


class TestIndexBackwardCompat:
    def test_none_guid_auto_generates(self):
        idx = Index.model_validate({"name": "IDX_X", "columns": ["X"], "guid": None})
        assert idx.guid

    def test_missing_guid_auto_generates(self):
        idx = Index.model_validate({"name": "IDX_X", "columns": ["X"]})
        assert idx.guid

    def test_missing_tablespace_defaults_none(self):
        idx = Index.model_validate({"name": "IDX_X", "columns": ["X"]})
        assert idx.tablespace is None


class TestIndexValidation:
    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            Index.model_validate({"columns": ["X"]})

    def test_missing_columns_raises(self):
        with pytest.raises(ValidationError):
            Index.model_validate({"name": "IDX_X"})
