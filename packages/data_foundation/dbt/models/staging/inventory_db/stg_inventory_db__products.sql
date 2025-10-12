{{-
    config(
        schema = "inventory_db",
        alias = "products",
        materialized = "view",
        meta = {
            "dagster": {
              "automation_condition": "eager",
              "freshness_check": {"lower_bound_delta_seconds": 129600}
            }
        }
      )
-}}

with products as (
    select * from {{ source("inventory_db", "products") }}
)

select
    id    product_id,
    name  product_name,
    brand brand_name,
    {{ pst_to_utc("updated_at") }} updated_at --noqa:all
from products
