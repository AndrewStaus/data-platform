{{
    config(
        schema = "exchange_rate",
        alias = "rate",
        materialized = 'view'
    )
-}}

with
cad as (
    select * from {{ source("exchange_rate", "cad") }}
),

usd as (
    select * from {{ source("exchange_rate", "usd") }}
),

unioned as (
    select * from cad
    union all by name
    select * from usd
),

renamed as (
    select
        date          exhange_date_utc,
        max(cad__usd) cad_usd,
        max(cad__eur) cad_eur,
        max(usd__cad) usd_cad,
        max({{- dlt_loaded_at() }}) _loaded_at --noqa:all
    from unioned
    group by exhange_date_utc
)

select * from renamed
