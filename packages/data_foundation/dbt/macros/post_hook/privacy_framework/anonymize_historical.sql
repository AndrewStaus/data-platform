{%- macro anonymize_historical(reference_date_column, retention_interval, columns) %}
    {# Delete the value of columns for records older than the retention interval,
    and log results to privacy log.
    #}

    {% if execute %}
        {% set anonymize_dml %}
            update {{ this }} set
                {% for col in columns %}
                    {{ col }} = Null
                    {%- if not loop.last -%}
                        ,
                    {%- endif -%}
                {%- endfor %}
            where {{ reference_date_column }} <=
                current_timestamp() - interval '{{ retention_interval }}'
            and ( false
                {% for col in columns %}
                    or {{ col }} is not null
                {%- endfor %}
            )
        {% endset %}

        {% set affected_rows = run_query(anonymize_dml)[0][0] %}

        {% do _log_privacy_operation(
            "anonymize",
            reference_date_column,
            retention_interval,
            affected_rows,
            columns
        ) %}

    {% endif %}
{%- endmacro %}