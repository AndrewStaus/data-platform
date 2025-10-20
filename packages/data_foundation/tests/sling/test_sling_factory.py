import unittest
from unittest.mock import patch

from dagster_sling import SlingConnectionResource
from data_foundation.defs.sling.factory import Factory

FACTORY = "data_foundation.defs.sling.factory.Factory"

class TestFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.factory = Factory()
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
                            "automation_condition": "on_schedule",
                            "tags": ["contains_pii"],
                            "automation_condition_config": {
                                "cron_schedule":"@daily",
                                "cron_timezone":"utc"}}}}}}

class TestBuildDefinitions(TestFactory): ...

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

class TestParseReplication(TestFactory): ...
class TestCreateAsset(TestFactory): ...
class TestSetSchema(TestFactory): ...
class TestGetSlingDeps(TestFactory): ...
class TestGetFreshnessChecks(TestFactory): ...


if __name__ == "__main__":
    unittest.main()