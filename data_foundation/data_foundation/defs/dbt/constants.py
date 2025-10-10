"""Constant values that are useful in selecting dbt models."""

# partition selectors
TIME_PARTITION_SELECTOR = "config.tags:partitioned"


# resource type selectors
SNAPSHOT_SELECTOR = "resource_type:snapshot"
MODEL_SELECTOR = "resource_type:model"
SEED_SELECTOR = "resource_type:seed"
