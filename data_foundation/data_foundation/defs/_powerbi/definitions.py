"""Sample Dagster assets that mirror a Power BI deployment structure.

These definitions intentionally remain lightweight: the semantic model asset simulates
an expensive refresh, while the downstream ``AssetSpec`` objects model dashboards that
depend on the shared semantic model. In production a factory would emit these assets
based on Power BI metadata, but the stubs provide realistic wiring for demos and
integration tests.
"""

from datetime import timedelta
from time import sleep

import dagster as dg


@dg.asset(
    key=["bi", "sm", "core_semantic_model"],
    deps=[["common", "fct", "fct_transactions"], ["common", "dim", "dim_customers"]],
    owners=["analytics@email.com"],
    kinds={"powerbi"},
    group_name="bi",
    automation_condition=dg.AutomationCondition.eager(),
    description="This is the core semantic model that is used by business "
    "leadership to self serve analtics",
)
def bi_sm_core_semantic_model(context: dg.AssetExecutionContext) -> None:
    """Refresh the sample Power BI semantic model used by downstream dashboards.

    Args:
        context: Dagster execution context supplied by the runtime. The handler is
            used exclusively for structured logging in this stub implementation.

    Returns:
        None: The asset does not produce any materialization payload; Dagster tracks
        completion based on the asset invocation finishing without raising an error.
    """
    context.log.info("refreshing powerbi semantic model")
    sleep(10)
    context.log.info("refresh complete")
    return None


executive_dashboard_freshness = dg.build_last_update_freshness_checks(
    assets=[bi_sm_core_semantic_model], lower_bound_delta=timedelta(days=1)
)


# These asset specs mirror dashboards in Power BI and model the implicit dependency on
# the shared semantic model defined above.  They are intentionally lightweight stubs
# that would be replaced by a factory in a production deployment.
bi_exp_executive_dashboard = dg.AssetSpec(
    key=["bi", "exp", "executive_dashboard"],
    deps=[
        ["bi", "sm", "core_semantic_model"],
    ],
    kinds={"powerbi"},
    group_name="bi",
)

bi_exp_daily_metrics = dg.AssetSpec(
    key=["bi", "exp", "daily_metrics"],
    deps=[
        ["bi", "sm", "core_semantic_model"],
    ],
    kinds={"powerbi"},
    group_name="bi",
)

bi_exp_weekly_metrics = dg.AssetSpec(
    key=["bi", "exp", "weekly_metrics"],
    deps=[
        ["bi", "sm", "core_semantic_model"],
    ],
    kinds={"powerbi"},
    group_name="bi",
)
