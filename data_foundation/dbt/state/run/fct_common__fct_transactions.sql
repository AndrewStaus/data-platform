
  create or replace   view _dev_analytics.common__astaus.fct_transactions
  
    
    
(
  
    "TRANSACTION_ID" COMMENT $$The identifier of the transaction, unique when concatentated with product_id$$, 
  
    "PRODUCT_ID" COMMENT $$The id of the product sold on the transaction, unique when concatentated with transaction_id$$, 
  
    "SALES_CHANNEL" COMMENT $$$$, 
  
    "INDIVIDUAL_PARTY_KEY" COMMENT $$$$, 
  
    "TRANSACTION_REVENUE" COMMENT $$the total sale item$$, 
  
    "TRANSACTION_MARGIN" COMMENT $$the gross margin after unit costs are considered$$, 
  
    "TRANSACTED_AT" COMMENT $$$$, 
  
    "_LOADED_AT" COMMENT $$the time the data was loaded from source$$
  
)

   as (
    with transactions as (
    select * from _dev_analytics.transaction_db__astaus.transactions
)

select * from transactions
  );

