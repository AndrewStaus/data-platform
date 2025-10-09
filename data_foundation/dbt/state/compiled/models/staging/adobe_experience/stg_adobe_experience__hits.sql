with
web_hits as (
    select * from raw.adobe_experience.web_hits
),

app_hits as (
    select * from raw.adobe_experience.app_hits
),

accounts as (
    select * from raw.accounts_db.accounts
),

united_hits as (
    select
        *,
        'web' hit_source
    from web_hits

    union all

    select
        *,
        'app' hit_source
    from app_hits
)

select
    h.hit_source,
    convert_timezone('America/Vancouver', 'UTC', date_time :: timestamp) hit_at, --noqa:all
    h.mcvisid                                           marketing_cloud_visitor_id,
    concat_ws(':', h.post_visid_high, h.post_visid_low) visit_id,
    concat_ws(':', visit_id, h.hitid_high, h.hitid_low) hit_id,
    concat_ws(':', h.hit_source, hit_id)                hit_sid,
    h.page_url                                          hit_url,
    a.party_key                                         individual_party_key,
    h.orderid                                           order_id,
    h._sling_loaded_at                                  _loaded_at
from united_hits h
left join accounts a on h.post_evar133 = a.id

