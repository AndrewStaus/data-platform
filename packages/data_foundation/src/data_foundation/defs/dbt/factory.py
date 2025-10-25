"""Factory responsible for turning dbt projects into Dagster assets and sensors.

The helper exposes :class:`DagsterDbtFactory`, which coordinates how Dagster loads
dbt metadata, partitions models, and configures runtime options surfaced through the
Launchpad. Each documented function clarifies the expected parameters and emitted
values to make customizations easier.
"""

import json
import os
from collections.abc import Callable, Generator
from functools import cache
from typing import Any

import dagster as dg
from dagster_dbt import (
    DagsterDbtTranslatorSettings,
    DbtCliResource,
    DbtProject,
    build_freshness_checks_from_dbt_assets,
    dbt_assets,
)
from dagster_dbt.asset_utils import DBT_DEFAULT_SELECT
from dagster_dbt.core.dbt_event_iterator import DbtEventIterator

from .constants import TIME_PARTITION_SELECTOR
from .translator import CustomDagsterDbtTranslator

is_defer = os.getenv("TARGET", "").lower() == "dev"


class DbtConfig(dg.Config):
    """Runtime configuration options surfaced to the Dagster Launchpad UI.

    Attributes:
        full_refresh: When ``True`` the factory issues ``--full-refresh`` so dbt
            rebuilds models from scratch.
        defer_to_prod: Controls whether ``--defer`` arguments are passed to reference
            production artifacts during local runs.
        favor_state: Augments ``--defer`` by preferring stored state when resolving
            nodes, matching dbt Cloud's behavior.
    """

    full_refresh: bool = False
    defer_to_prod: bool = is_defer
    favor_state: bool = False


class Factory:
    """Factory to generate dagster definitions from a dbt project."""

    @cache
    @staticmethod
    def build_definitions(dbt: Callable[[], DbtProject]) -> dg.Definitions:
        """Create Dagster definitions backed by the supplied dbt project factory.

        Args:
            dbt: A zero-argument callable that yields a ready-to-use
                :class:`DbtProject` instance.

        Returns:
            dagster.Definitions: Definitions composed of dbt assets, freshness checks,
                and the dbt CLI resource configured with the project directory supplied
                by the callable.
        """

        dbt_project = dbt()
        assert dbt_project
        
        assets = [
            Factory._get_assets(
                "dbt_partitioned_models",
                dbt_project=dbt_project,
                select=TIME_PARTITION_SELECTOR,
                partitioned=True,
            ),
            Factory._get_assets(
                "dbt_non_partitioned_models",
                dbt_project=dbt_project,
                exclude=TIME_PARTITION_SELECTOR,
                partitioned=False,
            ),
        ]

        freshness_checks = build_freshness_checks_from_dbt_assets(dbt_assets=assets)
        freshness_sensor = dg.build_sensor_for_freshness_checks(
            freshness_checks=freshness_checks, name="dbt_freshness_checks_sensor"
        )

        return dg.Definitions(
            resources={"dbt": DbtCliResource(project_dir=dbt_project)},
            assets=assets,
            asset_checks=freshness_checks,
            sensors=[freshness_sensor],
        )

    @cache
    @staticmethod
    def _get_assets(
        name: str | None,
        dbt_project: DbtProject,
        partitioned: bool = False,
        select: str = DBT_DEFAULT_SELECT,
        exclude: str | None = None,
    ) -> dg.AssetsDefinition:
        """Build a ``dbt_assets`` definition for a subset of the dbt project.

        Args:
            name: The Dagster asset group name used to namespace materializations.
            dbt_project: Configured dbt project.
            partitioned: Indicates whether the assets rely on partition time windows.
            select: dbt selection string narrowing which models to materialize.
            exclude: Optional selection string for excluding models from the run.

        Returns:
            dagster.AssetsDefinition: A Dagster assets definition that streams dbt CLI
                events and respects the provided partitioning behavior.
        """        

        @dbt_assets(
            name=name,
            manifest=dbt_project.manifest_path,
            select=select,
            exclude=exclude,
            dagster_dbt_translator=CustomDagsterDbtTranslator(
                settings=DagsterDbtTranslatorSettings(
                    enable_duplicate_source_asset_keys=True,
                )
            ),
            backfill_policy=dg.BackfillPolicy.single_run(),
            project=dbt_project,
            pool="dbt",
        )
        def assets( # pragma: no coverage
            context: dg.AssetExecutionContext, dbt: DbtCliResource, config: DbtConfig
        ) -> Generator[DbtEventIterator, Any, Any]:
            """Materialize the selected dbt models via the dbt CLI resource.

            Args:
                context: Dagster execution context providing partition metadata and
                    structured logging APIs.
                dbt: The Dagster-provided dbt CLI resource bound to the selected
                    project directory.
                config: Runtime configuration emitted from :class:`DbtConfig` that
                    toggles dbt CLI flags.

            Yields:
                dagster_dbt.core.dbt_event_iterator.DbtEventIterator: The stream of
                    structured dbt events produced during the CLI invocation. Yielding
                    the iterator allows Dagster to surface granular run status in the
                    UI.
            """
            args = ["build"]

            if config.full_refresh:
                args.append("--full-refresh")
            if config.defer_to_prod:
                args.extend(dbt.get_defer_args())
                if config.favor_state:
                    args.append("--favor-state")

            if partitioned:
                # Partitioned assets inject the selected time window into dbt vars so
                # the models can filter appropriately.
                time_window = context.partition_time_window
                format = "%Y-%m-%d %H:%M:%S"
                dbt_vars = {
                    "min_date": time_window.start.strftime(format),
                    "max_date": time_window.end.strftime(format),
                }

                args.extend(("--vars", json.dumps(dbt_vars)))

                yield from dbt.cli(
                    args,
                    context=context
                ).stream()  # .with_insights() # type: ignore
            else:
                yield from dbt.cli(
                    args,
                    context=context
                ).stream()  # .with_insights() # type: ignore

        return assets
