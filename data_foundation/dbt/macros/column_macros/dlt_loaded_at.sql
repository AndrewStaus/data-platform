{% macro dlt_loaded_at() -%}
    to_timestamp(split(_dlt_load_id, '.')[0])
{%- endmacro %}
