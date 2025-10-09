"""Constant values that are useful in selecting dbt models."""

# partition selectors
# HOURLY_PARTITION_SELECTOR = "config.meta.dagster.partition:hourly"
# DAILY_PARTITION_SELECTOR = "config.meta.dagster.partition:daily"
# WEEKLY_PARTITION_SELECTOR = "config.meta.dagster.partition:weekly"
# MONTHLY_PARTITION_SELECTOR = "config.meta.dagster.partition:monthly"

# TIME_PARTITION_SELECTOR = " ".join(
#     [
#         HOURLY_PARTITION_SELECTOR,
#         DAILY_PARTITION_SELECTOR,
#         WEEKLY_PARTITION_SELECTOR,
#         MONTHLY_PARTITION_SELECTOR,
#     ]
# )

TIME_PARTITION_SELECTOR = "config.tags:partitioned"


# resource type selectors
SNAPSHOT_SELECTOR = "resource_type:snapshot"
MODEL_SELECTOR = "resource_type:model"
SEED_SELECTOR = "resource_type:seed"
