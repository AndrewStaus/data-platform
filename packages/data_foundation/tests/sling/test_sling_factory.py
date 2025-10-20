import os
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

import dagster as dg
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
            "defaults": {
                "object": "{stream_schema_upper}.{stream_table_upper}",
                "meta": {
                    "dagster": {
                        "freshness_check": {"lower_bound_delta_seconds": 129600},
                        "automation_condition": "on_schedule",
                        "tags": ["contains_pii"],
                        "automation_condition_config": {
                            "cron_schedule":"@daily",
                            "cron_timezone":"utc"}}}
            },
            "streams": {
                "source.table": {
                    "mode": "incremental",
                    "object": "{stream_schema_upper}.{stream_table_upper}",
                    "primary_key": ["id"],
                    "update_key": "updated_at"}}}

        cls.partitioned_replication_config = {
            "name": "source->snowflake",
            "env": {"SLING_LOADED_AT_COLUMN": "timestamp"},
            "source": "source",
            "target": "snowflake",
            "defaults": {
                "meta": {
                    "dagster": {
                        "partition": "hourly",
                        "partition_start_date": "2025-07-01",
                        "freshness_check": {"deadline_cron": "@daily"},
                        "automation_condition": "on_schedule",
                        "tags": ["contains_pii"],
                        "automation_condition_config": {
                            "cron_schedule":"@daily",
                            "cron_timezone":"utc"}}}
            },
            "streams": {
                "source.table": {
                    "mode": "incremental",
                    "object": "{stream_schema_upper}.{stream_table_upper}",
                    "primary_key": ["id"],
                    "update_key": "updated_at"}}}

        cls.bad_partitioned_replication_config = {
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
                            "freshness_check": {"lower_bound_delta_seconds": None},
                            "automation_condition": "on_schedule",
                            "tags": ["contains_pii"],
                            "automation_condition_config": {
                                "cron_schedule":"@daily",
                                "cron_timezone":"utc"}}}}}}

class TestBuildDefinitions(TestFactory):
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("pathlib.Path.glob", return_value=["/some/path.yaml", "/some/path2.yaml"])
    @patch(f"{FACTORY}._parse_connections", return_value=([], {}))
    @patch(f"{FACTORY}._parse_replication", return_value=(None, [], []))
    @patch("dagster.Definitions")
    @patch("yaml.load")
    def test_build_definitions(self,
                               mock_yaml_load,
                               mock_definitions,
                               mock_parse_replicate,
                               mock_parse_connections,
                               mock_glob,
                               mock_file):
        connections_yaml = {"connections":self.connection_config}
        mock_yaml_load.side_effect = [connections_yaml, self.replication_config]
        definitions = self.factory.build_definitions(Path(__file__))
        mock_definitions.return_value = dg.Definitions()
        self.assertIsNotNone(definitions)

class TestParseConnections(TestFactory):
    
    @patch(f"{FACTORY}._create_resource")
    def test_parse_connection(self, mock_create_resource):
        connections, kind_map = self.factory._parse_connections(
            self.connection_config, [], {})
        self.assertIsNotNone(connections)
        self.assertIsNotNone(kind_map)

    @patch(f"{FACTORY}._create_resource", return_value=None)
    def test_parse_connection_no_resource(self, mock_create_resource):
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
        freshness_checks = self.factory._get_freshness_checks(
            self.replication_config)
        self.assertIsNotNone(freshness_checks)

    # # FAILING
    # # expecting deadline cron to be set in config, check implementation
    def test_get_partitioned_freshness_checks(self):
        freshness_checks = self.factory._get_freshness_checks(
            self.partitioned_replication_config)
        self.assertIsNotNone(freshness_checks)

    def test_raise_get_freshness_checks(self):
        with self.assertRaises(TypeError):
            self.factory._get_freshness_checks(self.bad_partitioned_replication_config)

if __name__ == "__main__":
    unittest.main()