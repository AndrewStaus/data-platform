{% macro normalize(column_name) -%}

    lower(trim({{ column_name }} :: string))

{%- endmacro %}

{% macro norm_hash(column_name) -%}

    (sha2({{ normalize(column_name) }}, 256))

{%- endmacro %}