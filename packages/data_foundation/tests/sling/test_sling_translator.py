import unittest

from data_foundation.defs.sling.translator import CustomDagsterSlingTranslator


class TestTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.translator = CustomDagsterSlingTranslator()

        cls.stream_definition = {
            "name":"schema.table_1",
            "config":{
                "meta": {
                    "dagster": {
                        "partition": "hourly",
                        "partition_start_date": "2025-07-01",
                        "automation_condition": "on_schedule",
                        "tags": {"pii":""},
                        "automation_condition_config": {
                            "cron_schedule":"@hourly",
                            "cron_timezone":"utc"}}}}}

        cls.stream_definition_set_asset_key = {
            "name":"schema.table_1",
            "config":{
                "meta": {
                    "dagster": {
                        "deps": ["schema.src.table"],
                        "asset_key": "schema.raw.table",
                        "group": "schema"}}}}
        
        cls.stream_definition_string_deps_key = {
            "name":"schema.table_1",
            "config":{
                "meta": {
                    "dagster": {
                        "deps": "schema.src.table"}}}}
        
        cls.stream_definition_bad_asset_key = {
            "name":"schema.table_1",
            "config":{
                "meta": {
                    "dagster": {
                        "asset_key": "schema/raw/table",
                        "deps": ["schema/src/table"]}}}}

class TestGetAssetSpec(TestTranslator):
    def test_get_asset_spec(self):
        asset_spec = self.translator.get_asset_spec(self.stream_definition)
        self.assertIsNotNone(asset_spec)

class TestGetAssetKey(TestTranslator):
    def test_get_asset_key(self):
        asset_key = self.translator.get_asset_key(self.stream_definition)
        self.assertIsNotNone(asset_key)

    def test_get_set_asset_key(self):
        asset_key = self.translator.get_asset_key(self.stream_definition_set_asset_key)
        self.assertIsNotNone(asset_key)

    def test_get_bad_asset_key(self):
        with self.assertRaises(ValueError):
            self.translator.get_asset_key(
                self.stream_definition_bad_asset_key)


class TestGetDepsAssetKey(TestTranslator):
    def test_get_deps_asset_key(self):
        deps_asset_key = self.translator.get_deps_asset_key(self.stream_definition)
        self.assertIsNotNone(deps_asset_key)

    def test_get_set_deps_asset_key(self):
        deps_asset_key = self.translator.get_deps_asset_key(
            self.stream_definition_set_asset_key)
        self.assertIsNotNone(deps_asset_key)

    def test_get_set_string_asset_key(self):
        deps_asset_key = self.translator.get_deps_asset_key(
            self.stream_definition_string_deps_key)
        self.assertIsNotNone(deps_asset_key)

    def test_get_bad_deps_asset_key(self):
        with self.assertRaises(ValueError):
            self.translator.get_deps_asset_key(
                self.stream_definition_bad_asset_key)

class TestGroupName(TestTranslator):
    def test_get_group_name(self):
        group_name = self.translator.get_group_name(self.stream_definition)
        self.assertIsNotNone(group_name)

    def test_get_set_group_name(self):
        group_name = self.translator.get_group_name(
            self.stream_definition_set_asset_key)
        self.assertIsNotNone(group_name)


class TestGetTags(TestTranslator):
    def test_get_tags(self):
        tags = self.translator.get_tags(self.stream_definition)
        self.assertIsNotNone(tags)
        self.assertEqual(tags, {"pii":""})

    def test_get_no_tags(self):
        tags = self.translator.get_tags(self.stream_definition_set_asset_key)
        self.assertIsNotNone(tags)
        self.assertEqual(tags, {})


class TestGetAutomationCondition(TestTranslator):
    def test_get_automation_condition(self):
        automation_condition = (
            self.translator.get_automation_condition(self.stream_definition)
        )
        self.assertIsNotNone(automation_condition)

    def test_get_no_automation_condition(self):
        automation_condition = (
            self.translator.get_automation_condition(
                self.stream_definition_set_asset_key)
        )
        self.assertIsNone(automation_condition)


class TestGetPartitionsDef(TestTranslator):
    def test_get_partitions_def(self):
        partitions_def = self.translator.get_partitions_def(self.stream_definition)
        self.assertIsNotNone(partitions_def)

    def test_get_no_partitions_def(self):
        partitions_def = self.translator.get_partitions_def(
            self.stream_definition_set_asset_key)
        self.assertIsNone(partitions_def)


if __name__ == "__main__":
    unittest.main()