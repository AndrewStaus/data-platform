"""dltHub pipelines that simulate Google Ads data ingestion."""

import dlt
from dagster import Definitions
from dagster.components import definitions


#######################################################
@definitions
def defs() -> Definitions:
    """Create Dagster definitions that wrap the simulated Google Ads loaders.

    Returns:
        dagster.Definitions: Definitions representing the Google Ads campaign and
        criterion resources with scheduling metadata applied through
        :class:`DagsterDltFactory`.
    """
    from ...factory import ConfigurableDltResource, DagsterDltFactory
    from .data import google_ads

    resources = [
        #######################################################
        ConfigurableDltResource.config(
            dlt.resource(
                google_ads("get_campaigns"),
                name="google_ads.campaigns",
                table_name="campaigns",
                primary_key="id",
                write_disposition="merge"
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
                google_ads("get_criterion"),
                name="google_ads.criterion",
                table_name="criterion",
                primary_key="id",
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
    ]
    # Delegate to the shared factory so that asset metadata stays consistent across
    # dlt-based examples.
    return DagsterDltFactory.build_definitions(tuple(resources))
