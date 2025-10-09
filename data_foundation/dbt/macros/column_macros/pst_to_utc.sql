{% macro pst_to_utc(column_name) -%}

    convert_timezone('America/Vancouver', 'UTC', {{ column_name }} :: timestamp)

{%- endmacro %}
