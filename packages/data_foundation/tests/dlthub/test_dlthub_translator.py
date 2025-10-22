import unittest
from datetime import datetime

import dagster as dg
import dlt
from data_foundation.defs.dlthub.translator import (
    CustomDagsterDltTranslator,
)


class TestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Create assets that can be reused across tests"""
        cls.translator = CustomDagsterDltTranslator()
        cls.configured_translator = CustomDagsterDltTranslator(
            automation_condition=dg.AutomationCondition.eager(),
            partitions_def=dg.MonthlyPartitionsDefinition(
                start_date=datetime(2023, 1, 1)
            ),
            tags={"pii":""}
        )

        @dlt.resource(name="test.table_1")
        def resource_1():
            yield from [{"a":1}]
        cls.resource_1 = resource_1

        @dlt.resource(name="test.table_2", data_from=resource_1)
        def resource_2(data):
            yield from [{"a":1}]

        @dlt.resource(name="test_table_3")
        def resource_3(data):
            yield from [{"a":1}]

        cls.resource_1 = resource_1
        cls.resource_2 = resource_2
        cls.resource_3 = resource_3

class TestGetDepsAssetKeys(TestCases):

    def test_get_deps_asset_key(self) -> None:
        deps_asset_key = self.translator.get_deps_asset_keys(self.resource_1)[0]
        schema, stage, table = deps_asset_key.parts
        self.assertEqual(schema, "test")
        self.assertEqual(stage, "src")
        self.assertEqual(table, "table_1")

    def test_get_deps_asset_key_with_data_from(self) -> None:
        deps_asset_key = self.translator.get_deps_asset_keys(self.resource_2)[0]
        schema, stage, table = deps_asset_key.parts
        self.assertEqual(schema, "test")
        self.assertEqual(stage, "raw")
        self.assertEqual(table, "table_1")

    def test_malformed_get_deps_asset_key(self) -> None:
        deps_asset_key = self.translator.get_deps_asset_keys(self.resource_3)[0]
        key, = deps_asset_key.parts
        self.assertEqual(key, "None_test_table_3")

class TestGetAssetKey(TestCases):

    def test_get_asset_key(self) -> None:
        asset_key = self.translator.get_asset_key(self.resource_1)
        schema, stage, table = asset_key.parts
        self.assertEqual(schema, "test")
        self.assertEqual(stage, "raw")
        self.assertEqual(table, "table_1")

        asset_key = self.translator.get_asset_key(self.resource_2)
        schema, stage, table = asset_key.parts
        self.assertEqual(schema, "test")
        self.assertEqual(stage, "raw")
        self.assertEqual(table, "table_2")

    def test_malformed_malformed_asset_key(self) -> None:
        asset_key = self.translator.get_asset_key(self.resource_3)
        key, = asset_key.parts
        self.assertEqual(key, "dlt_None_test_table_3")

class TestGetGroupName(TestCases):

    def test_get_group_name(self) -> None:
        group_name = self.translator.get_group_name(self.resource_1)
        self.assertEqual(group_name, "test")

class TestGetPartitionsDef(TestCases):

    def test_get_partitions_def_condition_when_set(self) -> None:
        partitions_def = self.configured_translator.get_partitions_def(self.resource_1)
        self.assertEqual(partitions_def, dg.MonthlyPartitionsDefinition(
            start_date=datetime(2023, 1, 1)
        ))

    def test_get_partitions_def_condition_when_none_is_set(self) -> None:
        partitions_def = self.translator.get_partitions_def(self.resource_1)
        self.assertIs(partitions_def, None)

class TestGetAutomationCondition(TestCases):

    def test_get_automation_condition_when_set(self) -> None:
        condition = self.configured_translator.get_automation_condition(self.resource_1)
        self.assertEqual(condition, dg.AutomationCondition.eager())

    def test_get_automation_condition_when_none_is_set(self) -> None:
        condition = self.translator.get_automation_condition(self.resource_1)
        self.assertIs(condition, None)

class TestGetTags(TestCases):

    def test_get_tags_when_set(self) -> None:
        tags = self.configured_translator.get_tags(self.resource_1)
        self.assertEqual(tags, {"pii":""})

    def test_get_tags_when_none_is_set(self) -> None:
        tags = self.translator.get_tags(self.resource_1)
        self.assertEqual(tags, {})


if __name__ == "__main__": # pragma: no coverage
    unittest.main()
