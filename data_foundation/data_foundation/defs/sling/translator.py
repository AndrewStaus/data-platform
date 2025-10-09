from collections.abc import Iterable, Mapping
from typing import Any, override

import dagster as dg
import dagster_sling as dg_sling
from dagster._utils.tags import is_valid_tag_key

from ...utils.helpers import (
    get_automation_condition_from_meta,
    get_partitions_def_from_meta,
)


class CustomDagsterSlingTranslator(dg_sling.DagsterSlingTranslator):
    """Overrides methods of the standard translator.

    Holds a set of methods that derive Dagster asset definition metadata given a
    representation of Sling resource (connections, replications). Methods are overriden
    to customize the implementation.

    See parent class for details on the purpose of each override"""

    @override
    def get_asset_spec(self, stream_definition: Mapping[str, Any]) -> dg.AssetSpec:
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
        config = stream_definition.get("config") or {}
        meta = config.get("meta") or {}
        dagster = meta.get("dagster") or {}
        asset_key = dagster.get("asset_key", None)

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
        config = stream_definition.get("config", {}) or {}
        meta = config.get("meta", {}) or {}
        deps = meta.get("dagster", {}).get("deps")
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
        try:
            group = stream_definition["config"]["meta"]["dagster"]["group"]
            if group:
                return group
        except Exception:
            ...

        stream_name = stream_definition["name"]
        schema, _ = self.sanitize_stream_name(stream_name).split(".")
        return schema

    @override
    def get_tags(self, stream_definition: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            tags = stream_definition["config"]["meta"]["dagster"]["tags"]
            return {tag: "" for tag in tags if is_valid_tag_key(tag)}
        except Exception:
            ...
        return {}

    def get_automation_condition(
        self, stream_definition: Mapping[str, Any]
    ) -> None | dg.AutomationCondition:
        try:
            meta = stream_definition["config"]["meta"]["dagster"]
            automation_condition = get_automation_condition_from_meta(meta)
            return automation_condition
        except Exception:
            ...
        return None

    def get_partitions_def(
        self, stream_definition: Mapping[str, Any]
    ) -> None | dg.PartitionsDefinition:
        try:
            meta = stream_definition["config"]["meta"]["dagster"]
            automation_condition = get_partitions_def_from_meta(meta)
            return automation_condition
        except Exception:
            ...
        return None
