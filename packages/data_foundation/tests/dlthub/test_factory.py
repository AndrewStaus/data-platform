import inspect
import shutil
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import dagster as dg
import dlt
import yaml
from data_foundation.defs.dlthub.factory import Factory
from dlt.extract.resource import DltResource

FACTORY = "data_foundation.defs.dlthub.factory.Factory"

class TestCases(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.resources = {
            "source_1.resource_1": {
                "name": "source_1.resource_1",
                "config_path": inspect.getfile(Factory),
                "entry": "data.func",
                "primary_key": "id",
                "write_disposition": "merge",
                "kinds": {"api"}
            },
            "source_2.resource_2": {
                "name": "source_2.resource_2",
                "config_path": inspect.getfile(Factory),
                "entry": "data.func",
                "primary_key": "id",
                "write_disposition": "merge",
                "kinds": {"api"},
                "meta": {
                    "dagster": {
                        "freshness_lower_bound_delta_seconds": 108000,
                        "automation_condition": "on_schedule",
                        "automation_condition_config": {
                            "cron_schedule": "@daily",
                            "cron_timezone": "utc"
                        },
                    }
                }
            },
            "source_2.resource_3": {
                "name": "source_2.resource_3",
                "config_path": inspect.getfile(Factory),
                "entry": "data.func",
                "data_from": "source_2.resource_2",
                "arguments": "endpoint",
                "primary_key": "id",
                "write_disposition": "merge",
                "kinds": {"api"}
            }
        }
    
        cls.sources = {
            "source_1": {
                "name": "source_1",
                "resources": ["source_1.resource_1"],
                "parallelized": True,
                "meta": {
                    "dagster": {
                        "freshness_lower_bound_delta_seconds": 108000,
                        "automation_condition": "on_schedule",
                        "automation_condition_config": {
                            "cron_schedule": "@daily",
                            "cron_timezone": "utc"
                        },
                    }
                }
            }
        }

class TestBuildDefinitions(TestCases):

    @patch("data_foundation.defs.dlthub.factory.DagsterDltResource")
    @patch(f"{FACTORY}._build_external_asset", return_value=None)
    @patch(f"{FACTORY}._build_assets_from_resource")
    @patch(f"{FACTORY}._build_assets_from_source")
    @patch(f"{FACTORY}._build_freshness_checks")
    @patch(f"{FACTORY}._build_resource_from_config")
    @patch(f"{FACTORY}._get_configs")
    def test_build_definitions_returns_definitions(self,
                                    mock_get_configs,
                                    mock_build_resource_from_config,
                                    mock_build_freshness_checks,
                                    mock_build_assets_from_source,
                                    mock_build_assets_from_resource,
                                    mock_build_external_asset,
                                    mock_dlt_resource,
                                ) -> None:

        @dg.asset
        def asset():
            return 1
        
        @dg.resource
        def resource():
            yield [1]

        resources = {"source_1.resource_1":resource}

        last_update_freshness_check = dg.build_last_update_freshness_checks(
            assets=["x"],
            lower_bound_delta=timedelta(seconds=float(99999))  # noqa: F821
        )

        mock_get_configs.return_value = (self.resources, self.sources)
        mock_build_resource_from_config.return_value = resource
        mock_build_freshness_checks.return_value = last_update_freshness_check
        mock_build_assets_from_source.return_value = (asset, resources)
        mock_build_assets_from_resource.return_value = asset
        mock_build_external_asset.return_value = dg.AssetSpec(["schema", "src", "table"])

        definitions = Factory.build_definitions(Path("/some/path"))

        self.assertIsInstance(definitions, dg.Definitions)
        self.assertIn("dlt", definitions.resources)
        self.assertIsInstance(definitions.assets, list)
        self.assertIsInstance(definitions.asset_checks, list)

    @patch("data_foundation.defs.dlthub.factory.DagsterDltResource")
    @patch(f"{FACTORY}._build_external_asset", return_value=None)
    @patch(f"{FACTORY}._build_assets_from_resource")
    @patch(f"{FACTORY}._build_assets_from_source")
    @patch(f"{FACTORY}._build_freshness_checks")
    @patch(f"{FACTORY}._build_resource_from_config")
    @patch(f"{FACTORY}._get_configs")
    def test_build_definitions_returns_definitions_with_sparse_configs(self,
                                    mock_get_configs,
                                    mock_build_resource_from_config,
                                    mock_build_freshness_checks,
                                    mock_build_assets_from_source,
                                    mock_build_assets_from_resource,
                                    mock_build_external_asset,
                                    mock_dlt_resource,
                                ) -> None:

        @dg.asset
        def asset():
            return 1
        
        @dg.resource
        def resource():
            yield [1]

        resources = {}

        mock_get_configs.return_value = (self.resources, {})
        mock_build_resource_from_config.return_value = resource
        mock_build_freshness_checks.return_value = None
        mock_build_assets_from_source.return_value = (asset, resources)
        mock_build_assets_from_resource.return_value = asset
        mock_build_external_asset.return_value = dg.AssetSpec(["schema", "src", "table"])

        definitions = Factory.build_definitions(Path("/some/path"))

        self.assertIsInstance(definitions, dg.Definitions)
        self.assertIn("dlt", definitions.resources)
        self.assertIsInstance(definitions.assets, list)
        self.assertIsInstance(definitions.asset_checks, list)

class TestGetConfigs(TestCases):

    def setUp(self):
        # Create a temporary directory to simulate the config directory
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir)

        # Sample YAML config content
        self.sample_config_1 = {
            "resources": {
                "resource1": {
                    "entry": "main",
                    "param": "value1"
                }
            },
            "sources": {
                "source1": {
                    "param": "value2"
                }
            }
        }

        self.sample_config_2 = {
            "resources": {
                "resource2": {
                    "entry": "load",
                    "param": "value3"
                }
            }
        }

        # Write sample YAML files
        self.sub_dir = self.config_dir / "submodule"
        self.sub_dir.mkdir()
        with open(self.sub_dir / "config1.yaml", "w") as f:
            yaml.dump(self.sample_config_1, f)

        with open(self.sub_dir / "config2.yml", "w") as f:
            yaml.dump(self.sample_config_2, f)

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_get_configs_parses_correctly(self):
        resource_configs, source_configs = Factory._get_configs(self.config_dir)

        # Test resource_configs
        self.assertIn("resource1", resource_configs)
        self.assertIn("resource2", resource_configs)
        self.assertEqual(resource_configs["resource1"]["entry"], "submodule.main")
        self.assertEqual(resource_configs["resource2"]["entry"], "submodule.load")
        self.assertEqual(resource_configs["resource1"]["name"], "resource1")
        self.assertIsInstance(resource_configs["resource1"]["config_path"], Path)

        # Test source_configs
        self.assertIn("source1", source_configs)
        self.assertEqual(source_configs["source1"]["name"], "source1")
        self.assertEqual(source_configs["source1"]["param"], "value2")

class TestBuildResourceFromConfig(TestCases):

    @patch(f"{FACTORY}._build_data_generator")
    def test_build_resource_singular(self, mock_build_data_generator):

        def generator():
            yield from [1]

        mock_build_data_generator.return_value = generator

        resources = {}
        resource = Factory._build_resource_from_config(
                self.resources["source_1.resource_1"], resources)
        self.assertIsInstance(resource, DltResource)

    @patch(f"{FACTORY}._build_data_generator")
    def test_build_resource_pipeline(self, mock_build_data_generator):

        def generator(arg):
            yield from [1]

        @dlt.resource()
        def resource():
            yield from [1]

        mock_build_data_generator.return_value = generator

        resources = {"source_2.resource_2": resource}
        resource = Factory._build_resource_from_config(
                self.resources["source_2.resource_3"], resources)
        self.assertIsInstance(resource, DltResource)

class TestBuildFreshnessChecks(TestCases):

    def test_build_freshness_checks_parses_correctly(self) -> None:
        asset_checks = Factory._build_freshness_checks(
            self.resources["source_2.resource_2"])
        self.assertIsInstance(asset_checks[0], dg.AssetChecksDefinition)

    def test_build_freshness_checks_handles_no_config(self) -> None:
        asset_checks = Factory._build_freshness_checks(
            self.resources["source_1.resource_1"])
        self.assertIs(asset_checks, None)


class TestBuildAssetsFromSource(TestCases):

    @patch(f"{FACTORY}._build_assets_definition")
    def test_build_assets_from_source(self, mock_build_assets_definition):

        @dg.asset(name="test.asset")
        def asset():
            return None

        mock_build_assets_definition.return_value = asset

        @dlt.resource()
        def resource():
            yield from [1]

        config = self.sources["source_1"]
        resources = self.resources

        assets, resources = Factory._build_assets_from_source(resources, config)
        self.assertIsInstance(assets, dg.AssetsDefinition)
        self.assertEqual(len(resources), 2)
        self.assertTrue(resources.get("source_2.resource_2"))

    @patch(f"{FACTORY}._build_assets_definition")
    def test_build_assets_definition_key_exception(self, mock_build_assets_definition):

        @dg.asset(name="test.asset")
        def asset():
            return None

        mock_build_assets_definition.return_value = asset

        @dlt.resource()
        def resource():
            yield from [1]

        config = self.sources["source_1"]
        resources = {}

        with self.assertRaises(KeyError):
            Factory._build_assets_from_source(resources, config)

class TestBuildAssetsFromResource(TestCases):
    
    @patch(f"{FACTORY}._build_assets_definition")
    def test_build_assets_definition_parses(self, mock_build_assets_definition):

        @dg.asset(name="test.asset")
        def asset():
            return None

        mock_build_assets_definition.return_value = asset

        @dlt.resource()
        def resource():
            yield from [1]

        config = self.resources["source_1.resource_1"]
        assets = Factory._build_assets_from_resource(resource, config)
        self.assertIsInstance(assets, dg.AssetsDefinition)
    

class TestBuildDataGenerator(TestCases):

    @patch("importlib.import_module")
    def test_get_first_order_generator(self, mock_import_module) -> None:
        class data:
            @staticmethod
            def func(self):
                yield from [1]

        mock_import_module.resturn_value = data

        config = self.resources["source_1.resource_1"]
        generator = Factory._build_data_generator(config)
        self.assertTrue(generator)

    @patch("importlib.import_module")
    def test_get_second_order_generator(self, mock_import_module) -> None:
        class data:
            @staticmethod
            def func(self, foo):
                def generator():
                    yield from [1]
                return generator

        mock_import_module.resturn_value = data

        config = self.resources["source_2.resource_3"]
        generator = Factory._build_data_generator(config)
        self.assertTrue(generator)

class TestBuildAssetsDefinition(TestCases):

    def test_build_assets_definition_returns_valid_object(self):

        config = self.resources["source_2.resource_2"]
        @dlt.resource()
        def resource():
            yield 1

        @dlt.source()
        def source_factory(resource=resource):
            yield resource
        
        assets_definition = Factory._build_assets_definition(source_factory, config)
        self.assertIsInstance(assets_definition, dg.AssetsDefinition)

class TestBuildExternalAsset(TestCases):

    def test_build_external_asset_parses(self):
        config = self.resources["source_1.resource_1"]
        asset_spec = Factory._build_external_asset(config)
        self.assertIsInstance(asset_spec, dg.AssetSpec)

        key_parts = asset_spec.key.parts
        self.assertEqual(len(key_parts), 3)
        self.assertEqual(key_parts[0], "source_1")
        self.assertEqual(key_parts[1], "src")
        self.assertEqual(key_parts[2], "resource_1")
