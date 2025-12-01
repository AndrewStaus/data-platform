from dataclasses import dataclass
from typing import Any

from snowflake.ml.modeling.pipeline.pipeline import Pipeline
from snowflake.ml.modeling.preprocessing.one_hot_encoder import OneHotEncoder
from snowflake.ml.modeling.preprocessing.standard_scaler import StandardScaler
from snowflake.ml.modeling.xgboost.xgb_classifier import XGBClassifier
from snowflake.ml.registry.registry import Registry
from snowflake.snowpark import Session
from snowflake.snowpark.dataframe import DataFrame


@dataclass
class Config:
    table_name = "titanic"
    model_name = "titanic_survived"
    model_description = "Toy model used to predict survivors of the titanic."
    categorical_columns = ["SEX", "EMBARKED", "BOAT"]
    numerical_columns = ["AGE", "PCLASS", "FARE", "SIBSP", "PARCH"]
    target_column = "SURVIVED"
    train_compute_pool = "SYSTEM_COMPUTE_POOL_GPU"
    stage_name = "payload_stage"


def main(config=None) -> dict[str, str | float | None]:
    print("Execution Started")
    config = config or Config()

    versions = [train_model(config)]
    version, score = promote_best(config, versions)
    
    return {"model_name": config.model_name, "version": version, "score": score}

def promote_best(config: Config, versions) -> tuple[Any | None, Any ]:
    print("promoting best model")
    session = get_session()
    registry = Registry(session)
    model_ref = registry.get_model(config.model_name)
    
    top_version = None
    top_score = 0
    for version in versions:
        score = model_ref.version(version).get_metric("score")
        if score > top_score:
            top_version = version
            top_score = score
    
    if top_version:
        model_ref.default = top_version

    return top_version, top_score


def train_model(config: Config) -> str:
    print("Training Model")

    df = get_data(config)
    train, test = df.random_split(weights=[0.7, 0.3], seed=42)

    model = Pipeline(steps=[
            ("onehot", OneHotEncoder(
                categories="auto",
                input_cols=config.categorical_columns,
                output_cols=config.categorical_columns,
                handle_unknown="ignore",
                drop_input_cols=True
            )),
            ("scale", StandardScaler(
                input_cols=config.numerical_columns,
                output_cols=config.numerical_columns,
                drop_input_cols=True
            )),
            ("reg", XGBClassifier(
                label_cols=[config.target_column],
                output_cols=["PRED"],
                drop_input_cols=True
            ))
    ]).fit(train)
    
    score = score_model(model, test)
    return register(config, model, score, df)

def get_data(config: Config) -> DataFrame:
    print("Getting data")
    session = get_session()
    return (
        session.table(config.table_name)
        .select(
            *config.categorical_columns,
            *config.numerical_columns,
            config.target_column
        )
    )

def score_model(model: Pipeline, test: DataFrame) -> float:
    print("Scoring Model")
    score = float(model.score(test)) # type: ignore
    return score 

def register(config: Config, model: Pipeline, score: float, df: DataFrame)  -> str:
    print("Registering Model")
    session = get_session()

    registry = Registry(session)

    model_ref = registry.log_model(
        model,
        model_name=config.model_name,
        comment=config.model_description,
        sample_input_data=df.limit(100).drop(config.target_column),
        metrics={"score": score},
    )
    version_name = model_ref.version_name
    return version_name

def get_session() -> Session:
    session = Session.get_active_session()
    assert session
    return session

if __name__ == "__main__":
    main()