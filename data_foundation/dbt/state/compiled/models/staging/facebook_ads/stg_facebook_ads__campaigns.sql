with campaigns as (
    select * from raw.facebook_ads.campaigns
)

select
    id::int            campaign_id,
    name::text         campaign_name,
    start_date::date   campaign_start_date,
    updated::timestamp campaign_update_date,
    to_timestamp(split(_dlt_load_id, '.')[0])::timestamp _loaded_at --noqa:all
from campaigns

