{%- set union_table_prefix = "int_int_marketing__int_attribution_last_click" -%}
{%- set union_table_postfixes = [
    "_30d",
    "_30d_same_brand",
    "_30d_same_sku",
] -%}
{{-
    config(
        schema = "marketing",
        alias = "fct_attributions",
        materialized = "view",
        meta = {
            "dagster": {
                "automation_condition": "on_cron",
                "automation_condition_config": {
                    "cron_schedule":"@daily",
                    "cron_timezone":"utc"
                },
                "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        },
        tags = ["pii"]
    )
-}}

{% for postfix in union_table_postfixes -%}
    {% if not loop.first %}
        union all
    {% endif -%}
    select * from {{ ref(union_table_prefix ~ postfix) }}

{%- endfor %}
