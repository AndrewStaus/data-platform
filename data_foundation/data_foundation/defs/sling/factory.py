import os
from collections.abc import Generator
from datetime import timedelta
from functools import cache
from pathlib import Path
from typing import Any

import dagster as dg
import yaml
from dagster_sling import SlingConnectionResource, SlingResource, sling_assets
from dagster_sling.sling_event_iterator import SlingEventType

from ...utils.helpers import get_nested, sanitize_input_signature
from ...utils.secrets import get_secret
from .translator import CustomDagsterSlingTranslator


class DagsterSlingFactory:
    """Factory to generate dagster definitions from Sling yaml config files."""

    @cache
    @staticmethod
    def build_definitions(config_dir: Path) -> dg.Definitions:
        """Returns a Definitions object for a path that contains Sling yaml configs."""
        connections = []
        assets = []
        freshness_checks = []
        kind_map = {}

        for config_path in os.listdir(config_dir):
            if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                config_path = config_dir.joinpath(config_path).resolve()
                with open(config_path) as file:
                    config = yaml.load(file, Loader=yaml.FullLoader)
                if not config:
                    continue

                if connection_configs := config.get("connections"):
                    connections, kind_map = DagsterSlingFactory._get_connections(
                        connection_configs, connections, kind_map
                    )

                if replication_configs := config.get("replications"):
                    assets, freshness_checks = DagsterSlingFactory._get_replications(
                        replication_configs, freshness_checks, kind_map, assets
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
    def _get_connections(
        connection_configs, connections, kind_map
    ) -> tuple[list[SlingConnectionResource], dict[str, str]]:
        """Returns a list of SlingConnectionResource for connections in the Sling
        yaml file.
        """
        for connection_config in connection_configs:
            if connection := DagsterSlingFactory._get_connection(connection_config):
                source = connection_config.get("name")
                kind = connection_config.get("type")
                kind_map[source] = kind
                connections.append(connection)

        return connections, kind_map

    @staticmethod
    def _get_connection(connection_config: dict) -> SlingConnectionResource | None:
        """Returns a SlingConnectionResource for a connection in the Sling yaml file."""
        for k, v in connection_config.items():
            if isinstance(v, dict):
                secret_name = list(v.keys())[0]
                display_type = list(v.values())[0]

                if display_type == "show":
                    connection_config[k] = get_secret(secret_name).get_value()
                else:
                    connection_config[k] = get_secret(secret_name)

        connection = SlingConnectionResource(**connection_config)
        return connection

    @staticmethod
    def _get_replications(
        replication_configs, freshness_checks, kind_map, assets
    ) -> tuple[list[dg.AssetsDefinition], list[dg.AssetChecksDefinition]]:
        """Returns a list of AssetsDefinitions for
        replications in a Sling yaml file
        """
        for replication_config in replication_configs:
            if bool(os.getenv("DAGSTER_IS_DEV_CLI")):
                replication_config = DagsterSlingFactory._set_dev_schema(
                    replication_config
                )
            assets_definition = DagsterSlingFactory._get_replication(replication_config)

            kind = kind_map.get(replication_config.get("source", None), None)
            dep_asset_specs = DagsterSlingFactory._get_sling_deps(
                replication_config, kind
            )
            asset_freshness_checks = DagsterSlingFactory._get_freshness_checks(
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
    def _get_replication(config: dict) -> dg.AssetsDefinition:
        """Returns a AssetsDefinition for replication
        in a Sling yaml file
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
        ) -> Generator[SlingEventType, Any, None]:
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
    def _set_dev_schema(replication_config: dict) -> dict:
        """Override the desination schema set in the yaml file when the environment
        is set to dev to point to a unique schema based on the developer.
        """
        user = os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME"].upper()
        if default_object := replication_config["defaults"]["object"]:
            schema, table = default_object.split(".")
            replication_config["defaults"]["object"] = f"{schema}__{user}.{table}"

        for stream, stream_config in list(
            replication_config.get("streams", {}).items()
        ):
            stream_config = stream_config or {}
            if stream_object := stream_config.get("object"):
                schema, table = stream_object.split(".")
                replication_config["streams"][stream]["object"] = (
                    f"{schema}__{user}.{table}"
                )

        return replication_config

    @staticmethod
    def _get_sling_deps(
        replication_config: dict, kind: str | None
    ) -> list[dg.AssetSpec] | None:
        """Create an external asset that is placed in the same prefix
        as the asset, and assigned the correct resource kind.
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
        """Returns a list of AssetChecksDefinition for replication configs.
        Configs supplied on the stream will take priority, otherwise the
        default will be used.
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
