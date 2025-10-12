"""dltHub resources that fetch and land exchange rate datasets.

The module wires mocked API loaders into :class:`DagsterDltFactory` so the example
repository can materialize exchange rate tables using Dagster. Each resource exposes
automation metadata to demonstrate how scheduling information flows through dlt to
Dagster assets.
"""

import dlt
from dagster import Definitions
from dagster.components import definitions


#######################################################
@definitions
def defs() -> Definitions:
    """Assemble Dagster definitions for the exchange rate dlt resources.

    Returns:
        dagster.Definitions: Definitions containing Dagster assets that wrap the dlt
        resources defined in this module, complete with automation metadata and
        freshness checks emitted by :class:`DagsterDltFactory`.
    """
    from ...factory import ConfigurableDltResource, DagsterDltFactory
    from .data import get_exchange_rate
    resources = [
        #######################################################
        ConfigurableDltResource.config(
            dlt.resource(
                get_exchange_rate("cad"),
                name="exchange_rate.cad",
                table_name="cad",
                primary_key="date",
                write_disposition="merge",
            ),
            kinds={"api"},
            meta={
                "dagster": {
                    "automation_condition": "on_schedule",
                    "automation_condition_config": {
                        "cron_schedule": "@daily",
                        "cron_timezone": "utc",
                    },
                    # "freshness_lower_bound_delta_seconds": 108000
                }
            },
        ),
        #######################################################
        ConfigurableDltResource.config(
            dlt.resource(
                get_exchange_rate("usd"),
                name="exchange_rate.usd",
                table_name="usd",
                primary_key="date",
                write_disposition="merge",
            ),
            kinds={"api"},
            meta={
                "dagster": {
                    "automation_condition": "on_cron_no_deps",
                    "automation_condition_config": {
                        "cron_schedule": "@daily",
                        "cron_timezone": "utc",
                    },
                    # "freshness_lower_bound_delta_seconds": 108000
                }
            },
        ),
        #######################################################
    ]
    # The factory consumes the configured dlt resources and produces Dagster assets,
    # freshness checks, and external asset placeholders.
    return DagsterDltFactory.build_definitions(tuple(resources))
