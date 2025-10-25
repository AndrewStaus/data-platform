# dbt

## Overview

The **dbt (data build tool)** project defines the transformation layer of the data platform.  
It converts raw, ingested data from **Sling** and **dltHub** into clean, analytics-ready datasets for reporting, machine learning, and monitoring.  

All transformation logic, tests, and documentation live within the dbt project located at:

```
packages/data_foundation/dbt/
```

dbt integrates tightly with **Dagster**, which orchestrates model runs, manages dependencies, and exposes metadata like freshness and test results in the Dagster UI.

---

## Project Structure

The dbt project follows a modular, maintainable layout designed for transparency and scalability.

### `dbt_project.yml` and `profiles.yml`

??? example "dbt_project.yml"
    ```yaml
    name: data_foundation
    version: 1.0
    profile: data_foundation
    models:
      +materialized: table
      staging:
        +schema: staging
      marts:
        +schema: marts
    ```

- **`dbt_project.yml`** defines project-level configuration such as naming conventions, materializations (e.g., table, view, incremental), and model directories.  
- **`profiles.yml`** specifies connection profiles for different environments (e.g., dev, staging, prod), including **Snowflake credentials** and warehouse configurations.

Inline comments document how these settings link dbt’s runtime behavior with Dagster’s orchestration layer.  
Dagster triggers dbt commands (e.g., `dbt build`, `dbt run`) using these configurations to ensure consistency across environments.

---

### `models/`

??? example " Models are organized by layer and by domain"

    ```
    models/
    ├── staging/
    │   ├── accounts_db/
    │   │   ├── _sources.yml
    │   │   ├── stg_accounts_db__accounts.sql
    │   │   └── stg_accounts_db__accounts.yml
    │   ├── facebook_ads/
    │   └── transaction_db/
    │
    ├── intermediate/
    │   ├── marketing/
    │   │   ├── int_marketing__campaign_performance.sql
    │   │   └── int_marketing__campaign_performance.yml
    │
    └── marts/
        ├── common/
        │   ├── fct_common__fct_transactions.sql
        │   └── fct_common__fct_transactions.yml
        └── marketing/
            ├── dim_marketing__dim_campaigns.sql
            └── fct_marketing__fct_attributions.sql
    ```

The **`models/`** directory contains all SQL transformations and their associated metadata.

Each SQL model:
- References **raw** data from Sling or dltHub via `{{ source('raw', 'table_name') }}`  
- Applies business logic to clean, standardize, or aggregate data  
- Has a companion `.yml` file documenting columns, tests, and freshness expectations  

Dagster automatically detects these models and surfaces them as **assets** in the data graph, showing full lineage from ingestion → staging → marts.

---

### `snapshots/`

??? example "snapshot.yaml"
    ```yaml
    snapshots:
    - name: snp_accounts_db__accounts
      relation: source('accounts_db', 'accounts')
      config:
        database: snapshots
        schema: accounts_db
        alias: accounts
        unique_key: [id]
        strategy: timestamp
        updated_at: updated_at
        dbt_valid_to_current: "to_date('9999-12-31')"
        snapshot_meta_column_names: {
          "dbt_valid_from": "_valid_from",
          "dbt_valid_to": "_valid_to",
          "dbt_scd_id": "_scd_id",
          "dbt_updated_at": "_updated_at",
          "dbt_is_deleted": "_is_deleted"
        }
        post_hook: [
          "{{ apply_privacy_rules(
            delete_interval='10 years',
            anonymize_interval='5 years',
            reference_date_column='updated_at',
            pii_columns=[
              'first_name',
              'last_name',
              'email',
            ]
          ) }}"
        ]
    ```

The **`snapshots/`** directory preserves **slowly changing dimensions (SCDs)** and historical states of records.  
These snapshots ensure the platform can perform time-based analyses and maintain data integrity across updates.

Inline comments describe:
- Retention policies for long-term storage  
- How snapshots handle **PII or sensitive fields**  
- The linkage between dbt snapshots and Dagster’s versioned asset tracking

---

### `seeds/`

??? example "Example Seed"
    ```
    seeds/
     ├── currency_codes.csv
     └── currency_codes.yml
    ```

The **`seeds/`** folder contains CSV-backed reference datasets — small, static tables loaded directly into the warehouse.

Examples:
- Country or currency lookup tables  
- Product taxonomies  
- Default configuration values for analytics logic  

Each seed is paired with a YAML file for column descriptions and tests, ensuring consistent governance.

---

### `groups/`

??? example "group.yaml"
    ```yaml
    version: 2

    groups:
    - name: marketing
        owner:
            name: Marketing Analytics
            email: analytics@company.com
    ```

The **`groups/`** directory defines **ownership and governance metadata** for models.  
Each group associates dbt assets with the teams responsible for maintenance, ensuring alert routing, documentation ownership, and access control are properly enforced.

These definitions allow **Dagster and dbt** to coordinate responsibility for assets and automate alerting or approvals by team.

---

### `macros/`

??? example "macro.sql"
    ```jinja
    {% macro safe_cast(column, data_type) %}
        case
            when {{ column }} is null then null
            else cast({{ column }} as {{ data_type }})
        end
    {% endmacro %}
    ```

The **`macros/`** folder defines **shared SQL logic** — reusable snippets that act like user-defined functions (UDFs).  
They allow complex transformations, date handling, and cross-model consistency to be defined in one place and reused across the project.

Common examples include:
- Generic key hashing functions  
- Conditional logic for incremental updates  
- Data quality or freshness checks  

---

### `packages.yml`

??? example "packages.yml"
    ```yaml
    packages:
    - package: dbt-labs/dbt_utils
        version: 1.1.1
    - package: calogica/dbt_expectations
        version: [">=0.7.0", "<0.8.0"]
    ```

The **`packages.yml`** file lists **third-party dbt packages** that extend project functionality.  
These packages provide pre-built macros and tests for common analytics patterns.

Commonly included packages:
- **dbt_utils** – essential generic tests and macros  
- **dbt_expectations** – advanced data validation  
- **dbt_artifacts** – metadata extraction for observability  

---

## Integration with Dagster and Snowflake

Dagster acts as the **orchestration and observability layer** for dbt:
- **Triggers** dbt runs (e.g., `dbt build`, `dbt test`) as part of daily pipelines  
- **Monitors** model dependencies and freshness  
- **Surfaces** lineage from **Sling/dltHub → dbt staging → marts → dashboards**

Snowflake serves as the **underlying data warehouse**, hosting raw, staging, snapshot, and mart schemas.  
dbt defines the **SQL logic and transformations**, while Dagster ensures those transformations are executed reliably and on schedule.

---

✅ **Summary**

| Directory | Purpose |
| ---------- | -------- |
| `dbt_project.yml`, `profiles.yml` | Project configuration and environment connections |
| `models/` | SQL transformations and metadata for staging, intermediate, and marts |
| `snapshots/` | Time-travel and historical data preservation |
| `seeds/` | Static reference data managed as CSVs |
| `groups/` | Ownership and governance definitions |
| `macros/` | Reusable SQL logic and helper functions |
| `packages.yml` | External macro and testing libraries |

---

**In short:**  
dbt is the transformation backbone of the platform.  
It turns the raw data ingested by **Sling** and **dltHub** into trusted, documented, and testable datasets — all orchestrated and observed through **Dagster**.
