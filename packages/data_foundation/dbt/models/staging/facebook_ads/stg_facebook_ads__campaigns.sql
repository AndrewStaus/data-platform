{{-
    config(
        schema = "facebook_ads",
        alias = "campaigns",
        materialized = "incremental",
        unique_key = "campaign_id",
        incremental_strategy="delete+insert",
        meta = {
            "dagster": {
                "automation_condition": "eager",
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        }
    )
-}}

with campaigns as (
    select * from {{ source('facebook_ads', 'campaigns') }}
)

select
    id::int            campaign_id,
    name::text         campaign_name,
    start_date::date   campaign_start_date,
    updated::timestamp campaign_update_date,
    {{ dlt_loaded_at() }}::timestamp _loaded_at --noqa:all
from campaigns

{% if is_incremental() -%}
    where _loaded_at >= coalesce((select max(_loaded_at) from {{ this }}), '1900-01-01')
{%- endif %}
