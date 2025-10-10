
  
    

        create or replace transient table _dev_analytics.int_marketing__astaus.int_attributions_last_click_30d
         as
        (with
    attribution as (
        select * from _dev_analytics.int_marketing__astaus.int_attributions
    ),
    transactions as (
        select * from _dev_analytics.transaction_db__astaus.transactions
    ),
    individual_party_keys as (
        select * from _dev_analytics.entity_resolution__astaus.individual_party_keys
    ),
    

    transactions_with_entity as (
        select
            t.transaction_id,
            t.product_id,
            t.sales_channel,
            t.transacted_at,
            t.individual_party_key,
            i.individual_id,
            t._loaded_at
        from transactions t
        inner join individual_party_keys i on t.individual_party_key = i.individual_party_key
        
    ),

    attributed as (
        select
            (sha2(concat_ws(':', nvl(t.product_id:: string, ''), nvl(t.transacted_at:: string, ''), nvl(t.transaction_id:: string, '')),256)) attribution_sid,
            30 lookback_window,
            [] criteria,
            a.hit_id,
            i.individual_id,
            a.campaign_sid,
            t.transaction_id,
            a.advertised_product_id,
            t.product_id transacted_product_id,
            t.sales_channel,
            t.transacted_at,
            a.attribution_start_at,
            coalesce(
                lag(a.attribution_start_at) over (
                    partition by i.individual_id
                    order by a.attribution_start_at, a.hit_id
                ),
                a.attribution_start_at + interval '30 days'
            ) attribution_end_at,
            t._loaded_at
        from attribution a
        inner join individual_party_keys i on a.individual_party_key = i.individual_party_key
        inner join transactions_with_entity t on true
            and i.individual_id = t.individual_id
            and t.transacted_at >= a.attribution_start_at
        
        where true
            
        qualify t.transacted_at < attribution_end_at
    )

    select
        *
    from attributed
    qualify 1 = row_number() over (partition by attribution_sid order by attribution_start_at desc)

--noqa:all
        );
      
  