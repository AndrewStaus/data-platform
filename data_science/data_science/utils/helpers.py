import os
from collections.abc import Callable, Mapping
from datetime import datetime
from inspect import signature
from typing import Any

import dagster as dg

from .automation_conditions import CustomAutomationCondition

def get_schema_name(schema: str) -> str:
    postfix = os.getenv("DESTINATION__USER", "")
    if os.getenv("TARGET") == "dev":
        schema = f"{schema}__{postfix}"
    return schema

def get_database_name(database: str) -> str:
    if os.getenv("TARGET") == "dev":
        database = f"_dev_{database}"
    return database

def get_automation_condition_from_meta(
    meta: dict[str, Any],
) -> dg.AutomationCondition | None:
    """Return an AutomationCondition if valid configuartion is provided in the meta.
    Meta should be of format dict in the following structure:
    .. code-block:: python
        "meta":{
            "dagster":{
                "automation_condition": condition,
                "automation_condition_config": {argument: value}
            }
        }
    """
    condition_name = meta.get("automation_condition")
    if not condition_name:
        return None

    condition = CustomAutomationCondition.get_automation_condition(condition_name)
    if not isinstance(condition, Callable):
        raise KeyError(f"Automation condition not found for key '{condition_name}'")

    condition_config = meta.get("automation_condition_config", {}) or {}
    if not isinstance(condition_config, dict):
        raise ValueError(f"Invalid condition config: '{condition_config}'")

    condition_config = sanitize_input_signature(condition, condition_config)
    try:
        return condition(**condition_config)
    except Exception as e:
        # e.message(
        #     "'condition_config' is missing required keys"
        #     f"for condition '{condition_name}'"
        # )
        raise e


def get_partitions_def_from_meta(
    meta: dict[str, Any],
) -> dg.TimeWindowPartitionsDefinition | None:
    """Return an TimeWindowPartitionsDefinition if valid configuartion is provided in
    the meta.
    - partition accepts the values: hourly, daily, weekly, monthly.
    - partition_start_date should be a iso format date, or timestamp.

    Meta should be of format dict in the following structure:
    .. code-block:: python
       "meta":{
           "dagster":{
               "partition": "daily",
               "partition_start_date": "2025-01-01"
           }
       }
    """
    try:
        partition = meta.get("partition")
        partition_start_date = meta.get("partition_start_date")

        if partition and partition_start_date:
            start_date = datetime.fromisoformat(partition_start_date)
            if partition == "hourly":
                return dg.HourlyPartitionsDefinition(
                    start_date=start_date.strftime("%Y-%m-%d-%H:%M")
                )
            if partition == "daily":
                return dg.DailyPartitionsDefinition(
                    start_date=start_date.strftime("%Y-%m-%d")
                )
            if partition == "weekly":
                return dg.WeeklyPartitionsDefinition(
                    start_date=start_date.strftime("%Y-%m-%d")
                )
            if partition == "monthly":
                return dg.MonthlyPartitionsDefinition(
                    start_date=start_date.strftime("%Y-%m-%d")
                )
    except Exception:
        ...
    return None


def sanitize_input_signature(func: Callable, kwargs: dict) -> dict:
    """Remove any arguments that are not expected by the recieving function."""
    sig = signature(func)
    key_words = list(kwargs.keys())
    expected_arguments = {argument for argument, _ in sig.parameters.items()}

    for argument in key_words:
        if argument not in expected_arguments:
            kwargs.pop(argument)

    return kwargs


def get_nested(config: Mapping[str, Any], path: list[str]) -> Any:
    """Helper function to safely traverse a nested dictionary that may have null values
    for a set key that is expected to be a dict. helpful because stream definitions that
    use only the default configs behave this way.
    .. code-block:: yaml
    streams:
        source.table_one:
        source.table_two:
    """
    try:
        for item in path:
            config = config[item]
        return config
    except Exception:
        ...
    return None
