begin;
    
        
        
        delete from _dev_analytics.adobe_experience__astaus.hits as DBT_INTERNAL_DEST
        where (hit_at) in (
            select distinct hit_at
            from _dev_analytics.adobe_experience__astaus.hits__dbt_tmp as DBT_INTERNAL_SOURCE
        );

    

    insert into _dev_analytics.adobe_experience__astaus.hits ("HIT_SOURCE", "HIT_AT", "MARKETING_CLOUD_VISITOR_ID", "VISIT_ID", "HIT_ID", "HIT_SID", "HIT_URL", "INDIVIDUAL_PARTY_KEY", "ORDER_ID", "_LOADED_AT")
    (
        select "HIT_SOURCE", "HIT_AT", "MARKETING_CLOUD_VISITOR_ID", "VISIT_ID", "HIT_ID", "HIT_SID", "HIT_URL", "INDIVIDUAL_PARTY_KEY", "ORDER_ID", "_LOADED_AT"
        from _dev_analytics.adobe_experience__astaus.hits__dbt_tmp
    );
    commit;