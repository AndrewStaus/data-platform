
    
    

with all_values as (

    select
        hit_source as value_field,
        count(*) as n_records

    from analytics.adobe_experience.hits
    group by hit_source

)

select *
from all_values
where value_field not in (
    'web','app'
)


