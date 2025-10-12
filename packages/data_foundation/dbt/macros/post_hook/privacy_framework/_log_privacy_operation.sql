{% macro _log_privacy_operation(operation, reference_date_column, retention_interval, affected_rows, columns=[]) %}
        {% set privacy_log_fqn = _get_privacy_log() %}
        {% set log_dml %}
            insert into {{ privacy_log_fqn }} (
                operation, fqn, database_name, schema_name, table_name,
                reference_date_column, anonymized_columns, retention_interval,
                affected_rows
            )
            select
                '{{ operation }}',
                '{{ this }}',
                '{{ this.database }}',
                '{{ this.schema }}',
                '{{ this.table }}',
                '{{ reference_date_column }}',
                {{ columns|string }},
                '{{ retention_interval }}',
                {{ affected_rows }}
            ;
        {% endset %}
        {% do run_query(log_dml) %}

        {%- set msg -%}
            {{ operation|capitalize }} historical operation logged to: '{{ privacy_log_fqn }}'
        {%- endset -%}
        {{ log(msg, True) }}

{% endmacro %}

{% macro _get_privacy_log() %}
    {% set schema_fqn = this.database~"."~generate_schema_name("logs") %}
    {% set privacy_log_fqn = schema_fqn~".privacy_log" %}

    {% set create_schema %}
        create schema if not exists {{ schema_fqn }};
    {% endset %}

    {% set create_table %}
        create table if not exists {{ privacy_log_fqn }}(
            id int identity(1,1),
            operation varchar,
            fqn varchar,
            database_name varchar,
            schema_name varchar,
            table_name varchar,
            reference_date_column varchar,
            anonymized_columns array,
            retention_interval varchar,
            affected_rows int,
            applied_at timestamp_ntz default current_timestamp()
        )
        ;
    {% endset %}

    {% do run_query(create_schema) %}
    {% do run_query(create_table) %}

    {% do return(privacy_log_fqn) %}

{% endmacro %}
