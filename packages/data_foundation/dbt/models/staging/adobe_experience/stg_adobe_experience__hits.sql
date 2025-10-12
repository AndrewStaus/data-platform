{{-
    config(
        schema = "adobe_experience",
        alias = "hits",
        materialized = "incremental",
        incremental_strategy = "delete+insert",
        unique_key = "hit_at",
        tags = ["partitioned"],
        meta = {
            "dagster": {
                "partition": "daily",
                "partition_start_date": "2025-07-01",
                "automation_condition": "eager",
                "freshness_check": {"deadline_cron": "@daily"}
            }
        }
    )
-}}

with
web_hits as (
    select * from {{ source("adobe_experience", "web_hits") }}
),

app_hits as (
    select * from {{ source("adobe_experience", "app_hits") }}
),

accounts as (
    select * from {{ source("accounts_db", "accounts") }}
),

united_hits as (
    select
        *,
        'web' hit_source
    from web_hits

    union all

    select
        *,
        'app' hit_source
    from app_hits
)

select
    h.hit_source,
    {{ pst_to_utc("date_time") }} hit_at, --noqa:all
    h.mcvisid                                           marketing_cloud_visitor_id,
    concat_ws(':', h.post_visid_high, h.post_visid_low) visit_id,
    concat_ws(':', visit_id, h.hitid_high, h.hitid_low) hit_id,
    concat_ws(':', h.hit_source, hit_id)                hit_sid,
    h.page_url                                          hit_url,
    a.party_key                                         individual_party_key,
    h.orderid                                           order_id,
    h._sling_loaded_at                                  _loaded_at
from united_hits h
left join accounts a on h.post_evar133 = a.id

{% if is_incremental() -%}
    where
        hit_at >= '{{ var("min_date", "1900-01-01") }}'
        and hit_at <= '{{ var("max_date", "9999-12-31") }}'
{%- endif %}
