{{-
    config(
        schema = "int_marketing",
        alias = "int_attributions_last_click_30d_same_sku",
        materialized="incremental",
        incremental_strategy="delete+insert",
        unique_key="attribution_sid"
    )
-}}

{{- attribution_last_click_n_days_same_x("30", ["product_id"]) -}} --noqa:all
