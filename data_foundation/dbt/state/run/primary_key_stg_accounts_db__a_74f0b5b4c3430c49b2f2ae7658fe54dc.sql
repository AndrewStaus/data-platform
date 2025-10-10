
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  select validation_errors.* from (
    select
        pk_test.account_id, count(*) as n_records
    from _dev_analytics.accounts_db__astaus.accounts_pii pk_test
    group by pk_test.account_id
    having count(*) > 1
        or pk_test.account_id is null
        
) validation_errors
  
  
      
    ) dbt_internal_test