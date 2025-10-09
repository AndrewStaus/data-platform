begin;
    
        
        
        delete from _dev_analytics.entity_resolution__astaus.individual_party_keys as DBT_INTERNAL_DEST
        where (individual_party_key) in (
            select distinct individual_party_key
            from _dev_analytics.entity_resolution__astaus.individual_party_keys__dbt_tmp as DBT_INTERNAL_SOURCE
        );

    

    insert into _dev_analytics.entity_resolution__astaus.individual_party_keys ("INDIVIDUAL_PARTY_KEY", "INDIVIDUAL_ID", "UPDATED_AT", "_LOADED_AT")
    (
        select "INDIVIDUAL_PARTY_KEY", "INDIVIDUAL_ID", "UPDATED_AT", "_LOADED_AT"
        from _dev_analytics.entity_resolution__astaus.individual_party_keys__dbt_tmp
    );
    commit;