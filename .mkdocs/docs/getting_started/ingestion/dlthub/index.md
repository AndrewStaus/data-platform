# ![dltHub](../../../assets/images/dlt/0_logo.png){ width="250" }

## Overview

The **dltHub** package provides the ingestion layer of the data platform.  
It connects to external APIs, public datasets, and ad platforms, and efficiently loads them into the **Snowflake raw database** — the foundation for all downstream transformations in **dbt**.

Each dltHub connector defines a lightweight configuration and generator pattern that enables flexible ingestion pipelines with minimal code.  
**Dagster** orchestrates these connectors, managing execution schedules, dependencies, and data lineage.

---

## Directory Structure

The dltHub project resides under:

```
packages/data_foundation/dlthub/
```

Each subdirectory represents a distinct data source or integration, such as **Facebook Ads**, **Google Ads**, **Exchange Rate APIs**, or **Open Data feeds**.


???+ quote "layout"
      ``` text
      dlthub/
      ├── source_name/
      │   ├── __init__.py
      │   ├── data.py
      │   └── sources.yaml
      ```

---

## How dltHub Works

Each source directory defines three core components that enable flexible data ingestion:

### 1. `__init__.py`

The `__init__.py` file is an empty file that identifies the folder as a Python module,
allowing Dagster and dltHub to dynamically import resources and pipelines.

---


### 2. Generator
??? example "data.py"

    ```python
    import requests

    def fetch_transactions():
        """Fetch paginated transactions from API"""
        page = 1
        while True:
            response = requests.get(f"https://api.example.com/transactions?page={page}")
            data = response.json()
            if not data:
                break
            yield data
            page += 1
    ```

    !!! tip
        - Always use **`yield`** (not `return`) to stream data in small chunks.  
        - Use API pagination, cursors, or offsets to avoid loading too much data into memory.  
        - Each yield should return a list (or iterable) of records, e.g. `[{...}, {...}, ...]`.

The **data generator** defines *how* data is fetched.  
It can yield any iterable of dictionaries (records).  
dltHub automatically batches and streams data to the destination.

The **`data.py`** script defines the **data generator** — a Python function that yields data in batches.  
Each yield represents a page or chunk of records fetched from the source system (API, file, or database).

This generator pattern allows dltHub to:
- Stream large datasets efficiently  
- Handle pagination and rate limits  
- Maintain memory efficiency during ingestion  

Ingestion functions can also accept arguments (like date ranges or filters), allowing Dagster to parametrize runs dynamically.

---

### Resources
??? example "sources.yaml"

    ```yaml
    resources:
        my_api.users:
            entry: data.fetch_users
            write_disposition: append
            primary_key: ["id"]
            kinds: {api}

        my_api.transactions:
            entry: data.fetch_transactions
            write_disposition: append
            primary_key: ["id"]
            kinds: {api}
    ```

**Explanation:**
- Each resource maps to a data generator function (defined in `data.py`).
- The resource defines how its data is written to the target system.
- Use multiple resources when extracting from different endpoints or datasets.

Typical fields include:

| Key | Description |
| ---- | ------------ |
| `entry` | The entry path to the generator function, e.g. `exchange_rate.data.get_exchange_rates` |
| `arguments` | Optional positional arguments passed to the function to select a generator |
| `keword_arguments` | Optional keyword arguments passed to the function to select a generator |
| `write_disposition` | Defines whether data is appended, replaced, or merged |

---

### Sources

??? example "sources.yaml"

    ```yaml
    sources:
        my_api:
            resources:
            - my_api.users
            - my_api.transactions
            meta:
                dagster:
                    automation_condition: on_schedule
                    automation_condition_config:
                        cron_schedule: "@daily"
                        cron_timezone: utc
                    freshness_lower_bound_delta_seconds: 108000
    ```

**Explanation:**
- The `sources` block declares a data source (e.g., an API, database, or file store).
- Each source can contain one or more **resources**, representing individual endpoints or tables.
- Grouping them provides modularity and reuse for replication definitions.

---

## Governance and Observability

All dltHub connectors include:
- **Inline docstrings** describing source purpose and ownership  
- **YAML metadata** for consistent data lineage and auditability  
- **Automatic asset mapping** into Dagster’s lineage graph  

This ensures every dataset — from an external API to the final mart — is fully traceable across ingestion, transformation, and consumption.
