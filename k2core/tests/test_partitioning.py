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

from k2core.models.base import Partitioning, PartitionType


class TestPartitionType:
    def test_range_value(self):
        assert PartitionType.RANGE.value == "range"

    def test_list_value(self):
        assert PartitionType.LIST.value == "list"

    def test_from_string(self):
        assert PartitionType("range") is PartitionType.RANGE
        assert PartitionType("list") is PartitionType.LIST

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            PartitionType("hash")


class TestPartitioningCreation:
    def test_range_partitioning(self, range_partitioning):
        assert range_partitioning.columns == ["CREATED_AT"]
        assert range_partitioning.partition_type == PartitionType.RANGE

    def test_list_partitioning(self):
        p = Partitioning(columns=["REGION", "COUNTRY"], partition_type=PartitionType.LIST)
        assert p.partition_type == PartitionType.LIST
        assert len(p.columns) == 2

    def test_multi_column_range(self):
        p = Partitioning(columns=["YEAR", "MONTH"], partition_type=PartitionType.RANGE)
        assert p.columns == ["YEAR", "MONTH"]


class TestPartitioningRoundTrip:
    def test_roundtrip_range(self, range_partitioning):
        d = range_partitioning.model_dump(mode="json")
        p2 = Partitioning.model_validate(d)
        assert p2.columns == range_partitioning.columns
        assert p2.partition_type == PartitionType.RANGE

    def test_roundtrip_list(self):
        p = Partitioning(columns=["REGION"], partition_type=PartitionType.LIST)
        d = p.model_dump(mode="json")
        p2 = Partitioning.model_validate(d)
        assert p2.partition_type == PartitionType.LIST

    def test_model_dump_partition_type_is_string(self, range_partitioning):
        d = range_partitioning.model_dump(mode="json")
        assert d["partition_type"] == "range"
        assert type(d["partition_type"]) is str

    def test_model_dump_is_json_serializable(self, range_partitioning):
        d = range_partitioning.model_dump(mode="json")
        json.dumps(d)  # must not raise

    def test_model_dump_contains_expected_keys(self, range_partitioning):
        d = range_partitioning.model_dump(mode="json")
        assert set(d.keys()) == {"columns", "partition_type"}


class TestPartitioningBackwardCompat:
    def test_validate_from_string_type(self):
        p = Partitioning.model_validate({"columns": ["X"], "partition_type": "range"})
        assert p.partition_type == PartitionType.RANGE

    def test_validate_list_from_string(self):
        p = Partitioning.model_validate({"columns": ["REGION"], "partition_type": "list"})
        assert p.partition_type == PartitionType.LIST


class TestPartitioningValidation:
    def test_missing_columns_raises(self):
        with pytest.raises(ValidationError):
            Partitioning.model_validate({"partition_type": "range"})

    def test_missing_partition_type_raises(self):
        with pytest.raises(ValidationError):
            Partitioning.model_validate({"columns": ["X"]})

    def test_invalid_partition_type_raises(self):
        with pytest.raises(ValidationError):
            Partitioning.model_validate({"columns": ["X"], "partition_type": "hash"})
