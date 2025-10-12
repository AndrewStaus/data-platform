{% macro generate_sid(column_names) -%}

    (sha2(concat_ws(':'
        {%- for column_name in column_names | sort() -%}
            , nvl({{ column_name -}} :: string, '')
        {%- endfor -%}
        ),256))

{%- endmacro %}
