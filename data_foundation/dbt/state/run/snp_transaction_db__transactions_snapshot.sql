
      begin;
    merge into _dev_snapshots.transaction_db__astaus.transactions as DBT_INTERNAL_DEST
    using _dev_snapshots.transaction_db__astaus.transactions__dbt_tmp as DBT_INTERNAL_SOURCE
    on DBT_INTERNAL_SOURCE.dbt_scd_id = DBT_INTERNAL_DEST.dbt_scd_id

    when matched
     
	
	
	and ((DBT_INTERNAL_DEST.dbt_valid_to = to_date('9999-12-31'))
 or DBT_INTERNAL_DEST.dbt_valid_to is null)

     
     and DBT_INTERNAL_SOURCE.dbt_change_type in ('update', 'delete')
        then update
        set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to

    when not matched
     and DBT_INTERNAL_SOURCE.dbt_change_type = 'insert'
        then insert ("ORDER_ID", "CHANNEL", "PARTY_KEY", "PRODUCT_ID", "REVENUE", "MARGIN", "DATE_TIME", "_SLING_LOADED_AT", "DBT_UPDATED_AT", "DBT_VALID_FROM", "DBT_VALID_TO", "DBT_SCD_ID")
        values ("ORDER_ID", "CHANNEL", "PARTY_KEY", "PRODUCT_ID", "REVENUE", "MARGIN", "DATE_TIME", "_SLING_LOADED_AT", "DBT_UPDATED_AT", "DBT_VALID_FROM", "DBT_VALID_TO", "DBT_SCD_ID")

;
    commit;
  