from pathlib import Path

import dagster as dg
from dagster.components import definitions
from data_platform_utils.automation_conditions import CustomAutomationCondition
from snowflake.ml.jobs import submit_file

from ...resources import SnowparkResource


class MLTrainConfig(dg.Config):
    """Exposes configuration options to end users in the Dagster launchpad."""
    retrain_threshold: float = 0.5


@dg.asset(
        key=["ml", "model", "titanic_survived"],
        deps=[["open_data", "stg", "titanic"]],
        kinds={"snowpark", "xgboost"},
        group_name="data_science",
        description="Toy model used to predict survivors of titanic.",
        automation_condition=CustomAutomationCondition.eager()
)
def asset(
        context: dg.AssetExecutionContext,
        snowpark: SnowparkResource,
        config: MLTrainConfig) -> dg.MaterializeResult:

    file_path = Path(__file__).joinpath("..", "train.py").resolve().as_posix()


    session = snowpark.get_session(schema="open_data")
    job = submit_file(
        file_path,
        "SYSTEM_COMPUTE_POOL_GPU",
        enable_telemetry=True,
        enable_metrics=True,
        stage_name="payload_stage",
        session=session
    )
    context.log.info("ML Job started \n"
                f"id: {job.id}\n"
                f"name: {job.name}"
    )

    status = job.wait()
    context.log.info(f"Run completed with status {status}")
    metadata = job.result()


    return dg.MaterializeResult(metadata=metadata)


@definitions
def defs() -> dg.Definitions:
    
    return dg.Definitions(
        assets=[asset]
    )
