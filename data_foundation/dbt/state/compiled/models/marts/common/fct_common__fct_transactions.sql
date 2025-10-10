with transactions as (
    select * from analytics.transaction_db.transactions
)

select * from transactions