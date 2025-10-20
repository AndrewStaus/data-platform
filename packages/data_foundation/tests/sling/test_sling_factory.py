import os
import unittest
from pathlib import Path
from unittest.mock import patch

from data_foundation.defs.sling.factory import Factory

FACTORY = "data_foundation.defs.sling.factory.Factory"

class TestFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.factory = Factory
        cls.connection_config = {
            "source":{
                "name": "source",
                "type": "postgres",
                "database": "env.SOURCE__SOURCE__DATABASE",
                "host": "env.SOURCE__SOURCE_DB__HOST",
                "port": "secret.SOURCE__SOURCE_DB__PORT",
                "user": "secret.SOURCE__SOURCE_DB__USER",
                "password": "secret.SOURCE__SOURCE_DB__PASSWORD"}}
        
        cls.replication_config = {
            "name": "source->snowflake",
            "env": {"SLING_LOADED_AT_COLUMN": "timestamp"},
            "source": "source",
            "target": "snowflake",
            "streams": {
                "source.table": {
                    "mode": "incremental",
                    "object": "{stream_schema_upper}.{stream_table_upper}",
                    "primary_key": ["id"],
                    "update_key": "updated_at",
                    "meta": {
                        "dagster": {
                            "partition": "hourly",
                            "partition_start_date": "2025-07-01",
                            #TODO: SOMETHING IS WRONG WITH THE FRESHNESS CHECK
                            # "freshness_check": {"lower_bound_delta_seconds": 129600},
                            "automation_condition": "on_schedule",
                            "tags": ["contains_pii"],
                            "automation_condition_config": {
                                "cron_schedule":"@daily",
                                "cron_timezone":"utc"}}}}}}

class TestBuildDefinitions(TestFactory):
    def test_build_definitions(self):
        definitions = self.factory.build_definitions(Path(__file__))
        self.assertIsNotNone(definitions)

class TestParseConnections(TestFactory):
    
    @patch(f"{FACTORY}._create_resource")
    def test_parse_connectsion(self, mock_create_resource):
        connections, kind_map = self.factory._parse_connections(
            self.connection_config, [], {})
        self.assertIsNotNone(connections)
        self.assertIsNotNone(kind_map)

    @patch(f"{FACTORY}._create_resource", return_value=None)
    def test_parse_connectsion_no_resource(self, mock_create_resource):
        connections, kind_map = self.factory._parse_connections(
            self.connection_config, [], {})
        self.assertEqual(connections, [])
        self.assertEqual(kind_map, {})

class TestCreateResource(TestFactory):
    def test_create_resource(self):
        resource = self.factory._create_resource(self.connection_config["source"])
        self.assertIsNotNone(resource)

class TestParseReplication(TestFactory):
    def test_parse_replication(self):
        resource = self.factory._parse_replication(
            self.replication_config, {"source":"postgres"})
        self.assertIsNotNone(resource)


class TestCreateAssets(TestFactory):
    def test_create_assets(self):
        assets = self.factory._create_assets(self.replication_config)
        self.assertIsNotNone(assets)


class TestSetSchema(TestFactory):
    def test_set_schema_prod(self):
        os.environ["TARGET"] = "prod"
        original_value = self.replication_config["streams"]["source.table"]["object"]
        replication_config = self.factory._set_schema(self.replication_config)
        new_value = self.replication_config["streams"]["source.table"]["object"]

        self.assertIsNotNone(replication_config)
        self.assertEqual(original_value, new_value)

    def test_set_schema_dev(self):
        os.environ["TARGET"] = "dev"
        original_value = self.replication_config["streams"]["source.table"]["object"]
        replication_config = self.factory._set_schema(self.replication_config)
        new_value = self.replication_config["streams"]["source.table"]["object"]

        self.assertIsNotNone(replication_config)
        self.assertNotEqual(original_value, new_value)

class TestGetDeps(TestFactory):
    def test_get_deps_with_kind(self):
        deps = self.factory._get_deps(self.replication_config, "postgres")
        self.assertIsNotNone(deps)

    def test_get_deps_without_kind(self):
        deps = self.factory._get_deps(self.replication_config)
        self.assertIsNotNone(deps)

class TestGetFreshnessChecks(TestFactory):
    def test_get_freshness_checks(self):
        freshness_checks = self.factory._get_freshness_checks(self.replication_config)
        self.assertIsNotNone(freshness_checks)


if __name__ == "__main__":
    unittest.main()