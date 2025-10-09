
  
    

        create or replace transient table _dev_analytics.marketing__astaus.dim_campaigns
         as
        (with
google_ads_campaigns as (
    select * from _dev_analytics.google_ads__astaus.campaigns
),

facebook_ads_campaigns as (
    select * from _dev_analytics.facebook_ads__astaus.campaigns
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
        );
      
  