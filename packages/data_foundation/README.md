# data_foundation/

Foundational data assets that are used across the business.  Contains data extract and 
load logic, as well as the main dbt project for data transformation.

## Contents

- `dbt`: dbt project containing models, seeds, snapshots, and tests. YAML files document
sources, staging models, and marts.
- `src/data_foundation`: Dagster definitions, resource configuration, and integration
glue code. Includes Sling source connection YAML that controls raw data ingestion

## Usage

### Ingestion (dltHub, Sling)
dltHub and Sling ingestion's are defined in their respective folders
    - .../src/data_foundation/defs/dlthub/dlthub/
    - .../src/data_foundation/defs/sling/sling/
All other code in the /src/ folder is for Dagster factories to automatically consume the
configurations in these spaces.

#### Sling
Sling replication configurations are yaml files that define what tables should be
ingested, the load pattern, and the frequency.

#### dltHub
dltHub is a python library that provides a wrapper for a python generator function.
It allows for ingestion of any data that can be described in a python object:
    - DataFrames: Pandas, Avro, Ork  
    - Python Objects: Lists of Lists, Lists of Dicts
It's primary use case if for data that is semi-structured, or from a source that can not
be otherwise ingested through Sling.  It allows for configuration of load patterns,
normalization, and frequency.

### Transformation (dbt)
dbt models are defined in the dbt folder using standard practices. An additional config
section is provided to control automation and SLA checks in Dagster:
    ```json
    meta = {
        "dagster": {
            "automation_condition": "eager",
            "freshness_check": {"lower_bound_delta_seconds": 129600}
        }
    }
    ```
Details on specific automation_conditions can be found on the
(documentation site)[https://andrewstaus.github.io/data-platform/modules/libs/data_platform_utils/automation_conditions/]
    
(Deferral)[https://docs.getdbt.com/docs/cloud/about-cloud-develop-defer] is enabled so
that each developer can test their models against production data that they have access
to in an temporary isolated environment that no one else has access to.  This ensures
data governance is respected, while also providing rapid feedback loops on code
development.