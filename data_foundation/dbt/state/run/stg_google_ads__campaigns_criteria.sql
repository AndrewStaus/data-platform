begin;
    
        
        
        delete from _dev_analytics.google_ads__astaus.campaigns_criteria as DBT_INTERNAL_DEST
        where (_scd_id) in (
            select distinct _scd_id
            from _dev_analytics.google_ads__astaus.campaigns_criteria__dbt_tmp as DBT_INTERNAL_SOURCE
        );

    

    insert into _dev_analytics.google_ads__astaus.campaigns_criteria ("CAMPAIGN_CRITERIA_ID", "_SCD_ID", "_LOADED_AT")
    (
        select "CAMPAIGN_CRITERIA_ID", "_SCD_ID", "_LOADED_AT"
        from _dev_analytics.google_ads__astaus.campaigns_criteria__dbt_tmp
    );
    commit;