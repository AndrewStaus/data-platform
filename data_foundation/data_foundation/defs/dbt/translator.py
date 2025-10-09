import re
from collections.abc import Mapping
from typing import Any, override

import dagster as dg
from dagster_dbt import DagsterDbtTranslator

from ...utils.automation_conditions import CustomAutomationCondition
from ...utils.helpers import (
    get_automation_condition_from_meta,
    get_nested,
    get_partitions_def_from_meta,
)


class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    """Overrides methods of the standard translator.

    Holds a set of methods that derive Dagster asset definition metadata given
    a representation of a dbt resource (models, tests, sources, etc).
    Methods are overriden to customize the implementation.

    See parent class for details on the purpose of each override"""

    @override
    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> dg.AssetKey:
        meta = dbt_resource_props.get("config", {}).get(
            "meta", {}
        ) or dbt_resource_props.get("meta", {})
        meta_dagster = meta.get("dagster") or {}
        asset_key_config = meta_dagster.get("asset_key")
        if asset_key_config:
            return dg.AssetKey(asset_key_config)

        prop_key = "name"
        if dbt_resource_props.get("version"):
            prop_key = "alias"

        if dbt_resource_props["resource_type"] == "source":
            schema = dbt_resource_props["source_name"]
            table = dbt_resource_props["name"]
            step = "raw"
            return dg.AssetKey([schema, step, table])

        parsed_name = re.search("(.*?)_(.*)__(.*)", dbt_resource_props[prop_key])
        if parsed_name:
            schema = parsed_name.group(2)
            table = parsed_name.group(3)
            step = parsed_name.group(1)
            return dg.AssetKey([schema, step, table])

        return super().get_asset_key(dbt_resource_props)

    @override
    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> str | None:
        prop_key = "name"
        if dbt_resource_props.get("version"):
            prop_key = "alias"
        parsed_name = re.search("(.*?)_(.*)__(.*)", dbt_resource_props[prop_key])
        if parsed_name:
            schema = parsed_name.group(2)
            return schema

        return super().get_group_name(dbt_resource_props)

    @override
    def get_partitions_def(
        self, dbt_resource_props: Mapping[str, Any]
    ) -> dg.PartitionsDefinition | None:
        if meta := get_nested(dbt_resource_props, ["config", "meta", "dagster"]):
            return get_partitions_def_from_meta(meta)

    @override
    def get_automation_condition(
        self, dbt_resource_props: Mapping[str, Any]
    ) -> dg.AutomationCondition | None:
        if meta := get_nested(dbt_resource_props, ["config", "meta", "dagster"]):
            automation_condition = get_automation_condition_from_meta(meta)
            if automation_condition:
                return automation_condition

        # default settings for resource types
        resource_type = dbt_resource_props.get("resource_type")
        if resource_type == "snapshot":
            return CustomAutomationCondition.eager_with_deps_checks()

        if resource_type == "seed":
            return CustomAutomationCondition.code_version_changed()

        else:
            return CustomAutomationCondition.lazy()

    @override
    def get_tags(self, dbt_resource_props: Mapping[str, Any]) -> Mapping[str, str]:
        tags = super().get_tags(dbt_resource_props)
        return tags
