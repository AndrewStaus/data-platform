# data_foundation/

Foundational data assets that are used across the business.  Contains ingestions and the
main dbt project.

## Contents

- `dbt`: dbt project containing models, seeds, snapshots, and tests. YAML files document
sources, staging models, and marts.
- `src/data_foundation`: Dagster definitions, resource configuration, and integration
glue code. Includes Sling source connection YAML that controls raw data ingestion

## Usage
