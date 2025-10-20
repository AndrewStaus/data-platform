"""Custom translator hooks that convert Sling configs into Dagster metadata.

The translator inspects Sling replication definitions and maps configuration metadata
to Dagster constructs such as asset keys, groups, and automation conditions.
"""

from collections.abc import Iterable, Mapping
from typing import Any, override

import dagster as dg
import dagster_sling as dg_sling
from dagster._utils.tags import is_valid_tag_key
from data_platform_utils.helpers import (
    get_automation_condition_from_meta,
    get_nested,
    get_partitions_def_from_meta,
)


class CustomDagsterSlingTranslator(dg_sling.DagsterSlingTranslator):
    """Translate Sling replication definitions into Dagster asset metadata."""

    @override
    def get_asset_spec(self, stream_definition: Mapping[str, Any]) -> dg.AssetSpec:
        """Build an :class:`~dagster.AssetSpec` using Sling replication metadata.

        Args:
            stream_definition: Dictionary describing a Sling replication stream.

        Returns:
            dagster.AssetSpec: Asset specification enriched with automation conditions,
                partitions, tags, and group information derived from the stream
                metadata.
        """
        return dg.AssetSpec(
            automation_condition=self.get_automation_condition(stream_definition),
            partitions_def=self.get_partitions_def(stream_definition),
            key=self._resolve_back_compat_method(
                "get_asset_key", self._default_asset_key_fn, stream_definition
            ),
            deps=self._resolve_back_compat_method(
                "get_deps_asset_key", self._default_deps_fn, stream_definition
            ),
            description=self._resolve_back_compat_method(
                "get_description", self._default_description_fn, stream_definition
            ),
            metadata=self._resolve_back_compat_method(
                "get_metadata", self._default_metadata_fn, stream_definition
            ),
            tags=self._resolve_back_compat_method(
                "get_tags", self._default_tags_fn, stream_definition
            ),
            kinds=self._resolve_back_compat_method(
                "get_kinds", self._default_kinds_fn, stream_definition
            ),
            group_name=self._resolve_back_compat_method(
                "get_group_name", self._default_group_name_fn, stream_definition
            ),
            legacy_freshness_policy=self._resolve_back_compat_method(
                "get_freshness_policy",
                self._default_freshness_policy_fn,
                stream_definition,
            ),
            auto_materialize_policy=self._resolve_back_compat_method(
                "get_auto_materialize_policy",
                self._default_auto_materialize_policy_fn,
                stream_definition,
            ),
        )

    @override
    def get_asset_key(self, stream_definition: Mapping[str, Any]) -> dg.AssetKey:
        """Derive the Dagster asset key for a Sling replication stream.

        Args:
            stream_definition: Sling stream dictionary potentially containing an
                explicit asset key override.

        Returns:
            dagster.AssetKey: Asset key determined either from explicit metadata or the
                sanitized stream name.
        """
        asset_key = get_nested(stream_definition,
                               ["config", "meta", "dagster", "asset_key"])

        if asset_key:
            if self.sanitize_stream_name(asset_key) != asset_key:
                raise ValueError(
                    f"Asset key {asset_key} for stream {stream_definition['name']} "
                    "is not sanitized. Please use only alphanumeric characters "
                    "and underscores."
                )
            return dg.AssetKey(asset_key.split("."))

        # You can override the Sling Replication default object with an object key
        stream_name = stream_definition["name"]
        schema, table = self.sanitize_stream_name(stream_name).split(".")
        return dg.AssetKey([schema, "raw", table])

    @override
    def get_deps_asset_key(
        self, stream_definition: Mapping[str, Any]
    ) -> Iterable[dg.AssetKey]:
        """Return upstream dependencies declared in the Sling configuration.

        Args:
            stream_definition: Sling stream configuration that may reference upstream
                asset keys under ``meta.dagster.deps``.

        Returns:
            Iterable[dagster.AssetKey]: Asset keys representing upstream sources.
        """

        deps = get_nested(stream_definition, ["config", "meta", "dagster", "deps"])
        deps_out = []
        if deps and isinstance(deps, str):
            deps = [deps]
        if deps:
            assert isinstance(deps, list)
            for asset_key in deps:
                if self.sanitize_stream_name(asset_key) != asset_key:
                    raise ValueError(
                        f"Deps Asset key {asset_key} for stream  "
                        f"{stream_definition['name']} is not sanitized. "
                        "Please use only alphanumeric characters and underscores."
                    )
                deps_out.append(dg.AssetKey(asset_key.split(".")))
            return deps_out

        stream_name = stream_definition["name"]
        schema, table = self.sanitize_stream_name(stream_name).split(".")
        return [dg.AssetKey([schema, "src", table])]

    @override
    def get_group_name(self, stream_definition: Mapping[str, Any]) -> str:
        """Resolve the asset group name from the stream metadata or schema.

        Args:
            stream_definition: Sling stream dictionary used to derive a group name.

        Returns:
            str: Group name supplied in metadata or the schema extracted from the stream
                name when no override exists.
        """
        group = get_nested(stream_definition, ["config", "meta", "dagster", "group"])
        if group:
            return group
        
        stream_name = stream_definition["name"]
        schema, _ = self.sanitize_stream_name(stream_name).split(".")
        return schema

    @override
    def get_tags(self, stream_definition: Mapping[str, Any]) -> Mapping[str, Any]:
        """Convert Sling "tags" metadata into Dagster tag key/value pairs.

        Args:
            stream_definition: Sling stream dictionary that may define a ``tags`` list.

        Returns:
            Mapping[str, Any]: Dictionary of sanitized tags safe for Dagster asset
                metadata.
        """

        tags = get_nested(stream_definition, ["config", "meta", "dagster", "tags"])
        if tags:
            return {tag: "" for tag in tags if is_valid_tag_key(tag)}
        return {}

    def get_automation_condition(
        self, stream_definition: Mapping[str, Any]
    ) -> None | dg.AutomationCondition:
        """Interpret the automation condition configuration for a stream, if present.

        Args:
            stream_definition: Stream configuration containing optional automation
                directives under ``meta.dagster``.

        Returns:
            dagster.AutomationCondition | None: Automation condition built from the
                metadata or ``None`` when unspecified.
        """

        if meta := get_nested(stream_definition, ["config", "meta", "dagster"]):
            automation_condition = get_automation_condition_from_meta(meta)
            return automation_condition

    def get_partitions_def(
        self, stream_definition: Mapping[str, Any]
    ) -> None | dg.PartitionsDefinition:
        """Interpret partition configuration and translate it into Dagster definitions.

        Args:
            stream_definition: Sling stream dictionary with optional partition metadata.

        Returns:
            dagster.PartitionsDefinition | None: Partition definition derived from
                metadata or ``None`` if the stream is un-partitioned.
        """
        if meta := get_nested(stream_definition, ["config", "meta", "dagster"]):
            partitions_def = get_partitions_def_from_meta(meta)
            return partitions_def
