"""Custom translator for enriching dltHub resources with Dagster metadata.

The translator inspects dlt resource metadata and maps it onto Dagster asset
constructs. This enables features such as automation conditions, partitions, and
validated tags to flow from dlt configuration into Dagster without manual wiring.
"""

from collections.abc import Iterable, Mapping
from typing import Any, override

import dagster as dg
from dagster_dlt import DagsterDltTranslator
from dagster_dlt.translator import DltResourceTranslatorData
from dlt.extract.resource import DltResource


class CustomDagsterDltTranslator(DagsterDltTranslator):
    """Translate dlt resource metadata into Dagster asset definitions."""

    def __init__(self,
                 automation_condition: dg.AutomationCondition[Any]|None=None,
                 tags: Mapping[str, Any]|None = None,
                 partitions_def: dg.PartitionsDefinition[str]|None = None) -> None:

        super().__init__() 
        self.automation_condition = automation_condition
        self.tags = tags
        self.partitions_def = partitions_def

    @override
    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        """Create an :class:`~dagster.AssetSpec` that reflects dlt resource metadata.

        Args:
            data: Translator payload that bundles the dlt resource and destination
                configuration used to inform Dagster metadata.

        Returns:
            dagster.AssetSpec: Asset specification populated with automation conditions,
                dependencies, tags, and partitioning inferred from the dlt resource.
        """
        return dg.AssetSpec(
            key=self._resolve_back_compat_method(
                "get_asset_key", self._default_asset_key_fn, data.resource
            ),
            automation_condition=self.get_automation_condition(data.resource),
            deps=self._resolve_back_compat_method(
                "get_deps_asset_keys", self._default_deps_fn, data.resource
            ),
            description=self._resolve_back_compat_method(
                "get_description", self._default_description_fn, data.resource
            ),
            group_name=self._resolve_back_compat_method(
                "get_group_name", self._default_group_name_fn, data.resource
            ),
            metadata=self._resolve_back_compat_method(
                "get_metadata", self._default_metadata_fn, data.resource
            ),
            owners=self._resolve_back_compat_method(
                "get_owners", self._default_owners_fn, data.resource
            ),
            tags=self._resolve_back_compat_method(
                "get_tags", self._default_tags_fn, data.resource
            ),
            kinds=self._resolve_back_compat_method(
                "get_kinds", self._default_kinds_fn, data.resource, data.destination
            ),
            partitions_def=self.get_partitions_def(data.resource),
        )

    @override
    def get_deps_asset_keys(self, resource: DltResource) -> Iterable[dg.AssetKey]:
        """Return external assets that represent upstream data sources.

        Args:
            resource: dlt resource whose upstream lineage should be mapped to Dagster
                asset keys.

        Returns:
            Iterable[dagster.AssetKey]: External asset keys representing the raw source
                tables feeding the resource.
        """
        name: str | None = None
        if resource.is_transformer:
            pipe = resource._pipe
            while pipe.has_parent:
                pipe = pipe.parent
                name = pipe.name
            if name:
                schema, table = name.split(".")
                asset_key = [schema, "raw", table]
                return [dg.AssetKey(asset_key)]
        else:
            name = resource.name
        if name:
            name_parts = name.split(".")
            if len(name_parts) == 2:
                schema, table = name_parts
                asset_key = [schema, "src", table]
                return [dg.AssetKey(asset_key)]
        return super().get_deps_asset_keys(resource)

    @override
    def get_asset_key(self, resource: DltResource) -> dg.AssetKey:
        """Generate the Dagster asset key for a dlt resource.

        Args:
            resource: dlt resource whose name encodes schema and table information.

        Returns:
            dagster.AssetKey: Asset key structured as ``[schema, "raw", table]``.
        """
        name_parts = resource.name.split(".")
        if len(name_parts) == 2:
            schema, table = resource.name.split(".")
            asset_key = [schema, "raw", table]
            return dg.AssetKey(asset_key)
        return super().get_asset_key(resource)

    @override
    def get_group_name(self, resource: DltResource) -> str:
        """Group dlt assets by the schema portion of the resource name.

        Args:
            resource: dlt resource used to determine the Dagster asset group.

        Returns:
            str: The schema prefix extracted from the resource name.
        """
        group = resource.name.split(".")[0]
        return group

    def get_partitions_def(
        self, resource: DltResource
    ) -> dg.PartitionsDefinition | None:
        """Return a partitions definition if one exists.  dlt does not support
        adding metadata, so this can not be parsed from the resouce itself, and must
        be defined when the translator is instantiated.

        Args:
            resource: dlt resource whose ``meta`` field may specify partition
                expectations.

        Returns:
            dagster.PartitionsDefinition | None: Partitions definition derived from
                metadata or ``None`` when no partitioning is configured.
        """
        if self.tags:
            return self.partitions_def

    @override
    def get_automation_condition(
                self, resource: DltResource) -> dg.AutomationCondition[Any] | None:
        """Return an automation condition definition if one exists.  dlt does not
        support adding metadata, so this can not be parsed from the resouce itself, and
        must be defined when the translator is instantiated.

        Args:
            resource: dlt resource whose ``meta`` configuration may describe automation
                triggers.

        Returns:
            dagster.AutomationCondition | None: Automation condition to apply to the
                Dagster asset or ``None`` when the default should be used.
        """
        if self.automation_condition:
            return self.automation_condition
        return super().get_automation_condition(resource)

    @override
    def get_tags(self, resource: DltResource) -> Mapping[str, Any]:
        """Return tags if they exists.  dlt does not support adding metadata, so this
        can not be parsed from the resouce itself, and must be defined when the
        translator is instantiated.

        Args:
            resource: dlt resource potentially containing tag metadata.

        Returns:
            Mapping[str, Any]: Dictionary of Dagster-compliant tags derived from the dlt
                resource metadata.
        """
        if self.tags:
            return self.tags
        return super().get_tags(resource)
