with
google_ads_campaigns as (
    select * from analytics.google_ads.campaigns
),

facebook_ads_campaigns as (
    select * from analytics.facebook_ads.campaigns
),

united as (
    select
        *,
        'gooogle_ads' campaign_source
    from google_ads_campaigns
    

    union all by name

    select
        *,
        'facebook_ads' campaign_source
    from facebook_ads_campaigns
    
)

select
    concat_ws(':', campaign_id, campaign_source) campaign_sid,
    * exclude (campaign_update_date)
from united