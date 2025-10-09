
      
  
    

        create or replace transient table _dev_snapshots.accounts_db.accounts_snapshot
         as
        (
    

    select *,
        md5(coalesce(cast(id as varchar ), '')
         || '|' || coalesce(cast(updated_at as varchar ), '')
        ) as dbt_scd_id,
        updated_at as dbt_updated_at,
        updated_at as dbt_valid_from,
        
  
  coalesce(nullif(updated_at, updated_at), to_date('9999-12-31'))
  as dbt_valid_to
from (
        select * from raw.accounts_db.accounts
    ) sbq



        );
      
  
  