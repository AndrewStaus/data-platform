with transactions as (
    select * from raw.transaction_db.transactions
)

select
    order_id::int                           transaction_id,
    product_id::varchar(10)                 product_id,
    channel::varchar(25)                    sales_channel,
    party_key::varchar(25)                  individual_party_key,
    round(revenue / 100, 2)::decimal(16, 2) transaction_revenue,
    round(margin / 100, 2)::decimal(16, 2)  transaction_margin,
    convert_timezone('America/Vancouver', 'UTC', date_time :: timestamp)          transacted_at, --noqa:all
    _sling_loaded_at::timestamp             _loaded_at
from transactions

