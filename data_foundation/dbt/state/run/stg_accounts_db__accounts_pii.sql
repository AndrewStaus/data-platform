begin;
    
        
        
        delete from _dev_analytics.accounts_db__astaus.accounts_pii as DBT_INTERNAL_DEST
        where (account_id) in (
            select distinct account_id
            from _dev_analytics.accounts_db__astaus.accounts_pii__dbt_tmp as DBT_INTERNAL_SOURCE
        );

    

    insert into _dev_analytics.accounts_db__astaus.accounts_pii ("ACCOUNT_ID", "ACCOUNT_FIRST_NAME", "ACCOUNT_LAST_NAME", "ACCOUNT_EMAIL", "_LOADED_AT")
    (
        select "ACCOUNT_ID", "ACCOUNT_FIRST_NAME", "ACCOUNT_LAST_NAME", "ACCOUNT_EMAIL", "_LOADED_AT"
        from _dev_analytics.accounts_db__astaus.accounts_pii__dbt_tmp
    );
    commit;