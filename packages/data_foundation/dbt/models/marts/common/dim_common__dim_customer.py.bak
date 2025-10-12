def model(dbt, session):
    session.use_schema("public")
    dbt.config(
        python_version="3.11",
        packages=["faker"],
        materialization="incremental",
        incremental_strategy="merge",
        unique_key="account_id",
        meta={
            "dagster": {
                "automation_condition": "on_cron",
                "automation_condition_config": {
                    "cron_schedule": "@daily",
                    "cron_timezone": "utc",
                },
                "freshness_check": {"lower_bound_delta_seconds": 129600},
            }
        },
    )
    from faker import Faker
    from snowflake.snowpark import functions as F

    fake = Faker()

    # define udfs for synthetic data generation
    @F.udf
    def syn_first_name(col: str) -> str:
        fake.seed_locale("en_US", col)
        return fake.first_name()

    @F.udf
    def syn_last_name(col: str) -> str:
        fake.seed_locale("en_US", col)
        return fake.last_name()

    # load upstream table to dateframe
    df = dbt.ref("stg_accounts_db__accounts")
    cols = df.columns

    # incremental settings
    if dbt.is_incremental:
        max_from_this = f"select max(_loaded_at) from {dbt.this}"
        df = df.filter(df["_loaded_at"] >= session.sql(max_from_this).collect()[0][0])

    # apply synthetic function to first name column
    df_fn = (
        df.select("account_first_name")
        .distinct()
        .with_column(
            "syn_first_name", F.lower(syn_first_name(F.col("account_first_name")))
        )
    )

    # apply synthetic function to last name column
    df_ln = (
        df.select("account_last_name")
        .distinct()
        .with_column(
            "syn_last_name", F.lower(syn_last_name(F.col("account_last_name")))
        )
    )

    # apply synthetic data over hashed columns
    df = (
        df.join(df_fn, "account_first_name")
        .join(df_ln, "account_last_name")
        .with_column("account_first_name", df_fn["syn_first_name"])
        .with_column("account_last_name", df_ln["syn_last_name"])
        .select(*cols)
    )

    return df
