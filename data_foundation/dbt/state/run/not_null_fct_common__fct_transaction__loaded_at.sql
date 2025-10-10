
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select _loaded_at
from _dev_analytics.astaus.fct_common__fct_transaction
where _loaded_at is null



  
  
      
    ) dbt_internal_test