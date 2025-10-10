{{-
    config(
        schema = "transaction_db",
        alias = "transactions",
        materialized = "incremental",
        unique_key = "transaction_id",
        incremental_strategy = "delete+insert",
        meta = {
            "dagster": {
                "automation_condition": "eager",
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        }
    )
-}}

with transactions as (
    select * from {{ source("transaction_db", "transactions") }}
)

select
    order_id::int                           transaction_id,
    product_id::varchar(10)                 product_id,
    channel::varchar(25)                    sales_channel,
    party_key::varchar(25)                  individual_party_key,
    round(revenue / 100, 2)::decimal(16, 2) transaction_revenue,
    round(margin / 100, 2)::decimal(16, 2)  transaction_margin,
    {{ pst_to_utc("date_time")  }}          transacted_at, --noqa:all
    _sling_loaded_at::timestamp             _loaded_at
from transactions

{% if is_incremental() -%}
    where _loaded_at >= coalesce((select max(_loaded_at) from {{ this }}), '1900-01-01')
{%- endif %}
