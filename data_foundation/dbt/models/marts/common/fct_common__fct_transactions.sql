{{-
    config(
        schema = "common",
        alias = "fct_transactions",
        materialized = "dynamic_table",
        target_lag = "24 hour",
        snowflake_warehouse = "compute_wh"
    )
-}}

with transactions as (
    select * from {{ ref("stg_transaction_db__transactions") }}
)

select * from transactions
