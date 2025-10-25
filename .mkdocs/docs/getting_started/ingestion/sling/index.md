# Sling

## Overview

**Sling** is the **data replication and movement layer** of the platform.  
It extracts data from databases, APIs, and file systems, and loads it into **Snowflake’s `raw` layer**, where it becomes available for transformation in **dbt**.

Each Sling configuration defines a source–target relationship and the rules governing replication, schema management, and incremental updates.  
**Dagster** orchestrates Sling, handling execution scheduling, monitoring, and automatic lineage tracking between upstream sources and downstream dbt models.

---

## Directory Structure

The Sling project resides under:

```
packages/data_foundation/sling/
```

Each subdirectory represents a **data system** (database or API) being replicated into Snowflake.

```
sling/
 ├── accounts_db/
 │   ├── connections.yaml
 │   └── replication.yaml
 │
 ├── adobe_experience/
 │   ├── connections.yaml
 │   └── replication.yaml
 │
 ├── entity_resolution/
 │   ├── connections.yaml
 │   └── replication.yaml
 │
 ├── inventory_db/
 │   ├── connections.yaml
 │   └── replication.yaml
 │
 ├── my_database/
 ├── snowflake/
 └── transaction_db/
```

Each folder contains **two key files** that define how Sling interacts with the source system.

---

## How Sling Works

Sling configurations are written in YAML and follow a consistent two-file pattern:

### 1. `connections.yaml`

Defines **connection details** for both source and target systems.  
This includes hostnames, credentials, database names, and authentication methods.

Example:

```yaml
connections:
  accounts_db:
    type: postgres
    database: env.SOURCE__ACCOUNTS_DB
    host: env.SOURCE__ACCOUNTS_HOST
    port: secret.SOURCE__ACCOUNTS_PORT
    user: secret.SOURCE__ACCOUNTS_USER
    password: secret.SOURCE__ACCOUNTS_PASSWORD
```

**Key features:**
- **`env.`** values are resolved from environment variables in Dagster and displayed as plaintext.
- **`secret.`** values are securely fetched from the key vault at runtime and masked in the Dagster UI.
- Supports multiple sources or destinations within a single configuration.
- Typically, the **destination** is always Snowflake, while sources vary by domain.

---

### 2. `replication.yaml`

Defines **replication jobs**, describing how data flows from a source to a destination.  
Each job specifies the source connection, target connection, replication mode, and table mappings.

Example:

```yaml
replications:
  - name: accounts_db->snowflake
    source: accounts_db
    target: snowflake
    defaults:
      mode: incremental
      object: '{stream_schema_upper}.{stream_table_upper}'
      primary_key: ["id"]
      update_key: updated_at
      target_options:
        column_casing: snake
        add_new_columns: true
        adjust_column_type: true
    streams:
      public.customers:
        tags: ["contains_pii"]
      public.transactions:
        primary_key: ["transaction_id"]
```

**Key sections:**
| Section | Description |
| -------- | ------------ |
| `name` | Logical name of the replication (`source->target`) |
| `source` / `target` | Connection names defined in `connections.yaml` |
| `defaults` | Default settings applied to all replicated tables |
| `streams` | List of tables (or files) to replicate and their table-specific overrides |

---

## Integration with Dagster

Each Sling replication job is materialized as a **Dagster asset**, which allows:

- **Automated scheduling** of extract-and-load pipelines  
- **Metadata tracking** — record counts, duration, and run status  
- **Lineage mapping** between raw sources and dbt staging models  
- **Parameterized execution** — e.g., running specific replication sets only

Example Dagster integration:

```python
from dagster import asset
from sling import run_replication

@asset
def accounts_db_raw():
    run_replication(config_path="sling/accounts_db/replication.yaml")
```

When triggered, Dagster reads both `connections.yaml` and `replication.yaml`, resolves credentials, and executes the appropriate extraction and load sequence into Snowflake.

---

## Data Flow Summary

```
Source Systems (Databases / APIs)
   ↓
Sling (connections + replications)
   ↓
Snowflake → schema: raw
   ↓
dbt (staging, intermediate, marts)
   ↓
Dashboards, Analytics, ML
```

Sling serves as the **bridge between operational systems and the analytics warehouse**, ensuring that all downstream transformations begin with a reliable, structured, and up-to-date raw layer.

---

## Adding a New Source

To replicate a new data source:

1. **Create a folder** in `sling/` named after the source system.  
   Example: `sling/crm_system/`

2. **Create the configuration files:**
   - `connections.yaml`
   - `replication.yaml`

3. **Define your connections**:
   ```yaml
   connections:
     crm_system:
       type: mysql
       host: env.CRM_HOST
       user: secret.CRM_USER
       password: secret.CRM_PASSWORD
     snowflake:
       type: snowflake
       account: env.SNOWFLAKE_ACCOUNT
       database: raw
       user: secret.SNOWFLAKE_USER
       password: secret.SNOWFLAKE_PASSWORD
   ```

4. **Define replication behavior**:
   ```yaml
   replications:
     - name: crm_system->snowflake
       source: crm_system
       target: snowflake
       defaults:
         mode: incremental
         primary_key: ["id"]
         update_key: updated_at
       streams:
         crm.contacts:
           add_new_columns: true
   ```

5. **Register the new replication** in Dagster so it appears as a managed asset.

---


✅ **Summary**

| File | Purpose |
| ---- | -------- |
| `connections.yaml` | Defines credentials and connection details for all involved systems |
| `replication.yaml` | Defines replication jobs, defaults, and stream mappings |
| Folder (e.g. `accounts_db/`, `adobe_experience/`) | Represents one system or domain to be replicated |
| Dagster integration | Executes and monitors replications; maps lineage to dbt |

---
