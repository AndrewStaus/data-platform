{{-
    config(
        schema = "accounts_db",
        alias = "accounts",
        materialized = "incremental",
        unique_key = "account_id",
        incremental_strategy="delete+insert",
        meta = {
            "dagster": {
                "automation_condition": "eager",
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        },
        post_hook = ["{{
            apply_privacy_rules(
                apply_mask=True,
                delete_interval='10 years',
                anonymize_interval='5 years',
                reference_date_column='updated_at',
                pii_columns=[
                    'account_first_name',
                    'account_last_name',
                    'account_email',
                ]
            )
        }}"]
    )
-}}

with accounts as (
    select * from {{ source("accounts_db", "accounts") }}
)

select
    id                      account_id,
    trim(lower(first_name)) account_first_name,
    trim(lower(last_name))  account_last_name,
    trim(lower(email))      account_email,
    party_key               individual_party_key,
    {{ pst_to_utc("updated_at") }} updated_at, -- noqa:TMP
    _sling_loaded_at        _loaded_at
from accounts
