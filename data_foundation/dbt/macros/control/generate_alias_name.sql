{%- macro generate_alias_name(custom_alias_name=none, node=none) -%}
    {%- if custom_alias_name -%}
        {{- custom_alias_name | trim -}}
    {%- else -%}
        {{- return(node.name.split('__', maxsplit=1)[-1]) -}}
    {%- endif -%}
{%- endmacro -%}
