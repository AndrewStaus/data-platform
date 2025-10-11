{{
  config(
    schema = "accounts_db",
    alias = "test",
    materialized = "view",
    )
-}}

with test as (
    select * from {{ ref('stg_accounts_db__accounts') }}
)

select * from tests
