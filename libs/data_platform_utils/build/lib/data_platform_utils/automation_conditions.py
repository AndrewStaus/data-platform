# from typing import override

from dagster import AssetSelection, AutomationCondition
from dagster._core.definitions.declarative_automation.operators import (
    AndAutomationCondition,
)


class CustomAutomationCondition(AutomationCondition):
    @classmethod
    def get_automation_condition(
        cls, automation_condition_name: str
    ) -> AutomationCondition | None:
        methods = AutomationCondition.__dict__ | cls.__dict__
        return methods.get(automation_condition_name, None)

    @staticmethod
    def manual() -> None:
        """Returns no AutomationCondition that will require a user to manually trigger.
        Used for overriding default automations for static assets.
        """
        return None

    @staticmethod
    def missing_or_changed() -> AutomationCondition:
        """Returns no AutomationCondition that will trigger only if the asset has never
        been materialized, or if its definition has changed.

        Common use for dbt seeds that only need to be reloaded when the underlying csv
        file changes.
        """
        return (
            AutomationCondition.in_latest_time_window()
            & (
                AutomationCondition.code_version_changed()
                | AutomationCondition.newly_missing()
            ).since_last_handled()
            & ~AutomationCondition.in_progress()
        ).with_label("missing_or_changed")

    # @override
    @staticmethod
    def eager() -> AndAutomationCondition:
        """Returns an AutomationCondition which will cause a target to be executed if
        any of its dependencies update, and will execute missing partitions if they
        become missing after this condition is applied to the target. This will not
        execute targets that have any missing or in progress dependencies, or are
        currently in progress.

        For time partitioned assets, only the latest time partition will be considered.
        Commonly used for assets that are far downstream and have users that directly
        interact with them, and do not have sensitivity to late arriving dimensions.
        """
        return (
            AutomationCondition.in_latest_time_window()
            & (
                AutomationCondition.newly_missing()
                | AutomationCondition.any_deps_updated()
            ).since_last_handled()
            & ~AutomationCondition.any_deps_missing()
            & ~AutomationCondition.any_deps_in_progress()
            & ~AutomationCondition.in_progress()
        ).with_label("eager")

    @staticmethod
    def eager_with_deps_checks() -> AutomationCondition:
        """Returns an AutomationCondition which will cause a target
        to be executed if any of its dependencies update but only after,
        the dependencies blocking checks have passed, and will
        execute missing partitions if they become missing after this
        condition is applied to the target. This will not execute targets
        that have any missing or in progress dependencies,
        or are currently in progress.

        For time partitioned assets, only the latest time partition will be considered.
        Commonly used for assets that are far downstream and have users that directly
        interact with them, and do not have sensitivity to late arriving dimensions.
        """
        return (
            AutomationCondition.eager()
            & AutomationCondition.all_deps_blocking_checks_passed()
        )

    @classmethod
    def lazy(cls) -> AutomationCondition:
        """Returns an AutomationCondition which will cause a target to be executed if
        any downstream conditions are true or the partition is missing or changed.

        Commonly used for intermediate assets that are used for downstream
        materializations.
        """
        return (
            AutomationCondition.any_downstream_conditions() | cls.missing_or_changed()
        ).with_label("lazy")

    @staticmethod
    def lazy_on_cron(
        cron_schedule: str,
        cron_timezone: str = "UTC",
        ignore_asset_keys: list[list[str]] | None = None,
    ) -> AutomationCondition:
        """Returns an AutomationCondition which will cause a target to be
        executed if any downstream conditions are true or the partition is missing or
        changed. Will limit to only one execution for the given cron_schedule.

        Commonly used for intermediate assets that are used for downstream
        materializations, that have high frequency upstream assets, but themselves do
        not need to be updated as frequently.
        """
        ignore_asset_keys = ignore_asset_keys or []
        return (
            AutomationCondition.in_latest_time_window()
            & AutomationCondition.cron_tick_passed(
                cron_schedule, cron_timezone
            ).since_last_handled()
            & AutomationCondition.all_deps_updated_since_cron(
                cron_schedule, cron_timezone
            ).ignore(AssetSelection.assets(*ignore_asset_keys))
            & ~AutomationCondition.in_progress()
        ).with_label(f"lazy_on_cron({cron_schedule}, {cron_timezone})")

    @staticmethod
    # @override
    def on_cron(
        cron_schedule: str,
        cron_timezone: str = "UTC",
        ignore_asset_keys: list[list[str]] | None = None,
    ) -> AndAutomationCondition:
        """Returns an AutomationCondition which will cause a target to be executed on a
        given cron schedule, after all of its dependencies have been updated since the
        latest tick of that cron schedule.

        For time partitioned assets, only the latest time partition will be considered.

        Commonly used for assets that are far downstream and have users that directly
        interact with them, and have sensitivity to late arriving dimensions.
        """
        ignore_asset_keys = ignore_asset_keys or []
        return AutomationCondition.on_cron(cron_schedule, cron_timezone).ignore(
            AssetSelection.assets(*ignore_asset_keys)
        )

    @staticmethod
    def on_schedule(
        cron_schedule: str, cron_timezone: str = "utc"
    ) -> AutomationCondition:
        """Returns an AutomationCondition which will cause a target to be executed on a
        given cron schedule, regardless of the state of its dependencies

        For time partitioned assets, only the latest time partition will be considered.

        Commonly used for assets in the ingestion layer that should always run on
        a scheduled basis, and have no way of knowing when the source system has
        updates.
        """
        return (
            AutomationCondition.in_latest_time_window()
            & AutomationCondition.cron_tick_passed(
                cron_schedule, cron_timezone
            ).since_last_handled()
        ).with_label(f"on_schedule({cron_schedule}, {cron_timezone})")
