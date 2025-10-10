with
campaign_criteria as (
    select * from raw.google_ads.campaigns__criteria
),

campaigns as (
    select * from raw.google_ads.campaigns
)

select
    b.id::int       campaign_criteria_id,
    b._dlt_id::text _scd_id,
    to_timestamp(split(_dlt_load_id, '.')[0]) _loaded_at, --noqa:all
from campaigns a
inner join campaign_criteria b on a._dlt_id = b._dlt_parent_id

