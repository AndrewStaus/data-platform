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
from data_platform_utils.helpers import get_nested, get_schema_name
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
        asset_checks = []
        assets = []
        configs = DagsterDltFactory._get_configs(config_dir)
        for name, config in configs.items():
            parsed_config = DagsterDltFactory._parse_config(name, config)
            assets_definition, dep, checks = parsed_config

            assets.append(assets_definition)
            assets.append(dep)
            asset_checks.extend(checks or [])
        
        return dg.Definitions(
            resources={"dlt": DagsterDltResource()},
            assets=assets,
            asset_checks=asset_checks
        )

    @staticmethod
    def _get_configs(config_dir: Path) -> dict:
        """Invoke the dlt pipeline and stream structured event data.

        Args:
            config_dir: The path to the root folder where dlt configs are located.

        Yields:
            A dictonary containing all of the YAML configs.
        """
        configs = {}
        config_paths = set()
        patterns = ["**/*.yaml", "**/*.yml"]
        for pattern in patterns:
            config_paths = config_paths.union(config_dir.resolve().glob(pattern))
        
        for config_path in config_paths:
            with open(config_path) as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                for name, values in config.items():
                    parent = config_path.parent.name
                    values["entry"] = parent+"."+values["entry"]
                    configs[name] = values
        return configs

    @staticmethod
    def _build_assets(resource: DltResource, schema: str,
                    table: str, tags: set) -> dg.AssetsDefinition:
        """Build Dagster assets from a dlt resource, along with metadata from the YAML
        config.

        Args:
            resource: A dlt resource that can be invoked at run time.
            schema: The target schema, used to generate a unique asset key.
            table: The target table, used to generate a unique asset key.
            tags: Metadata tags for discoverability in the dagster asset catalog.

        Returns:
            A dagster asset definition.
        """

        @dlt.source()
        def source(resource=resource) -> Generator[DltResource, Any]:
            yield resource

        @dlt_assets(
            name=f"{schema}__{table}",
            op_tags={"tags": tags},
            dlt_source=source(),
            backfill_policy=dg.BackfillPolicy.single_run(),
            dagster_dlt_translator=CustomDagsterDltTranslator(),
            pool="dlthub",
            dlt_pipeline=dlt.pipeline(
                pipeline_name=f"{schema}__{table}",
                destination="snowflake",
                dataset_name=get_schema_name(schema),
                progress="log",
            ),
        )
        def assets(
            context: dg.AssetExecutionContext, dlt: DagsterDltResource
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
    def _build_freshness_checks(meta: dict, schema: str, table: str
                                ) -> Sequence[dg.AssetChecksDefinition] | None:
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
            meta, ["dagster", "freshness_lower_bound_delta_seconds"]
        ):
            asset_key = dg.AssetKey([schema, "raw", table])
            last_update_freshness_check = dg.build_last_update_freshness_checks(
                assets=[asset_key],
                lower_bound_delta=timedelta(seconds=float(delta)),
            )
            return last_update_freshness_check

    @staticmethod
    def _build_generator(entry: str,
                         args: list,
                         kwargs: dict) -> Generator[Any, Any, None]:
        """Instantiate a generator that yeilds data from the data source.

        Args:
            entry: The import path of the generator realative to
                data_foundation.defs.dlthub.dlthub
            args: If the entry is a second order funtion, the arguments to return the
                generator.
            kwargs: If the entry is a second order funtion, the key word arguments to
                return the generator.

        Returns:
            A generator object that dlt will use to retreive paginated data for
            ingestion.
        """
        entry_parts = entry.split(".")
        module_path = ".".join(entry_parts[:-1])
        function_name = entry_parts[-1]

        data: Generator[Any, Any, None]
        module = importlib.import_module(
            "data_foundation.defs.dlthub.dlthub"+module_path
        )
        generator = getattr(module, function_name)

        data = generator
        if args or kwargs:
            data = generator(*args, **kwargs)
        return data

    @staticmethod
    def _parse_config(name: str, config: dict
                      ) -> tuple[dg.AssetsDefinition,
                                 dg.AssetSpec,
                                 Sequence[dg.AssetChecksDefinition] | None]:
        """Parse a YAML file contents to create dagster resources.

        Args:
            name: The name of the resouce in format {schema}.{table}.
            connection_configs: Raw configuration dictionaries from YAML.

        Returns:
            A tuple containing the assets, dependancies, and freshness checks.
        """
        schema, table = name.split(".")

        # remove non-dlt keys so that it matches dlt.resource function signature
        meta: dict = config.pop("meta", {})
        kinds: set = config.pop("kinds")
        tags: set = config.pop("tags")
        entry: str = config.pop("entry")
        args: list = config.pop("arguments", [])
        kwargs: dict = config.pop("keyword_arguments", {})

        # set table name if not defined
        config["table"] = config.get("table") or table

        # build assets and checks
        data = DagsterDltFactory._build_generator(entry, args, kwargs)
        resource: DltResource = dlt.resource(data, **config)
        assets = DagsterDltFactory._build_assets(resource, schema, table, tags)
        dep = dg.AssetSpec(
            [schema, "src", table], kinds=kinds, group_name=schema
        )
        freshness_check = DagsterDltFactory._build_freshness_checks(meta, schema, table)
        
        return assets, dep, freshness_check