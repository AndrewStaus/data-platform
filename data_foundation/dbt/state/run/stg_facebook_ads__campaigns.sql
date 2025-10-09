begin;
    
        
        
        delete from _dev_analytics.facebook_ads__astaus.campaigns as DBT_INTERNAL_DEST
        where (campaign_id) in (
            select distinct campaign_id
            from _dev_analytics.facebook_ads__astaus.campaigns__dbt_tmp as DBT_INTERNAL_SOURCE
        );

    

    insert into _dev_analytics.facebook_ads__astaus.campaigns ("CAMPAIGN_ID", "CAMPAIGN_NAME", "CAMPAIGN_START_DATE", "CAMPAIGN_UPDATE_DATE", "_LOADED_AT")
    (
        select "CAMPAIGN_ID", "CAMPAIGN_NAME", "CAMPAIGN_START_DATE", "CAMPAIGN_UPDATE_DATE", "_LOADED_AT"
        from _dev_analytics.facebook_ads__astaus.campaigns__dbt_tmp
    );
    commit;