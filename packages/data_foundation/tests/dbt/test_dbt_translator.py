import unittest

from data_foundation.defs.dbt.translator import CustomDagsterDbtTranslator


class TestTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model_props = {
            # "version": None, # if not set, then name is used, otherwise alias
            # "alias": "stg_source__table", # table name
            # "source_name": "source", # schema name

            "name": "stg_source__table", # table name
            "resource_type": "model", # source, model, seed, or snapshot
            "tags": {"pii"},
            "config": {
                "meta": {
                    "dagster": {
                        "partition": "daily",
                        "partition_start_date": "2025-07-01",
                        "automation_condition": "eager"
                    }
                }
            }
        }
        cls.versioned_model_props = {
            "alias": "stg_source__table",
            "version": "v1",
            "resource_type": "model",
        }

        cls.source_props = {
            "name": "table",
            "source_name": "source", # schema name
            "resource_type": "source",
            "config": {}
        }

        cls.set_asset_key_props = {
            "name": "table",
            "source_name": "source", # schema name
            "resource_type": "source",
            "config": {
                "meta": {
                    "dagster": {
                        "asset_key": ["my", "set", "key"]
                    }
                }
            }
        }

        cls.snapshot_props = {
            "resource_type": "snapshot"
        }

        cls.seed_props = {
            "resource_type": "seed"
        }

        cls.translator = CustomDagsterDbtTranslator()

class TestGetAssetKey(TestTranslator):
    def test_get_model_asset_key(self):
        asset_key = self.translator.get_asset_key(self.model_props)
        asset_key_parts = asset_key.parts
        self.assertEqual(asset_key_parts[0], "source")
        self.assertEqual(asset_key_parts[1], "stg")
        self.assertEqual(asset_key_parts[2], "table")

    def test_get_versioned_model_asset_key(self):
        asset_key = self.translator.get_asset_key(self.versioned_model_props)
        asset_key_parts = asset_key.parts
        self.assertEqual(asset_key_parts[0], "source")
        self.assertEqual(asset_key_parts[1], "stg")
        self.assertEqual(asset_key_parts[2], "table")

    def test_get_source_asset_key(self):
        asset_key = self.translator.get_asset_key(self.source_props)
        asset_key_parts = asset_key.parts
        self.assertEqual(asset_key_parts[0], "source")
        self.assertEqual(asset_key_parts[1], "raw")
        self.assertEqual(asset_key_parts[2], "table")

    def test_get_set_asset_key(self):
        asset_key = self.translator.get_asset_key(self.set_asset_key_props)
        asset_key_parts = asset_key.parts
        self.assertEqual(asset_key_parts[0], "my")
        self.assertEqual(asset_key_parts[1], "set")
        self.assertEqual(asset_key_parts[2], "key")


class TestGetGroupName(TestTranslator):

    def test_get_group_name(self):
        group_name = self.translator.get_group_name(self.model_props)
        self.assertEqual(group_name, "source")

    def test_get_versioned_group_name(self):
        group_name = self.translator.get_group_name(self.versioned_model_props)
        self.assertEqual(group_name, "source")


class TestGetPartitionsDef(TestTranslator):
    def test_get_partitions(self):
        partitions_def = self.translator.get_partitions_def(self.model_props)
        self.assertIsNotNone(partitions_def)

    def test_get_unset_partitions(self):
        partitions_def = self.translator.get_partitions_def(self.versioned_model_props)
        self.assertIsNone(partitions_def)


class TestGetAutomationCondition(TestTranslator):
    def test_get_automation_condition(self):
        automation_condition = (
            self.translator.get_automation_condition(self.model_props)
        )
        self.assertIsNotNone(automation_condition)

    def test_get_default_model_automation_condition(self):
        automation_condition = (
            self.translator.get_automation_condition(self.versioned_model_props)
        )
        self.assertIsNotNone(automation_condition)

    def test_get_default_snapshot_automation_condition(self):
        automation_condition = (
            self.translator.get_automation_condition(self.snapshot_props)
        )
        self.assertIsNotNone(automation_condition)

    def test_get_default_seed_automation_condition(self):
        automation_condition = (
            self.translator.get_automation_condition(self.seed_props)
        )
        self.assertIsNotNone(automation_condition)
        

class TestGetTags(TestTranslator):
    def test_get_tags(self):
        tags = self.translator.get_tags(self.model_props)
        self.assertIsNotNone(tags)

    def test_get_unset_tags(self):
        tags = self.translator.get_tags(self.versioned_model_props)
        self.assertEqual(tags, {})


if __name__ == "__main__":
    unittest.main()
