{{-
    config(
        schema = "int_marketing",
        alias = "int_attributions_last_click_30d",
        materialized="incremental",
        incremental_strategy="delete+insert",
        unique_key="attribution_sid"
    )
-}}

{{- attribution_last_click_n_days_same_x("30") -}} --noqa:all
