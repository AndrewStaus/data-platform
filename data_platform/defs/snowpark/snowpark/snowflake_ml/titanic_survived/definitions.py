import dagster as dg

from ......utils.automation_conditions import CustomAutomationCondition
from ....resources import SnowparkResource
from .model import materialze


class MLTrainConfig(dg.Config):
    """Exposes configuration options to end users in the Dagster launchpad."""
    retrain_treshold: float = 0.5


@dg.asset(
        key=["ml", "model", "titanic_survived"],
        deps=[["open_data", "stg", "titanic"]],
        kinds={"snowpark", "xgboost"},
        group_name="data_science",
        description="Toy model used to predict survivors of titanic.",
        automation_condition=CustomAutomationCondition.on_cron("@monthly")
)
def asset(
        context: dg.AssetExecutionContext,
        snowpark: SnowparkResource,
        config: MLTrainConfig) -> dg.MaterializeResult:

    session = snowpark.get_session(schema="open_data")
    metadata = materialze(context, session, config.retrain_treshold)

    return dg.MaterializeResult(metadata=metadata)

@dg.asset_check(
        asset=["ml", "model", "titanic_survived"],
        description=("Check that default version of model scores above"
                     "threshold for retraining")
)
def score_above_threshold_check(
        snowpark: SnowparkResource,
        config: MLTrainConfig) -> dg.AssetCheckResult:
    
    from snowflake.ml.registry.registry import Registry
    session = snowpark.get_session(schema="open_data")
    registry = Registry(session)
    model = registry.get_model("titanic_survived").default
    score = model.get_metric("score")
    return dg.AssetCheckResult(
        passed=bool(score > config.retrain_treshold),
        metadata={"score": score}
    )
