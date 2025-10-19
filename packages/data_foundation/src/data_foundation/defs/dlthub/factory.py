"""Factory helpers that translate dlt resources into Dagster definitions."""

import importlib
from collections.abc import Generator, Sequence
from datetime import timedelta
from functools import cache
from pathlib import Path
from typing import Any

import dagster as dg
import dlt
import yaml
from dagster_dlt import DagsterDltResource, dlt_assets
from dagster_dlt.dlt_event_iterator import DltEventType
from data_platform_utils.helpers import (
    get_automation_condition_from_meta,
    get_nested,
    get_schema_name,
    sanitize_input_signature,
)
from dlt.extract.resource import DltResource

from .translator import CustomDagsterDltTranslator


class DagsterDltFactory:
    """Utility class for building Dagster ``Definitions`` from dlt resources."""
    @cache
    @staticmethod
    def build_definitions(config_dir: Path) -> dg.Definitions:
        """Create Dagster definitions from a directory of dlt YAML configs and python
        scripts.

        Args:
            config_dir: Absolute path to the folder containing dlt configuration
                files.

        Returns:
            Definitions containing assets, resources, and freshness checks derived from
                the provided configuration files.
        """
        resources = {}
        freshness_checks = []
        resource_configs, source_configs = DagsterDltFactory._get_configs(config_dir)

        for config in resource_configs.values():
            if resource := (DagsterDltFactory
                            ._build_resource_from_config(config, resources)):
                resource_name = config["name"]
                resources[resource_name] = resource

            if freshness_check := (DagsterDltFactory
                                   ._build_freshness_checks(config)):
                freshness_checks.extend(freshness_check)

        assets = []

        # bundle resources into sources
        for source_config in source_configs.values():
            assets_definition, resources = (DagsterDltFactory
                                ._build_assets_from_source(resources, source_config))
            assets.append(assets_definition)

        # any left over resource will be put into its own stand alone source
        for resource_name, resource in resources.items():
            resource_config = resource_configs[resource_name]
            assets_definition = (DagsterDltFactory
                                ._build_source_from_resource(resource, resource_config))
            assets.append(assets_definition)

        # build stub external assets to allow for external materialization triggers
        for config in resource_configs.values():
            if external_assets_definition := (DagsterDltFactory
                                ._build_external_asset_from_config(config)):
                assets.append(external_assets_definition)

        return dg.Definitions(
            resources={"dlt": DagsterDltResource()},
            assets=assets,
            asset_checks=freshness_checks
        )

    @staticmethod
    def _get_configs(config_dir: Path) -> tuple[dict[Any, Any], dict[Any, Any]]:
        """Invoke the dlt pipeline and stream structured event data.

        Args:
            config_dir: The path to the root folder where dlt configs are located.

        Yields:
            Tuple of two dictionaries, containing the resource, and source YAML configs.
        """
        resource_configs = {}
        source_configs = {}
        config_paths = set()
        patterns = ["**/*.yaml", "**/*.yml"]
        for pattern in patterns:
            config_paths = config_paths.union(config_dir.resolve().glob(pattern))
        
        for config_path in config_paths:
            with open(config_path) as file:
                data = yaml.load(file, Loader=yaml.FullLoader) or {}
            resource_config = data.get("resources", {})
            for name, attributes in resource_config.items():
                parent = config_path.parent.name
                if attributes:
                    attributes["entry"] = parent+"."+attributes["entry"]
                    attributes["name"] = name
                    resource_configs[name] = attributes
            
            source_config = data.get("sources", {})
            for name, attributes in source_config.items():
                if attributes:
                    attributes["name"] = name
                    source_configs[name] = attributes

        return resource_configs, source_configs

    @staticmethod
    def _build_resource_from_config(config: dict, resources):
        """TODO"""
        data = DagsterDltFactory._build_data_generator(config)
        sanitized_config = sanitize_input_signature(dlt.resource, config)

        # swap string reference with hard reference to the instantiated resource
        if config.get("data_from"):
            table_name = config.get("name", "").split(".")[0]
            sanitized_config["data_from"] = resources[config["data_from"]]
            sanitized_config["table_name"] = table_name or config["table_name"]
        return dlt.resource(data, **sanitized_config)    

    @staticmethod
    def _build_freshness_checks(
            config: dict) -> Sequence[dg.AssetChecksDefinition] | None:
        """Build asset freshness checks based on the meta property in the YAML 
        configuration

        Args:
            meta: the meta property from the YAML configuration
            schema: The schema of the target table
            table: The table name of the target table

        Returns:
            A sequence of asset checks definitions to monitor for SLA violations.
        """
        if delta := get_nested(
            config, ["meta", "dagster", "freshness_lower_bound_delta_seconds"]
        ):
            schema, table = config["name"].split(".")
            asset_key = dg.AssetKey([schema, "raw", table])
            last_update_freshness_check = dg.build_last_update_freshness_checks(
                assets=[asset_key],
                lower_bound_delta=timedelta(seconds=float(delta)),
            )
            return last_update_freshness_check

    @staticmethod
    def _build_assets_from_source(resources: dict, config: dict):
        remaining_resources = resources
        selected_resources = ()
        for bundled_resource in config.get("resources", []):
            selected_resources += (remaining_resources.pop(bundled_resource),)

        sanitized_config = sanitize_input_signature(dlt.source, config)
        @dlt.source(**sanitized_config)
        def source(
                selected_resources=selected_resources) -> Generator[DltResource, Any]:
            """TODO
            """
            yield from selected_resources

        assets_definition = DagsterDltFactory._build_assets_definition(source, config)

        return assets_definition, remaining_resources

    @staticmethod
    def _build_source_from_resource(
            resource, config: dict) -> dg.AssetsDefinition:
        """TODO
        """
        sanitized_config = sanitize_input_signature(dlt.source, config)
        sanitized_config["name"] = config["name"].split(".")[0]
        @dlt.source(**sanitized_config)
        def source(resource=resource) -> Generator[DltResource, Any]:
            yield resource

        assets_definition = DagsterDltFactory._build_assets_definition(source, config)

        return assets_definition

    @staticmethod
    def _build_data_generator(resource_config: dict) -> Generator[Any, Any, None]:
        """TODO
        """
        entry_parts = resource_config["entry"].split(".")
        module_path = ".".join(entry_parts[:-1])
        function_name = entry_parts[-1]

        module = importlib.import_module(
            # TODO better relative import using pathlib
            "data_foundation.defs.dlthub.dlthub." + module_path
        )

        data_generator = getattr(module, function_name)
        args = resource_config.get("arguments", [])
        kwargs = resource_config.get("keyword_arguments", {})

        # if second order function, pass arguments to get the wrapped generator
        if args or kwargs:
            if not isinstance(args, list):
                args = [args]
            data_generator = data_generator(*args, **kwargs)
        return data_generator

    @staticmethod
    def _build_assets_definition(source, config) -> dg.AssetsDefinition:
        """TODO
        """

        condition = None
        if meta := get_nested(config.get("meta", {}), ["dagster"]):
            condition = get_automation_condition_from_meta(meta)

        sanitized_name = config["name"].replace(".", "__")
        schema_name = get_schema_name(config["name"].split(".")[0])
        @dlt_assets(
            name=sanitized_name,
            op_tags={"tags": config.get("tags")},
            dlt_source=source(),
            backfill_policy=dg.BackfillPolicy.single_run(),
            pool="dlthub",
            dagster_dlt_translator=CustomDagsterDltTranslator(
                automation_condition=condition
            ),
            dlt_pipeline=dlt.pipeline(
                pipeline_name=sanitized_name,
                destination="snowflake",
                dataset_name=schema_name,
                progress="log",
            ),
        )
        def assets(
            context: dg.AssetExecutionContext,
            dlt: DagsterDltResource
        ) -> Generator[DltEventType, Any]:
            """Invoke the dlt pipeline and stream structured event data.

            Args:
                context: Dagster execution context supplying runtime configuration.
                dlt: Dagster resource for executing the dlt pipeline.

            Yields:
                dagster_dlt.dlt_event_iterator.DltEventType: Structured events emitted
                    from the dlt pipeline run which Dagster converts into asset
                    materialize events.
            """
            yield from dlt.run(context=context)

        return assets

    @staticmethod
    def _build_external_asset_from_config(config) -> dg.AssetSpec | None:
        schema, table = config["name"].split(".")
        if not config.get("data_from"):
            external_asset = dg.AssetSpec(
                key=[schema, "src", table],
                kinds=config.get("kinds", {}),
                group_name=schema,
            )
            return external_asset