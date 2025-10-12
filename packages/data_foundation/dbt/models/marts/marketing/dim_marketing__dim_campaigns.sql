{{-
    config(
        schema = "marketing",
        alias = "dim_campaigns",
        materialized="incremental",
        unique_key="campaign_sid",
        incremental_strategy="delete+insert",
        grants={"select":["marketing"]},
        meta = {
            "dagster": {
                "automation_condition": "on_cron",
                "automation_condition_config": {
                    "cron_schedule":"@daily",
                    "cron_timezone":"utc",
                    "ignore_asset_keys": ["google_ads","stg", "campaigns"]},
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        }
    )
-}}

with
google_ads_campaigns as (
    select * from {{ ref("stg_google_ads__campaigns") }}
),

facebook_ads_campaigns as (
    select * from {{ ref("stg_facebook_ads__campaigns") }}
),

united as (
    select
        *,
        'gooogle_ads' campaign_source
    from google_ads_campaigns
    {% if is_incremental() -%}
        where _loaded_at >= coalesce((
            select max(_loaded_at)
            from {{ this }}
            where campaign_source = 'google_ads'
        ),
        '1900-01-01'
        )
    {%- endif %}

    union all by name

    select
        *,
        'facebook_ads' campaign_source
    from facebook_ads_campaigns
    {% if is_incremental() -%}
        where _loaded_at >= coalesce((
            select max(_loaded_at)
            from {{ this }}
            where campaign_source = 'facebook_ads'
        ),
        '1900-01-01'
        )
    {%- endif %}
)

select
    concat_ws(':', campaign_id, campaign_source) campaign_sid,
    * exclude (campaign_update_date)
from united
