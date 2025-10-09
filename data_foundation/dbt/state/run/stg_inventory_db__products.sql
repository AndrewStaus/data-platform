
  create or replace   view _dev_analytics.inventory_db__astaus.products
  
    
    
(
  
    "PRODUCT_ID" COMMENT $$$$, 
  
    "PRODUCT_NAME" COMMENT $$$$, 
  
    "BRAND_NAME" COMMENT $$$$, 
  
    "UPDATED_AT" COMMENT $$$$
  
)

   as (
    with products as (
    select * from raw.inventory_db.products
)

select
    id    product_id,
    name  product_name,
    brand brand_name,
    convert_timezone('America/Vancouver', 'UTC', updated_at :: timestamp) updated_at --noqa:all
from products
  );

