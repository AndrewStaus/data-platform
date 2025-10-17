"""Factory helpers that translate dlt resources into Dagster definitions."""

import os
from collections.abc import Generator, Sequence
from datetime import timedelta
from functools import cache
from typing import Any

import dagster as dg
import dlt
from dagster_dlt import DagsterDltResource, dlt_assets
from dagster_dlt.dlt_event_iterator import DltEventType
from data_platform_utils.helpers import get_nested
from dlt.extract.resource import DltResource

from .translator import CustomDagsterDltTranslator


class ConfigurableDltResource(DltResource):
    """Extend :class:`dlt.extract.resource.DltResource` with Dagster-specific metadata.

    The wrapper exposes hooks for automation conditions, tags, and kinds that the
    Dagster factory consumes when creating asset definitions.
    """

    meta: dict | None
    tags: list | None
    kinds: set | None

    @staticmethod
    def config(
        resource: DltResource,
        meta: dict | None = None,
        tags: list[str] | None = None,
        kinds: set[str] | None = None,
    ) -> "ConfigurableDltResource":
        """Attach Dagster metadata to a dlt resource.

        Args:
            resource: The dlt resource to wrap.
            meta: Optional metadata dictionary forwarded to Dagster asset definitions.
            tags: Dagster tag values applied to downstream assets.
            kinds: Dagster ``kind`` labels used for categorizing assets.

        Returns:
            ConfigurableDltResource: The wrapped resource enriched with the provided
                metadata.
        """
        resource = ConfigurableDltResource._convert(resource, meta, tags, kinds)
        return resource  # type: ignore

    @staticmethod
    def _convert(
        dlt_resource: DltResource,
        meta: dict | None,
        tags: list[str] | None,
        kinds: set[str] | None,
    ) -> "ConfigurableDltResource":
        """Apply metadata attributes to the underlying dlt resource."""
        dlt_resource.tags = tags  # type: ignore
        dlt_resource.meta = meta  # type: ignore
        dlt_resource.kinds = kinds  # type: ignore
        return dlt_resource  # type: ignore


class DagsterDltFactory:
    """Utility class for building Dagster ``Definitions`` from dlt resources."""
    @cache
    @staticmethod
    def build_definitions(resources: list[ConfigurableDltResource]) -> dg.Definitions:
        """Create Dagster definitions for the provided dlt resources.

        Args:
            resources: Collection of :class:`ConfigurableDltResource` instances that
                describe how to materialize data via dlt.

        Returns:
            dagster.Definitions: Definitions containing Dagster assets representing the
                supplied resources plus any derived asset checks.
        """
        assets_definitions = []
        freshness_checks = []
        for resource in resources:
            assets = DagsterDltFactory._build_assets(resource)
            assets_definitions.extend(assets)

            if last_update_freshness_check := (
                DagsterDltFactory._build_freshness_checks(resource)
            ):
                freshness_checks.extend(last_update_freshness_check)

        return dg.Definitions(assets=assets_definitions, asset_checks=freshness_checks)

    @staticmethod
    def _build_assets(
        resource: ConfigurableDltResource,
    ) -> list[dg.AssetsDefinition | dg.AssetSpec]:
        """Build the Dagster asset definition and matching dependency spec.

        Args:
            resource: The configured dlt resource to expose via Dagster assets.

        Returns:
            list[dg.AssetsDefinition | dg.AssetSpec]: The Dagster asset definition that
                executes the dlt pipeline alongside the dependency ``AssetSpec``
                describing upstream source data.
        """
        schema, table = resource.name.split(".")
        dataset_name = schema
        if os.getenv("TARGET") == "dev":
            dataset_name = (
                schema + "__" + os.getenv("DESTINATION__USER", "DEFAULT").upper()
            )

        @dlt.source()
        def source() -> Generator[DltResource, Any]:
            yield resource

        @dlt_assets(
            name=f"{schema}__{table}",
            op_tags={"tags": resource.tags},
            dlt_source=source(),
            backfill_policy=dg.BackfillPolicy.single_run(),
            dagster_dlt_translator=CustomDagsterDltTranslator(),
            pool="dlthub",
            dlt_pipeline=dlt.pipeline(
                pipeline_name=f"{schema}__{table}",
                destination="snowflake",
                dataset_name=dataset_name,
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

        dep = dg.AssetSpec(
            [schema, "src", table], kinds=resource.kinds, group_name=schema
        )

        return [assets, dep]

    @staticmethod
    def _build_freshness_checks(
        resource: ConfigurableDltResource,
    ) -> Sequence[dg.AssetChecksDefinition] | None:
        """Create freshness checks based on metadata embedded within the resource.

        Args:
            resource: Configured dlt resource whose metadata may include freshness
                expectations.

        Returns:
            Sequence[dagster.AssetChecksDefinition] | None: Freshness checks when the
                metadata includes ``freshness_lower_bound_delta_seconds``; otherwise
                ``None`` to skip check generation.
        """
        schema, table = resource.name.split(".")

        meta = resource.meta or {}
        if delta := get_nested(
            meta, ["dagster", "freshness_lower_bound_delta_seconds"]
        ):
            asset_key = dg.AssetKey([schema, "raw", table])
            last_update_freshness_check = dg.build_last_update_freshness_checks(
                assets=[asset_key],
                lower_bound_delta=timedelta(seconds=float(delta)),
            )
            return last_update_freshness_check
