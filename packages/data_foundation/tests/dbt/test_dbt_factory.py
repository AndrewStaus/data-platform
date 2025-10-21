# test_factory.py

import unittest
from unittest.mock import MagicMock, patch

import dagster as dg
from data_foundation.defs.dbt.factory import Factory


class TestFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_project = MagicMock()
        cls.mock_project.manifest_path = "/fake/path/manifest.json"
        cls.mock_dbt_callable = staticmethod(lambda: cls.mock_project)
        cls.mock_assets_definition = MagicMock(spec=dg.AssetsDefinition)
        cls.mock_freshness_checks = [MagicMock(spec=dg.AssetChecksDefinition)]
        cls.mock_sensor = MagicMock(spec=dg.SensorDefinition)


class TestBuildDefinitions(TestFactory):

    @patch("data_foundation.defs.dbt.factory.Factory._get_assets")
    @patch("data_foundation.defs.dbt.factory.build_freshness_checks_from_dbt_assets")
    @patch("data_foundation.defs.dbt.factory.dg.build_sensor_for_freshness_checks")
    @patch("data_foundation.defs.dbt.factory.DbtCliResource")
    def test_builds_correct_definitions(
                self,
                mock_dbt_cli_resource,
                mock_build_sensor,
                mock_build_freshness,
                mock_get_assets,
            ):
        # Arrange
        Factory.build_definitions.cache_clear()
        mock_get_assets.side_effect = [self.mock_assets_definition]*2
        mock_build_freshness.return_value = self.mock_freshness_checks
        mock_build_sensor.return_value = self.mock_sensor
        mock_dbt_cli_resource.return_value = MagicMock()

        # Act
        definitions = Factory.build_definitions(self.mock_dbt_callable)

        # Assert
        self.assertIsInstance(definitions, dg.Definitions)
        self.assertIn("dbt", definitions.resources)
        self.assertEqual(definitions.assets, [self.mock_assets_definition]*2)
        self.assertEqual(definitions.asset_checks, self.mock_freshness_checks)
        self.assertEqual(definitions.sensors, [self.mock_sensor])


class TestGetAssets(TestFactory):

    @patch("data_foundation.defs.dbt.factory.dbt_assets")
    def test_get_assets_non_partitioned(self, mock_dbt_assets) -> None:
        # Arrange
        mock_dbt_project = MagicMock()
        mock_dbt_project.manifest_path = "/path/to/manifest.json"

        mock_assets_fn = MagicMock()
        mock_assets_def = MagicMock(spec=dg.AssetsDefinition)
        mock_assets_fn.return_value = mock_assets_def
        mock_dbt_assets.return_value = mock_assets_fn

        # Act
        result = Factory._get_assets(
            name="test_asset",
            dbt=lambda: mock_dbt_project,
            partitioned=False,
            select="some:select",
            exclude="some:exclude"
        )

        # Assert
        self.assertEqual(result, mock_assets_def)
        mock_dbt_assets.assert_called_once()
        kwargs = mock_dbt_assets.call_args.kwargs
        self.assertEqual(kwargs["name"], "test_asset")
        self.assertEqual(kwargs["manifest"], "/path/to/manifest.json")
        self.assertEqual(kwargs["select"], "some:select")
        self.assertEqual(kwargs["exclude"], "some:exclude")
        self.assertEqual(kwargs["pool"], "dbt")

    @patch("data_foundation.defs.dbt.factory.dbt_assets")
    def test_get_assets_partitioned_injects_vars(self, mock_dbt_assets):
        # Arrange
        mock_dbt_project = MagicMock()
        mock_dbt_project.manifest_path = "/path/to/manifest.json"

        # Mock time window partition context
        mock_context = MagicMock()
        mock_context.partition_time_window.start.strftime.return_value = (
            "2023-01-01 00:00:00")
        mock_context.partition_time_window.end.strftime.return_value = (
            "2023-01-02 00:00:00"
        )

        # Mock dbt CLI resource
        mock_dbt_resource = MagicMock()
        mock_dbt_resource.cli.return_value.stream.return_value = (
            iter(["event1", "event2"])
        )

        # Mock asset function return
        def mock_assets_fn(context, dbt, config):
            return list(Factory._get_assets
                        .latest_args["inner_fn"](context, dbt, config))

    def test_get_assets_raises_if_dbt_callable_returns_none(self):
        # Act / Assert
        with self.assertRaises(AssertionError):
            Factory._get_assets(
                name="invalid_asset",
                dbt=lambda: None # broken dbt
            )