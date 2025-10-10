{#-
Applys a dynamic mask to columns listed.

Add a post hook to the model config, and masking rules will be applied to
columns.

    post_hook = "{{ apply_dynamic_data_mask(
        columns = [
            'account_first_name',
            'account_last_name',
            'account_email',
        ]
    )}}",

Unmasking can be granted by role at column, table, schema, and database level:

    {database}__{schema}__{table}__{column_name}__unmasked
    {database}__{schema}__{table}__unmasked
    {database}__{schema}__unmasked
    {database}__unmasked

Support for text and numeric type columns.
-#}

{%- macro apply_dynamic_data_mask(columns) -%}
    {% if execute %}
        {%- set database = this.database -%}
        {%- set schema = this.schema -%}
        {%- set table = this.table -%}

        {%- set relation = load_relation(this) -%}
        {%- set table_type = "view" if relation.is_view else "table" -%}

        {%- set table_columns = adapter.get_columns_in_relation(relation) -%}

        {% for column_name in columns -%}
            {%- for column in table_columns -%}
                {%- if column.name | upper == column_name | upper -%}
                    {% set create_mask %}
                        create masking policy if not exists {{ database }}.{{ schema }}.{{ table }}__{{ column_name }}__mask
                        as (val {{ column.dtype }}) returns {{ column.dtype }} ->
                            case
                                when lower(current_role()) in ('service_account')
                                then val

                                when array_contains(
                                    upper('{{ database }}__{{ schema }}__{{ table }}__{{ column_name }}__unmasked'),
                                    parse_json(current_available_roles())::array(varchar)
                                )
                                then val

                                when array_contains(
                                    upper('{{ database }}__{{ schema }}__{{ table }}__unmasked'),
                                    parse_json(current_available_roles())::array(varchar)
                                )
                                then val

                                when array_contains(
                                    upper('{{ database }}__{{ schema }}__unmasked'),
                                    parse_json(current_available_roles())::array(varchar)
                                )
                                then val

                                when array_contains(
                                    '{{ database }}__unmasked',
                                    parse_json(current_available_roles())::array(varchar)
                                )
                                then val
                                
                                else
                                {% if column.is_string() -%}
                                    md5(val)
                                {%- elif column.is_number() -%}
                                    0
                                {%- endif %}
                            end
comment='Applies to {{ database }}.{{ schema }}.{{ table }}.{{ column_name }}
Unmasking can be applied by granting role:
    database: {{ database }}__unmasked
    schema:   {{ database }}__{{ schema }}__unmasked
    table:    {{ database }}__{{ schema }}__{{ table }}__unmasked
    column:   {{ database }}__{{ schema }}__{{ table }}__{{ column_name }}__unmasked'
;
                    {% endset %}
                    {% set apply_mask %}
                        alter {{ table_type }} if exists {{ database }}.{{ schema }}.{{ table }}
                        modify column {{ column_name }} set masking policy {{ database }}.{{ schema }}.{{ table }}__{{ column_name }}__mask
                        ;
                    {% endset %}

                    {% do run_query(create_mask) %}
                    {% do run_query(apply_mask) %}

                    {%- set msg -%}
                        Dynamic mask applied to: '{{ column_name }}'
                    {%- endset -%}
                    {{ log(msg, True) }}
                {%- endif -%}
            {%- endfor -%}
        {% endfor %}
    {% endif %}
{%- endmacro -%}
