from typing import Any

import dagster as dg
from snowflake.snowpark.dataframe import DataFrame
from snowflake.snowpark.session import Session


def materialize(
        context: dg.AssetExecutionContext,
        session: Session,
        retrain_threshold: float
        ) -> dict[str, Any]:
    """Model retrain pipeline steps:
        1. get current version of model from registry
        2. score against validation data set
        3. log metrics
        4. if score above threshold skip retraining
        5. else train new models using training dataset
        6. select top scoring model
        7. score against validation data set
        8. if score below previous model score do not register model
        9. else register and promote model as default version
        10. if score is still below threshold, asset check will alert an issue in
        dagster
    """
    from snowflake.ml.model.type_hints import SupportedModelType
    from snowflake.ml.registry.registry import Registry


    model_name = "titanic_survived"
    categorical_columns = ["SEX", "EMBARKED", "BOAT"]
    numerical_columns = ["AGE", "PCLASS", "FARE", "SIBSP", "PARCH"]
    target_column = "SURVIVED"

    val = _get_validation_data(session,
                               categorical_columns,
                               numerical_columns,
                               target_column)

    registry = Registry(session)
    try:
        model_ref = registry.get_model(model_name).default

    except Exception:
        model_ref = None

    if model_ref:
        context.log.info("previous version found, checking score.")
        model: SupportedModelType = model_ref.load() 
        old_version_name = model_ref.version_name
        old_score = model.score(val) # type: ignore
        model_ref.set_metric("score", old_score)
        if old_score >= retrain_threshold:
            context.log.info("Score above threshold, skipping retrain.")
            return {"version": model_ref.version_name, "score": old_score}
        else:
            context.log.info("Score below threshold, starting retrain.")

    else:
        context.log.info("No previous model version found.")
        old_score = 0.0
        old_version_name = "not_registered"

    context.log.info("Training model.")
    df = _get_train_data(session,
                         categorical_columns,
                         numerical_columns,
                         target_column)

    model: SupportedModelType = _train_model(df, context,
                         categorical_columns,
                         numerical_columns,
                         target_column)

    new_score = float(model.score(val)) # type: ignore

    if new_score >= old_score:
        context.log.info("Registering new model version.")
        model_ref = registry.log_model(
            model,
            model_name=model_name,
            comment="Toy model used to predict survivors of the titanic.",
            sample_input_data=df.drop("SURVIVED"),
            metrics={"score": new_score},
        )
        version_name = model_ref.version_name
        model_ref = registry.get_model(model_name)
        model_ref.default = version_name

        return {"version": version_name, "score": new_score}
    
    else:
        context.log.info("New model performance worse than previous version, "
                         "retaining previous version.")
        return {"version": old_version_name, "score": old_score}

def _train_model(df: DataFrame, context: dg.AssetExecutionContext,
                    categorical_columns: list[str],
                    numerical_columns: list[str],
                    target_column: str):

    from snowflake.ml.modeling.ensemble.random_forest_classifier import (
        RandomForestClassifier,
    )
    from snowflake.ml.modeling.pipeline.pipeline import Pipeline
    from snowflake.ml.modeling.preprocessing.one_hot_encoder import OneHotEncoder
    from snowflake.ml.modeling.preprocessing.standard_scaler import StandardScaler
    from snowflake.ml.modeling.xgboost.xgb_classifier import XGBClassifier
    from snowflake.snowpark import functions as F
    
    # use SMOTE here
    positive_count = df.filter(F.col(target_column) == 1).count()
    negative_count = df.filter(F.col(target_column) == 0).count()

    context.log.info(f"Positive count: {positive_count}")
    context.log.info(f"Negative count: {negative_count}")

    train, test = df.random_split(weights=[0.7, 0.3], seed=42)


    # use grid search cv
    selected_model = None
    selected_type = None
    top_score = 0.0

    transformers = [XGBClassifier, RandomForestClassifier]
    
    for Transformer in transformers:
        context.log.info(f"training {Transformer}")

        model = Pipeline(steps=[
                ("onehot", OneHotEncoder(
                    categories="auto",
                    input_cols=categorical_columns,
                    output_cols=categorical_columns,
                    handle_unknown="ignore",
                    drop_input_cols=True
                )),
                ("scale", StandardScaler(
                    input_cols=numerical_columns,
                    output_cols=numerical_columns,
                    drop_input_cols=True
                )),
                ("reg", Transformer(
                    label_cols=[target_column],
                    output_cols=["PRED"],
                    drop_input_cols=True
                ))
        ]).fit(train)

        score = float(model.score(test)) # type: ignore
        context.log.info(f"{Transformer}: {score}")

        if score > top_score:
            selected_model = model
            selected_type = Transformer
            top_score = score

    context.log.info(f"{selected_type} model selected")
    return selected_model

def _get_train_data(session: Session,
                    categorical_columns: list[str],
                    numerical_columns: list[str],
                    target_column: str) -> DataFrame:

    return (
        session.table("titanic")
        .select(
            *categorical_columns,
            *numerical_columns,
            target_column
        )
    )

def _get_validation_data(session: Session,
                    categorical_columns: list[str],
                    numerical_columns: list[str],
                    target_column: str) -> DataFrame:
    return (
        session.table("titanic")
        .select(
            *categorical_columns,
            *numerical_columns,
            target_column
        )
    )
