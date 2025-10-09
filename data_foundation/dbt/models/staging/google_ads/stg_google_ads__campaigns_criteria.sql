{{-
    config(
        schema = "google_ads",
        alias = "campaigns_criteria",
        materialized = "incremental",
        unique_key = "_scd_id",
        incremental_strategy='delete+insert',
        meta = {
            "dagster": {
                "automation_condition": "eager",
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        }
    )
-}}

with
campaign_criteria as (
    select * from {{ source('google_ads', 'campaigns__criteria') }}
),

campaigns as (
    select * from {{ source('google_ads', 'campaigns') }}
)

select
    b.id::int       campaign_criteria_id,
    b._dlt_id::text _scd_id,
    {{ dlt_loaded_at() }} _loaded_at, --noqa:all
from campaigns a
inner join campaign_criteria b on a._dlt_id = b._dlt_parent_id

{% if is_incremental() -%}
    where _loaded_at >= coalesce((select max(_loaded_at) from {{ this }}), '1900-01-01')
{%- endif %}
