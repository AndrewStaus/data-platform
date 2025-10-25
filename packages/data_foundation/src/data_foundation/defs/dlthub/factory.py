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
from dlt.extract.decorators import ResourceFactory
from dlt.extract.reference import SourceFactory
from dlt.extract.resource import DltResource

from .translator import CustomDagsterDltTranslator


class Factory:
    """Utility class for building Dagster ``Definitions`` from dlt resources."""
    @cache
    @staticmethod
    def build_definitions(config_dir: Path) -> dg.Definitions:
        """ Build Dagster definitions from a directory containing dlt YAML
        configurations and Python scripts.

        This method parses dlt resource and source configurations from the specifie
        directory, constructs corresponding Dagster assets and resources, adds any
        defined freshness checks,  and returns a `Definitions` object for use in a
        Dagster project.

        Args:
            config_dir:
                Absolute path to the directory containing dlt configuration files,
                including YAML resource/source definitions and any accompanying Python
                scripts.

        Returns:
            A Definitions object containing a resouce, assets, and asset checks.
        """
        resources = {}
        freshness_checks = []
        resource_configs, source_configs = Factory._get_configs(config_dir)

        for config in resource_configs.values():
            if resource := (Factory
                            ._build_resource_from_config(config, resources)):
                resource_name = config["name"]
                resources[resource_name] = resource

            if freshness_check := (Factory
                                   ._build_freshness_checks(config)):
                freshness_checks.extend(freshness_check)

        assets = []

        # bundle resources into sources
        for source_config in source_configs.values():
            assets_definition, resources = (Factory
                                ._build_assets_from_source(resources, source_config))
            assets.append(assets_definition)

        # any left over resource will be put into its own stand alone source
        for resource_name, resource in resources.items():
            resource_config = resource_configs[resource_name]
            assets_definition = (Factory
                                ._build_assets_from_resource(resource, resource_config))
            assets.append(assets_definition)

        # build stub external assets to allow for external materialization triggers
        for config in resource_configs.values():
            if external_assets_definition := (Factory
                                ._build_external_asset(config)):
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
            Tuple of two dictionaries, containing the resource, and source YAML
                configs.
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
                    attributes["config_path"] = config_path
                    resource_configs[name] = attributes
            
            source_config = data.get("sources", {})
            for name, attributes in source_config.items():
                if attributes:
                    attributes["name"] = name
                    source_configs[name] = attributes

        return resource_configs, source_configs

    @staticmethod
    def _build_resource_from_config(config: dict,
                                resources: dict[str, DltResource]) -> ResourceFactory:
        """Build dlt resource from values from the resource section of the config.
        If a resource has reference to another resource by key, the key is replaced
        with the instantiated object.

        Args:
            config: a resource config
            resources: the list of built resources already built for replacing
                key references.

        Retruns:
            Instantiated dlt resource object.
        """
        data = Factory._build_data_generator(config)
        sanitized_config = sanitize_input_signature(dlt.resource, config)

        table_name = config.get("name", "").split(".")[-1]
        sanitized_config["table_name"] = table_name or config["table_name"]

        # swap string reference with hard reference to the instantiated resource
        if config.get("data_from"):
            sanitized_config["data_from"] = resources[config["data_from"]]
        return dlt.resource(data, **sanitized_config)    

    @staticmethod
    def _build_freshness_checks(
            config: dict) -> Sequence[dg.AssetChecksDefinition] | None:
        """Build asset freshness checks based on the meta property in the YAML 
        configuration

        Args:
            config: The resource or source config which may contain a meta property

        Returns:
            A sequence of asset checks definitions to allow dagster to monitor for SLA
                violations.
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
    def _build_assets_from_source(resources: dict,
                        config: dict) -> tuple[dg.AssetsDefinition, dict[Any, Any]]:
        """Builds an AssetsDefinition from a source config, assigning resources
        listed in the assets parameter of the config to be members of the source.
        Returns both the resulting AssetsDefinition and the remaining unassigned
        resources.

        Args:
            resources: A dictionary of available resource instances, where keys are
                resource names.
            config: A dictionary specifying configuration options for the source.

        Returns: 
            A tuple containing An `AssetsDefinition` and A dictonary of the remaining
                resources not assigned to the source.

        Raises:
            KeyError: 
                If a resource listed in `config["resources"]` is not found in the
                provided `resources` dictionary.
        """
        remaining_resources = resources
        selected_resources = ()
        for bundled_resource in config.get("resources", []):
            try:
                selected_resources += (remaining_resources.pop(bundled_resource),)
            except KeyError as e:
                e.add_note(f"Resource '{bundled_resource}' could not be assigned to "
                    f"source: '{config['name']}'. Make sure that the resouce is "
                    "defined, and not assigned to another source.")
                raise e

        sanitized_config = sanitize_input_signature(dlt.source, config)
        @dlt.source(**sanitized_config)
        def source_factory(
                selected_resources=selected_resources) -> Generator[DltResource, Any]:
            yield from selected_resources # pragma: no cover

        assets_definition = Factory._build_assets_definition(source_factory, config)

        return assets_definition, remaining_resources

    @staticmethod
    def _build_assets_from_resource(
            resource: DltResource, config: dict) -> dg.AssetsDefinition:
        """
        Builds a Dagster AssetsDefinition from a single dlt resource.

        This method wraps a single dlt resource into a dlt source using the provided
        configuration, and then builds an `AssetsDefinition` from that source.

        Args:
            resource: A DLT resource instance to be wrapped into a source and converted
                into a Dagster asset.
            config: A dictionary containing configuration for the source.

        Returns:
            An `AssetsDefinition` object representing the asset generated from the
                provided resource.
        """
        sanitized_config = sanitize_input_signature(dlt.source, config)
        sanitized_config["name"] = config["name"].split(".")[0]
        @dlt.source(**sanitized_config)
        def source_factory(resource=resource) -> Generator[DltResource, Any]:
            yield resource # pragma: no cover

        assets_definition = Factory._build_assets_definition(source_factory, config)

        return assets_definition

    @staticmethod
    def _build_data_generator(resource_config: dict) -> Generator[Any, Any, None]:
        """ Dynamically imports and initializes a data generator function based on a
        resource configuration.

        This method resolves and imports a Python module and function based on the
        `entry` key in the 
        provided `resource_config`, which is expected to be a dotted path relative to.
        the yaml file. If the function is a second order funcion, then it is called
        using the configured args, and kwargs to get the generator.

        Args:
            resource_config:
                A dictionary containing configuration for loading the data generator,
                including:
                    - "entry" (str): A dotted path to the target function
                        (e.g. "module.submodule.function").
                    - "config_path" (str): Path to the configuration file, used to
                        resolve the module location.
                    - "arguments" (optional): A list (or single value) of positional
                        arguments to pass to the function.
                    - "keyword_arguments" (optional): A dictionary of keyword arguments
                        to pass to the function.

        Returns:
            A generator instance returned by the specified function, optionally called
                with arguments.

        Raises:
            ModuleNotFoundError: If the specified module cannot be resolved or imported.
            AttributeError: If the specified function does not exist in the resolved
                module.
            TypeError: If argument types are incorrect for the function being called.
            ValueError: If config paths cannot be resolved relative to the source file.
        """
        entry_parts = resource_config["entry"].split(".")
        module_dir = (Path(resource_config["config_path"])
                   .relative_to(Path(__file__).parent).parent.parent)

        module_name = "."+".".join([*module_dir.parts, *entry_parts[:-1]])
        module = importlib.import_module(module_name, __package__)

        data_generator = getattr(module, entry_parts[-1])

        # if second order function, pass arguments to get the wrapped generator
        args = resource_config.get("arguments", [])
        kwargs = resource_config.get("keyword_arguments", {})
        if args or kwargs:
            if not isinstance(args, list):
                args = [args]
            data_generator = data_generator(*args, **kwargs)
        return data_generator

    @staticmethod
    def _build_assets_definition(source_factory: SourceFactory,
                                  config: dict) -> dg.AssetsDefinition:
        """Convert a source factory into a dagster assets definition so it can be
            materialized in the dagster interface.

            Args:
                source_factory:  A generator like factory that yeilds dlt sources.
                config: the config for the source that holds dagster metadata for
                    scheduling and control.

            Retruns:
                A dagster assets definition.
        """

        condition = None
        if meta := get_nested(config.get("meta", {}), ["dagster"]):
            condition = get_automation_condition_from_meta(meta)

        sanitized_name = config["name"].replace(".", "__")
        schema_name = get_schema_name(config["name"].split(".")[0])

        pipeline = dlt.pipeline(
            pipeline_name=sanitized_name,
            destination="snowflake",
            dataset_name=schema_name,
            progress="log",
        )

        @dlt_assets(
            name=sanitized_name,
            op_tags={"tags": config.get("tags")},
            dlt_source=source_factory(),
            backfill_policy=dg.BackfillPolicy.single_run(),
            pool=schema_name,
            dlt_pipeline=pipeline,
            dagster_dlt_translator=CustomDagsterDltTranslator(
                automation_condition=condition
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
                    dagster_dlt.dlt_event_iterator.DltEventType: Structured events
                        emitted from the dlt pipeline run which Dagster converts into
                        asset materialize events.
            """
            yield from dlt.run(context=context) # pragma: no cover

        return assets

    @staticmethod
    def _build_external_asset(config) -> dg.AssetSpec | None:
        """Constructs an external Dagster asset specification from the given
        configuration.

        If the configuration does not specify a data source (`data_from`), this function
        treats the asset as externally managed and builds a corresponding `AssetSpec` 
        to allow for external materialization triggers.

        Args:
            config:
                A dictionary containing asset metadata. Expected keys:
                    - "name" (str): The full asset name in "schema.table" format.
                    - "kinds" (optional): A dictionary of metadata about the asset kind.
                    - "data_from" (optional): If present, indicates the asset is
                        external.

        Returns:
            An `AssetSpec` object representing the external asset if `data_from` is not
                defined; otherwise, returns `None`.

        Raises:
            ValueError: If the "name" field is missing or not in the expected
                "schema.table" format.
        """
        schema, table = config["name"].split(".")
        if not config.get("data_from"):
            external_asset = dg.AssetSpec(
                key=[schema, "src", table],
                kinds=config.get("kinds", {}),
                group_name=schema,
            )
            return external_asset