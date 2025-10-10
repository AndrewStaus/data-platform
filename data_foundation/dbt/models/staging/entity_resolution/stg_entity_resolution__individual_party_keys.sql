{{-
    config(
        schema = "entity_resolution",
        alias = "individual_party_keys",
        materialized = "incremental",
        unique_key = "individual_party_key",
        incremental_strategy = "delete+insert",
        meta = {
            "dagster": {
                "automation_condition": "eager",
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        }
    )
-}}


with individual_party_keys as (
    select * from {{ source("entity_resolution", "individual_party_keys") }}
)

select
    party_key        individual_party_key,
    entity_id        individual_id,
    updated          updated_at,
    _sling_loaded_at _loaded_at
from individual_party_keys

{% if is_incremental() -%}
    where _loaded_at >= coalesce((select max(_loaded_at) from {{ this }}), '1900-01-01')
{%- endif %}
