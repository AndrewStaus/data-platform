 -- noqa: Should accept a string instead of a integer
    
    
    truncate table _dev_analytics.astaus.dim_marketing__dim_campaign_details;
    -- dbt seed --
    
            insert into _dev_analytics.astaus.dim_marketing__dim_campaign_details (CAMPAIGN_ID, BRAND, CATEGORY) values
            (%s,%s,%s),(%s,%s,%s),(%s,%s,%s)
        

;
  