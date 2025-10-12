"""dltHub resources that simulate Facebook Ads ingestion for Dagster demos."""

import dlt
from dagster import Definitions
from dagster.components import definitions


#######################################################
@definitions
def defs() -> Definitions:
    """Assemble Dagster definitions for the mock Facebook Ads dataset.

    Returns:
        dagster.Definitions: Definitions that wrap the dlt resource used to ingest
        campaign data, including automation metadata surfaced through the factory.
    """
    from ...factory import ConfigurableDltResource, DagsterDltFactory
    from .data import get_campaigns

    resources = [
        #######################################################
        ConfigurableDltResource.config(
            dlt.resource(
                get_campaigns,
                name="facebook_ads.campaigns",
                table_name="campaigns",
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
        )
        #######################################################
    ]
    # Reuse the shared factory to ensure consistent resource wiring.
    return DagsterDltFactory.build_definitions(tuple(resources))
