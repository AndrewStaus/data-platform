select validation_errors.* from (
    select
        pk_test.account_id, count(*) as n_records
    from analytics.accounts_db.accounts_pii pk_test
    group by pk_test.account_id
    having count(*) > 1
        or pk_test.account_id is null
        
) validation_errors