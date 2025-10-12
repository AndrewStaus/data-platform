{% macro attribution_last_click_n_days_same_x(lookback_window, criteria=[]) -%}

    with
    attribution as (
        select * from {{ ref("int_int_marketing__int_attributions") }}
    ),
    transactions as (
        select * from {{ ref("stg_transaction_db__transactions") }}
    ),
    individual_party_keys as (
        select * from {{ ref("stg_entity_resolution__individual_party_keys") }}
    ),
    {% if criteria -%}
        products as (
            select * from {{ ref("stg_inventory_db__products") }}
        ),
    {%- endif %}

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
        {% if is_incremental() -%}
            where t._loaded_at >= (select max(_loaded_at) from {{ this }})
        {%- endif %}
    ),

    attributed as (
        select
            {{ generate_sid(["t.transaction_id", "t.product_id", "t.transacted_at"]) }} attribution_sid,
            {{ lookback_window }} lookback_window,
            {{ criteria }} criteria,
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
                a.attribution_start_at + interval {{ "'n days'" | replace("n", lookback_window) }}
            ) attribution_end_at,
            t._loaded_at
        from attribution a
        inner join individual_party_keys i on a.individual_party_key = i.individual_party_key
        inner join transactions_with_entity t on true
            and i.individual_id = t.individual_id
            and t.transacted_at >= a.attribution_start_at
        {% if criteria -%}
            inner join products ap on a.advertised_product_id = ap.product_id
            inner join products tp on t.product_id = tp.product_id
        {%- endif %}
        where true
            {% if criteria -%}
                {%- for criterion in criteria -%}
                        and ap.{{- criterion }} = tp.{{- criterion }}
                {% endfor -%}
            {%- endif -%}
        {%- if is_incremental() %}
            and a._loaded_at >= (select max(_loaded_at) - interval {{ "'n days'" | replace("n", lookback_window) }} from {{ this }})
        {% endif %}
        qualify t.transacted_at < attribution_end_at
    )

    select
        *
    from attributed
    qualify 1 = row_number() over (partition by attribution_sid order by attribution_start_at desc)

{% endmacro %}