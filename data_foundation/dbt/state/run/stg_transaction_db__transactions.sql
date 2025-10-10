begin;
    
        
        
        delete from _dev_analytics.transaction_db__astaus.transactions as DBT_INTERNAL_DEST
        where (transaction_id) in (
            select distinct transaction_id
            from _dev_analytics.transaction_db__astaus.transactions__dbt_tmp as DBT_INTERNAL_SOURCE
        );

    

    insert into _dev_analytics.transaction_db__astaus.transactions ("TRANSACTION_ID", "PRODUCT_ID", "SALES_CHANNEL", "INDIVIDUAL_PARTY_KEY", "TRANSACTION_REVENUE", "TRANSACTION_MARGIN", "TRANSACTED_AT", "_LOADED_AT")
    (
        select "TRANSACTION_ID", "PRODUCT_ID", "SALES_CHANNEL", "INDIVIDUAL_PARTY_KEY", "TRANSACTION_REVENUE", "TRANSACTION_MARGIN", "TRANSACTED_AT", "_LOADED_AT"
        from _dev_analytics.transaction_db__astaus.transactions__dbt_tmp
    );
    commit;