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

defer_to_prod = os.getenv("TARGET", "").lower() != "prod"


class DbtConfig(dg.Config):
    """Exposes configuration options to end users in the Dagster
    launchpad.
    """

    full_refresh: bool = False
    defer_to_prod: bool = defer_to_prod
    favor_state: bool = False


class DagsterDbtFactory:
    """Factory to generate dagster definitions from a dbt project."""

    @cache
    @staticmethod
    def build_definitions(dbt: Callable[[], DbtProject]) -> dg.Definitions:
        """Returns a Definitions object from a dbt project."""
        
        assets = [
            DagsterDbtFactory._get_assets(
                "dbt_partitioned_models",
                dbt=dbt,
                select=TIME_PARTITION_SELECTOR,
                partitioned=True,
            ),
            DagsterDbtFactory._get_assets(
                "dbt_non_partitioned_models",
                dbt=dbt,
                exclude=TIME_PARTITION_SELECTOR,
                partitioned=False,
            ),
        ]

        freshness_checks = build_freshness_checks_from_dbt_assets(dbt_assets=assets)
        freshness_sensor = dg.build_sensor_for_freshness_checks(
            freshness_checks=freshness_checks, name="dbt_freshness_checks_sensor"
        )

        return dg.Definitions(
            resources={"dbt": DbtCliResource(project_dir=dbt())},
            assets=assets,
            asset_checks=freshness_checks,
            sensors=[freshness_sensor],
        )

    @cache
    @staticmethod
    def _get_assets(
        name: str | None,
        dbt: Callable[[], DbtProject],
        partitioned: bool = False,
        select: str = DBT_DEFAULT_SELECT,
        exclude: str | None = None,
    ) -> dg.AssetsDefinition:
        """Returns a AssetsDefinition with different execution for partitioned
        and non-partitioned models so that they can be ran on the same job.
        """
        dbt_project = dbt()
        assert dbt_project

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
        def assets(
            context: dg.AssetExecutionContext, dbt: DbtCliResource, config: DbtConfig
        ) -> Generator[DbtEventIterator, Any, Any]:
            args = ["build"]

            if config.full_refresh:
                args.append("--full-refresh")
            if config.defer_to_prod:
                args.extend(dbt.get_defer_args())
                if config.favor_state:
                    args.append("--favor-state")

            if partitioned:
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
