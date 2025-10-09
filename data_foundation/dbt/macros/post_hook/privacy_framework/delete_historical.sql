{%- macro delete_historical(reference_date_column, retention_interval) %}
    {# Delete records older than the retention interval,
    and log results to privacy log
    #}

    {% if execute %}

        {% set delete_dml %}
            delete from {{ this }}
            where {{ reference_date_column }} <= 
                current_timestamp() - interval '{{ retention_interval }}'
        {% endset %}

        {% set affected_rows = run_query(delete_dml)[0][0] %}
        
        {% do _log_privacy_operation(
            "delete", reference_date_column,
            retention_interval, affected_rows, columns
        ) %}

    {% endif %}
{%- endmacro %}