import os
import unittest
from datetime import datetime

from dagster import (
    AutomationCondition,
    DailyPartitionsDefinition,
    HourlyPartitionsDefinition,
    MonthlyPartitionsDefinition,
    WeeklyPartitionsDefinition,
)

from data_platform_utils import helpers


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.env_backup = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

class TestGetSchemaName(TestHelpers):
    def test_get_schema_name_dev_environment(self):
        os.environ["TARGET"] = "dev"
        os.environ["DESTINATION__USER"] = "alice"
        result = helpers.get_schema_name("my_schema")
        self.assertEqual(result, "MY_SCHEMA__ALICE")

    def test_get_schema_name_non_dev(self):
        os.environ["TARGET"] = "prod"
        result = helpers.get_schema_name("my_schema")
        self.assertEqual(result, "MY_SCHEMA")

class TestGetDatabaseName(TestHelpers):
    def test_get_database_name_dev_environment(self):
        os.environ["TARGET"] = "dev"
        result = helpers.get_database_name("my_db")
        self.assertEqual(result, "_DEV_MY_DB")

    def test_get_database_name_non_dev(self):
        os.environ["TARGET"] = "prod"
        result = helpers.get_database_name("my_db")
        self.assertEqual(result, "MY_DB")

class TestGetAutomationConditionFromMeta(TestHelpers):
    def test_get_automation_condition_from_meta_valid(self):
        meta = {
            "automation_condition": "eager"
        }
        condition = helpers.get_automation_condition_from_meta(meta)
        self.assertIsInstance(condition, AutomationCondition)

    def test_get_automation_condition_from_meta_missing(self):
        meta = {}
        self.assertIsNone(helpers.get_automation_condition_from_meta(meta))

    def test_get_automation_condition_from_meta_invalid_condition_name(self):
        meta = {"automation_condition": "nonexistent"}
        with self.assertRaises(KeyError):
            helpers.get_automation_condition_from_meta(meta)

    def test_get_automation_condition_from_meta_invalid_config_type(self):
        meta = {
            "automation_condition": "eager",
            "automation_condition_config": "not a dict",
        }
        with self.assertRaises(ValueError):
            helpers.get_automation_condition_from_meta(meta)

    def test_get_automation_condition_from_meta_ignores_extra_args(self):
        meta = {
            "automation_condition": "eager",
            "automation_condition_config": {"unexpected_arg": "value"},
        }
        result = helpers.get_automation_condition_from_meta(meta)
        self.assertIsInstance(result, AutomationCondition)

class TestGetPartitionsDefFromMeta(TestHelpers):
    def test_get_partitions_def_from_meta_daily(self):
        meta = {
            "partition": "daily",
            "partition_start_date": "2025-01-01"
        }
        part = helpers.get_partitions_def_from_meta(meta)
        self.assertIsInstance(part, DailyPartitionsDefinition)
        self.assertEqual(part.start.date(),
                         datetime.fromisoformat("2025-01-01").date())

    def test_get_partitions_def_from_meta_hourly(self):
        meta = {
            "partition": "hourly",
            "partition_start_date": "2025-01-01T04:00"
        }
        part = helpers.get_partitions_def_from_meta(meta)
        self.assertIsInstance(part, HourlyPartitionsDefinition)
        self.assertEqual(part.start.date(),
                         datetime.fromisoformat("2025-01-01 04:00").date())
        self.assertEqual(part.start.time(),
                         datetime.fromisoformat("2025-01-01 04:00").time())

    def test_get_partitions_def_from_meta_weekly(self):
        meta = {
            "partition": "weekly",
            "partition_start_date": "2025-01-01"
        }
        part = helpers.get_partitions_def_from_meta(meta)
        self.assertIsInstance(part, WeeklyPartitionsDefinition)

    def test_get_partitions_def_from_meta_monthly(self):
        meta = {
            "partition": "monthly",
            "partition_start_date": "2025-01-01"
        }
        part = helpers.get_partitions_def_from_meta(meta)
        self.assertIsInstance(part, MonthlyPartitionsDefinition)

    def test_get_partitions_def_from_meta_invalid(self):
        meta = {
            "partition": "yearly",
            "partition_start_date": "2025-01-01"
        }
        self.assertIsNone(helpers.get_partitions_def_from_meta(meta))

    def test_get_partitions_def_from_meta_missing_keys(self):
        self.assertIsNone(helpers.get_partitions_def_from_meta({}))

class TestSanitizeInputSignature(TestHelpers):
    def test_sanitize_input_signature_filters_unexpected_keys(self):
        def sample_func(foo, bar): pass
        kwargs = {"foo": 1, "bar": 2, "extra": 999}
        result = helpers.sanitize_input_signature(sample_func, kwargs)
        self.assertEqual(result, {"foo": 1, "bar": 2})

    def test_sanitize_input_signature_keeps_valid_args(self):
        def f(a, b=2): pass
        self.assertEqual(
            helpers.sanitize_input_signature(f, {"a": 1, "b": 3}),
            {"a": 1, "b": 3}
        )

class TestGetNested(TestHelpers):
    def test_get_nested_valid_path(self):
        data = {"a": {"b": {"c": 42}}}
        self.assertEqual(helpers.get_nested(data, ["a", "b", "c"]), 42)

    def test_get_nested_path_not_found(self):
        data = {"a": {"b": {}}}
        self.assertIsNone(helpers.get_nested(data, ["a", "b", "x"]))

    def test_get_nested_null_intermediate(self):
        data = {"a": None}
        self.assertIsNone(helpers.get_nested(data, ["a", "b"]))


if __name__ == "__main__":
    unittest.main()
