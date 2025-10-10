
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select transaction_margin
from _dev_analytics.common__astaus.fct_transactions
where transaction_margin is null



  
  
      
    ) dbt_internal_test