{%- macro generate_schema_name(custom_schema_name=none, node=none) -%}
    {%- if custom_schema_name is none -%}

        {%- set prefix = node.name.split("__", maxsplit=1)[0] -%}
        {%- set schema_name = prefix.split("_", maxsplit=1)[-1] -%}

    {%- else -%}

        {%- set schema_name = custom_schema_name -%}

    {%- endif -%}
    
    {%- set schema_name = schema_name | trim -%}
    {%- if target.name == "dev" -%}

        {{- schema_name -}}__{{- target.user -}}

    {%- else -%}

        {{- schema_name -}}
        
    {%- endif -%}
{%- endmacro -%}
