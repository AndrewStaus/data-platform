with individual_party_keys as (
    select * from raw.entity_resolution.individual_party_keys
)

select
    party_key        individual_party_key,
    entity_id        individual_id,
    updated          updated_at,
    _sling_loaded_at _loaded_at
from individual_party_keys

