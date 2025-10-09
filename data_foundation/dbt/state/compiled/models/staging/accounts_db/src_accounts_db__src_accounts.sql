

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