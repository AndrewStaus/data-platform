
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select _loaded_at
from _dev_analytics.common__astaus.fct_transactions
where _loaded_at is null



  
  
      
    ) dbt_internal_test