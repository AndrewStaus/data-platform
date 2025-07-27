from typing import Iterable, Mapping, Any

from dagster._utils.tags import is_valid_tag_key
from dlt.extract.resource import DltResource
from dagster_dlt.translator import DltResourceTranslatorData
from dagster_dlt import DagsterDltTranslator
import dagster as dg

from ..helpers import (
    get_automation_condition_from_meta,
    get_partitions_def_from_meta
)



class CustomDagsterDltTranslator(DagsterDltTranslator):

    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        """Defines the asset spec for a given dlt resource.

        This method can be overridden to provide custom asset key for a dlt resource.

        Args:
            data (DltResourceTranslatorData): The dlt data to pass to the translator,
                including the resource and the destination.

        Returns:
            The :py:class:`dagster.AssetSpec` for the given dlt resource

        """
        return dg.AssetSpec(
            key=self._resolve_back_compat_method(
                "get_asset_key", self._default_asset_key_fn, data.resource
            ),
            automation_condition=self._resolve_back_compat_method(
                "get_automation_condition", self._default_automation_condition_fn, data.resource
            ),
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
            tags=self._resolve_back_compat_method("get_tags", self._default_tags_fn, data.resource),
            kinds=self._resolve_back_compat_method(
                "get_kinds", self._default_kinds_fn, data.resource, data.destination
            ),
            partitions_def=self.get_partitions_def(data.resource)
        )



    def get_deps_asset_keys(self, resource: DltResource) -> Iterable[dg.AssetKey]:
        name : str | None = None
        if resource.is_transformer:
            pipe = resource._pipe
            while pipe.has_parent:
                pipe = pipe.parent
                name = pipe.schema.name # type: ignore
        else:
            name = resource.name
        if name:
            schema, table = name.split(".")
            asset_key = [schema, "src", table]
            return [dg.AssetKey(asset_key)]
        return super().get_deps_asset_keys(resource)

    def get_asset_key(self, resource: DltResource) -> dg.AssetKey:
        schema, table = resource.name.split(".")
        asset_key = [schema, "raw", table]
        return dg.AssetKey(asset_key)
    
    def get_group_name(self, resource: DltResource) -> str:
        group = resource.name.split(".")[0]
        return group

    # not implemented in base class
    def get_partitions_def(self, resource: DltResource) -> dg.PartitionsDefinition | None:
        try:
            meta = resource.meta.get("dagster") # type: ignore
            return get_partitions_def_from_meta(meta)
        except Exception: ...
        return None

    def get_automation_condition(self, resource: DltResource):
        try:
            meta = resource.meta.get("dagster") # type: ignore
            automation_condition = get_automation_condition_from_meta(meta)
            if automation_condition:
                return automation_condition
        except Exception: ...
        return super().get_automation_condition(resource)


    def get_tags(self, resource: DltResource) -> Mapping[str, Any]:
        try:
            tags = resource.tags # type: ignore
            return {tag: "" for tag in tags if is_valid_tag_key(tag)}
        except Exception: ...
        return {}
