import dlt
from dagster import Definitions
from dagster.components import definitions


#######################################################
@definitions
def defs() -> Definitions:
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
    return DagsterDltFactory.build_definitions(tuple(resources))
