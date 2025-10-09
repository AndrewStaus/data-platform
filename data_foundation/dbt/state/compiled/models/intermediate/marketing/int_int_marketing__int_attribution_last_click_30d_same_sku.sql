with
    attribution as (
        select * from analytics.int_marketing.int_attributions
    ),
    transactions as (
        select * from analytics.transaction_db.transactions
    ),
    individual_party_keys as (
        select * from analytics.entity_resolution.individual_party_keys
    ),
    products as (
            select * from analytics.inventory_db.products
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
            ['product_id'] criteria,
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
        inner join products ap on a.advertised_product_id = ap.product_id
            inner join products tp on t.product_id = tp.product_id
        where true
            and ap.product_id = tp.product_id
                
        qualify t.transacted_at < attribution_end_at
    )

    select
        *
    from attributed
    qualify 1 = row_number() over (partition by attribution_sid order by attribution_start_at desc)

--noqa:all