"""Factory helpers for translating Sling YAML configs into Dagster definitions."""

from collections.abc import Generator
from datetime import timedelta
from functools import cache
from pathlib import Path
from typing import Any

import dagster as dg
import yaml
from dagster_sling import SlingConnectionResource, SlingResource, sling_assets
from dagster_sling.sling_event_iterator import SlingEventType
from data_platform_utils.helpers import (
    get_nested,
    get_schema_name,
    sanitize_input_signature,
)
from data_platform_utils.secrets import get_secret

from .translator import CustomDagsterSlingTranslator


class Factory:
    """Factory to generate Dagster definitions from Sling YAML config files."""

    @cache
    @staticmethod
    def build_definitions(config_dir: Path) -> dg.Definitions:
        """Create Dagster definitions from a directory of Sling YAML configs.

        Args:
            config_dir: Absolute path to the folder containing Sling configuration
                files.

        Returns:
            dagster.Definitions: Definitions containing assets, resources, and
                freshness checks derived from the provided configuration files.
        """
        connections = []
        assets = []
        freshness_checks = []
        kind_map = {}

        config_paths = set()
        patterns = ["**/*.yaml", "**/*.yml"]
        for pattern in patterns:
            config_paths = config_paths.union(config_dir.resolve().glob(pattern))

        for config_path in config_paths:
            config_path = config_dir.joinpath(config_path).resolve()
            with open(config_path) as file:
                config = yaml.load(file, Loader=yaml.FullLoader)

            if connection_configs := config.get("connections"):
                connections, kind_map = Factory._parse_connections(
                    connection_configs, connections, kind_map
                )

            if config.get("streams"):
                assets, freshness_checks = Factory._parse_replication(
                    config, freshness_checks, kind_map, assets
                )

        return dg.Definitions(
            resources={"sling": SlingResource(connections=connections)},
            assets=assets,
            asset_checks=freshness_checks,
            sensors=[
                dg.build_sensor_for_freshness_checks(
                    freshness_checks=freshness_checks,
                    name="sling_freshness_checks_sensor",
                )
            ],
        )

    @staticmethod
    def _parse_connections(
        connection_configs: dict, connections: list, kind_map: dict
    ) -> tuple[list[SlingConnectionResource], dict[str, str]]:
        """Parse connection blocks and produce Sling connection resources.

        Args:
            connection_configs: Raw connection configuration dictionaries from YAML.
            connections: Mutable list accumulating :class:`SlingConnectionResource`
                instances.
            kind_map: Mapping of connection names to their declared kinds.

        Returns:
            tuple[list[SlingConnectionResource], dict[str, str]]: The updated
                connections list and kind mapping including the newly processed entries.
        """
        # Each connection block yields a resource definition and updates the map of
        # connection names to their declared kinds.  The kind map is used later when
        # building external assets for dependencies.
        for source, connection_config in connection_configs.items():
            connection_config["name"] = source
            if connection := Factory._create_resource(connection_config):
                kind = connection_config.get("type")
                kind_map[source] = kind
                connections.append(connection)

        return connections, kind_map

    @staticmethod
    def _create_resource(connection_config: dict) -> SlingConnectionResource | None:
        """Materialize a Sling connection resource from a configuration dictionary.

        Args:
            connection_config: Configuration block describing the Sling connection.

        Returns:
            SlingConnectionResource | None: Concrete connection resource populated with
                secrets resolved from the key vault stub. Returns ``None`` when the
                config does not produce a valid resource.
        """
        for attribute, original_value in connection_config.items():
            parts = original_value.split(".")
            prefix = parts[0].lower()
            if prefix == "env": # ex: env.DESTINATION__SNOWFLAKE__HOST
                connection_config[attribute] = get_secret(parts[1]).get_value()
            elif prefix == "secret": # ex: secret.DESTINATION__SNOWFLAKE__PASSWORD
                connection_config[attribute] = get_secret(parts[1])
            else: # ex: postgres
                connection_config[attribute]  = original_value

        connection = SlingConnectionResource(**connection_config)
        return connection

    @staticmethod
    def _parse_replication(
        replication_config, freshness_checks, kind_map, assets
    ) -> tuple[list[dg.AssetsDefinition], list[dg.AssetChecksDefinition]]:
        """Construct Dagster assets and freshness checks for Sling replications.

        Args:
            replication_config: A replication configuration dictionaries.
            freshness_checks: Mutable list accumulating generated freshness checks.
            kind_map: Mapping of source names to their declared resource kind.
            assets: Mutable list accumulating Dagster asset definitions.

        Returns:
            tuple[list[dg.AssetsDefinition], list[dg.AssetChecksDefinition]]: Updated
                assets and freshness checks lists containing entries for the processed
                replications.
        """
        # Iterate through each replication block and build Dagster assets, any
        # associated freshness checks, and companion external assets for dependencies.
        replication_config = Factory._set_schema(replication_config)
        assets_definition = Factory._create_asset(replication_config)

        kind = kind_map.get(replication_config.get("source", None), None)
        dep_asset_specs = Factory._get_sling_deps(
            replication_config, kind
        )
        asset_freshness_checks = Factory._get_freshness_checks(
            replication_config
        )

        if asset_freshness_checks:
            freshness_checks.extend(asset_freshness_checks)
        if assets_definition:
            assets.append(assets_definition)
        if dep_asset_specs:
            assets.extend(dep_asset_specs)

        return assets, freshness_checks

    @staticmethod
    def _create_asset(config: dict) -> dg.AssetsDefinition:
        """Create a Dagster assets definition for a single Sling replication.

        Args:
            config: Sling replication configuration dictionary.

        Returns:
            dagster.AssetsDefinition: Assets definition that wraps the Sling
                replication and streams structured events back to Dagster.
        """

        @sling_assets(
            name=config["source"] + "_assets",
            replication_config=config,
            backfill_policy=dg.BackfillPolicy.single_run(),
            dagster_sling_translator=CustomDagsterSlingTranslator(),
            pool="sling",
        )
        def assets(
            context: dg.AssetExecutionContext, sling: SlingResource
        ) -> Generator[SlingEventType, Any]:
            """Execute the Sling replication and emit structured events.

            Args:
                context: Dagster execution context providing partition metadata.
                sling: Configured Sling resource capable of running the replication.

            Yields:
                dagster_sling.sling_event_iterator.SlingEventType: Structured logs and
                    progress events produced during the replication.
            """

            if "defaults" not in config:
                config["defaults"] = {}

            try:  # to inject start and end dates for partitioned runs
                time_window = context.partition_time_window
                if time_window:
                    if "source_options" not in config["defaults"]:
                        config["defaults"]["source_options"] = {}

                    format = "%Y-%m-%d %H:%M:%S"
                    start = time_window.start.strftime(format)
                    end = time_window.end.strftime(format)
                    config["defaults"]["source_options"]["range"] = f"{start},{end}"
            except Exception:  # run normal run if time window not provided
                pass

            yield from sling.replicate(
                context=context,
                replication_config=config,
                dagster_sling_translator=CustomDagsterSlingTranslator(),
            )
            for row in sling.stream_raw_logs():
                context.log.info(row)

        return assets

    @staticmethod
    def _set_schema(replication_config: dict) -> dict:
        """Override destination schemas with user-specific suffixes when configured.

        Args:
            replication_config: Raw replication dictionary that may specify destination
                objects and per-stream overrides.

        Returns:
            dict: Updated replication configuration incorporating the rendered schema
                suffix when the active environment requests user-level isolation.
        """

        if default_object := replication_config["defaults"]["object"]:
            schema, table = default_object.split(".")
            object = ".".join((get_schema_name(schema), table))
            replication_config["defaults"]["object"] = object

        for stream, stream_config in list(
            replication_config.get("streams", {}).items()
        ):
            stream_config = stream_config or {}
            if stream_object := stream_config.get("object"):
                schema, table = stream_object.split(".")
                object = ".".join((get_schema_name(schema), table))
                replication_config["streams"][stream]["object"] = object

        return replication_config

    @staticmethod
    def _get_sling_deps(
        replication_config: dict, kind: str | None
    ) -> list[dg.AssetSpec] | None:
        """Create external asset specs representing upstream Sling dependencies.

        Args:
            replication_config: Replication configuration describing dependent streams.
            kind: Resource kind associated with the upstream connection.

        Returns:
            list[dagster.AssetSpec] | None: Asset specs mirroring upstream data sources
                or ``None`` when no dependencies are declared.
        """
        kinds = {kind} if kind else None

        deps = []
        for k in replication_config["streams"]:
            schema, table = k.split(".")
            dep = dg.AssetSpec(
                key=[schema, "src", table], group_name=schema, kinds=kinds
            )
            deps.append(dep)
        return deps

    @staticmethod
    def _get_freshness_checks(
        replication_config: dict,
    ) -> list[dg.AssetChecksDefinition]:
        """Build freshness checks for each stream declared in a replication config.

        Args:
            replication_config: Replication configuration containing optional freshness
                metadata at both the default and stream level.

        Returns:
            list[dagster.AssetChecksDefinition]: Freshness checks constructed from the
                merged configuration, one per stream with configured thresholds.
        """
        freshness_checks = []

        default_freshness_check_config = (
            get_nested(
                replication_config, ["defaults", "meta", "dagster", "freshness_check"]
            )
            or {}
        )
        default_partition = get_nested(
            replication_config, ["defaults", "meta", "dagster", "partition"]
        )

        streams = replication_config.get("streams", {})
        for stream_name, steam_config in streams.items():
            freshness_check_config = (
                get_nested(steam_config, ["meta", "dagster", "freshness_check"]) or {}
            )
            partition = get_nested(steam_config, ["meta", "dagster", "partition"])

            freshness_check_config = (
                freshness_check_config | default_freshness_check_config
            )
            partition = partition or default_partition

            if freshness_check_config:
                if lower_bound_delta_seconds := freshness_check_config.pop(
                    "lower_bound_delta_seconds", None
                ):
                    lower_bound_delta = timedelta(
                        seconds=float(lower_bound_delta_seconds)
                    )
                    freshness_check_config["lower_bound_delta"] = lower_bound_delta

                schema, table_name = stream_name.split(".")
                asset_key = [schema, "raw", table_name]
                freshness_check_config["assets"] = [asset_key]

                try:
                    if partition in ["hourly", "daily", "weekly", "monthly"]:
                        freshness_check_config = sanitize_input_signature(
                            dg.build_time_partition_freshness_checks,
                            freshness_check_config,
                        )

                        time_partition_update_freshness_checks = (
                            dg.build_time_partition_freshness_checks(
                                **freshness_check_config
                            )
                        )
                        freshness_checks.extend(time_partition_update_freshness_checks)

                    else:
                        freshness_check_config = sanitize_input_signature(
                            dg.build_last_update_freshness_checks,
                            freshness_check_config,
                        )

                        last_update_freshness_checks = (
                            dg.build_last_update_freshness_checks(
                                **freshness_check_config
                            )
                        )
                        freshness_checks.extend(last_update_freshness_checks)
                except TypeError as e:
                    raise TypeError(
                        "Error creating freshness check, check your configuration for "
                        f"'{asset_key}'. Supplied arguments: {freshness_check_config}"
                    ) from e

        return freshness_checks
