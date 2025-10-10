with campaigns as (
    select * from raw.google_ads.campaigns
)

select
    id::int          campaign_id,
    name::text       campaign_name,
    start_date::date campaign_start_date,
    to_timestamp(split(_dlt_load_id, '.')[0])::timestamp  _loaded_at --noqa:all
from campaigns



qualify 1 = row_number() over (partition by id order by _loaded_at desc)