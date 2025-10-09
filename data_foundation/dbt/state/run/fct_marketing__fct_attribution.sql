
  create or replace   view _dev_analytics.astaus.fct_marketing__fct_attribution
  
    
    
(
  
    "ATTRIBUTION_SID" COMMENT $$$$, 
  
    "LOOKBACK_WINDOW" COMMENT $$$$, 
  
    "CRITERIA" COMMENT $$$$, 
  
    "HIT_ID" COMMENT $$$$, 
  
    "INDIVIDUAL_ID" COMMENT $$$$, 
  
    "CAMPAIGN_SID" COMMENT $$$$, 
  
    "TRANSACTION_ID" COMMENT $$$$, 
  
    "ADVERTISED_PRODUCT_ID" COMMENT $$$$, 
  
    "TRANSACTED_PRODUCT_ID" COMMENT $$$$, 
  
    "SALES_CHANNEL" COMMENT $$$$, 
  
    "TRANSACTED_AT" COMMENT $$$$, 
  
    "ATTRIBUTION_START_AT" COMMENT $$$$, 
  
    "ATTRIBUTION_END_AT" COMMENT $$$$, 
  
    "_LOADED_AT" COMMENT $$$$
  
)

   as (
    select * from _dev_analytics.astaus.int_int_marketing__int_attribution_last_click_30d
        union all
    select * from _dev_analytics.astaus.int_int_marketing__int_attribution_last_click_30d_same_brand
        union all
    select * from _dev_analytics.astaus.int_int_marketing__int_attribution_last_click_30d_same_sku
  );

