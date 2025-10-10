{% macro apply_privacy_rules(apply_mask=True, delete_interval=None, anonymize_interval=None, reference_date_column=None, pii_columns=[], ) %}

    {% if apply_mask %}
        {% do apply_dynamic_data_mask(pii_columns) %}
    {% endif %}

    {% if delete_interval %}
        {% do delete_historical(
            reference_date_column,
            delete_interval
        ) %}
    {% endif %}

    {% if anonymize_interval %}
        {% do anonymize_historical(
            reference_date_column,
            anonymize_interval,
            pii_columns
        ) %}
    {% endif %}

{% endmacro %}