
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        hit_source as value_field,
        count(*) as n_records

    from _dev_analytics.adobe_experience__astaus.hits
    group by hit_source

)

select *
from all_values
where value_field not in (
    'web','app'
)



  
  
      
    ) dbt_internal_test