"""Example snowpark asset to showcase boilerplate to integrate into dagster"""

import dagster as dg

from .....utils.automation_conditions import CustomAutomationCondition
from ...resources import SnowparkResource
from .asset import materialize


@dg.asset(
        group_name="marketing",
        key=["marketing", "snowpark", "hello_world"],
        deps=[["marketing","fct","fct_attributions"]],
        kinds={"snowpark"},
        description="Example snowpark asset to showcase boilerplate",
        automation_condition=CustomAutomationCondition.on_cron("@daily")
)
def hello_world(
        context: dg.AssetExecutionContext,
        snowpark: SnowparkResource) -> dg.MaterializeResult:
    
    session = snowpark.get_session(schema="transaction_db")

    result_metadata = materialize(session, context)

    return dg.MaterializeResult(metadata=result_metadata)
