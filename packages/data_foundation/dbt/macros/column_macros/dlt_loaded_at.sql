{% macro dlt_loaded_at(col="_dlt_load_id") -%}
    to_timestamp(split({{ col }}, '.')[0])
{%- endmacro %}
