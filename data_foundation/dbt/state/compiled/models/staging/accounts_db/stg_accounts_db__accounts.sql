with __dbt__cte__src_accounts_db__src_accounts as (


with accounts as (
    select * from raw.accounts_db.accounts
)

select
    id                      account_id,
    trim(lower(first_name)) account_first_name,
    trim(lower(last_name))  account_last_name,
    trim(lower(email))      account_email,
    party_key               indvidual_party_key,
    convert_timezone('America/Vancouver', 'UTC', updated_at :: timestamp) updated_at, -- noqa: all
    _sling_loaded_at        _loaded_at
from accounts
)

select * from (


with accounts as (
    select * from __dbt__cte__src_accounts_db__src_accounts
)

select
    account_id,
    sha2(account_first_name, 256) account_first_name,
    sha2(account_last_name, 256)  account_last_name,
    sha2(account_email, 256)      account_email,
    indvidual_party_key,
    _loaded_at
from accounts


)