# dltHub

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

```
dlthub/
 ├── exchange_rate/
 │   ├── __init__.py
 │   ├── data.py
 │   └── sources.yaml
 │
 ├── facebook_ads/
 │   ├── __init__.py
 │   ├── data.py
 │   └── sources.yaml
 │
 ├── google_ads/
 │   ├── __init__.py
 │   ├── data.py
 │   └── sources.yaml
 │
 └── open_data/
     ├── __init__.py
     ├── data.py
     └── sources.yaml
```

---

## How dltHub Works

Each source directory defines three core components that enable flexible data ingestion:

### 1. `__init__.py`

The `__init__.py` file identifies the folder as a Python module, allowing Dagster and dltHub to dynamically import resources and pipelines.

It can also define helper functions or constants used across the source, such as authentication tokens, endpoint definitions, or dataset-specific utilities.

---

### 2. `data.py`

The **`data.py`** script defines the **data generator** — a Python function that yields data in batches.  
Each yield represents a page or chunk of records fetched from the source system (API, file, or database).

This generator pattern allows dltHub to:
- Stream large datasets efficiently  
- Handle pagination and rate limits  
- Maintain memory efficiency during ingestion  

Example:

```python
import requests

def get_exchange_rates():
    url = "https://api.exchangerate.host/latest"
    response = requests.get(url)
    data = response.json()

    # Yield in pages or time slices if needed
    yield data["rates"]
```

Ingestion functions can also accept arguments (like date ranges or filters), allowing Dagster to parametrize runs dynamically.

---

### 3. `sources.yaml`

The **`sources.yaml`** file defines the **replication and resource configuration** for dltHub.  
It tells dltHub how to call the generator and where to send the resulting data.

Typical fields include:

| Key | Description |
| ---- | ------------ |
| `entry` | The import path to the generator function, e.g. `exchange_rate.data.get_exchange_rates` |
| `args` | Optional positional arguments passed to the generator |
| `kwargs` | Optional keyword arguments for dynamic parameters (like `start_date`, `end_date`) |
| `destination` | The target dataset or schema in Snowflake (commonly `raw`) |
| `write_disposition` | Defines whether data is appended, replaced, or merged |

Example configuration:

```yaml
resources:
  - entry: exchange_rate.data.get_exchange_rates
    destination: raw.exchange_rate
    write_disposition: replace
```

---

## Integration with Dagster

**Dagster** is responsible for **executing**, **monitoring**, and **documenting** all dltHub pipelines.  

Each dltHub resource is automatically materialized as a **Dagster asset**, allowing you to:
- Schedule ingestion jobs (hourly, daily, weekly)
- Track lineage from **source → raw → dbt staging → marts**
- Visualize dependencies between connectors and downstream dbt models
- Surface metadata such as run duration, success/failure, and record counts

Example Dagster asset definition:

```python
from dagster import asset
from dlthub.exchange_rate.data import get_exchange_rates

@asset
def exchange_rate_raw():
    for batch in get_exchange_rates():
        load_to_snowflake(batch, table="raw.exchange_rate")
```

Dagster uses this integration to ensure each dltHub dataset is up-to-date before dbt transformations begin.

---

## Data Flow Summary

```
External APIs / Feeds
   ↓
dltHub (data generators & configs)
   ↓
Snowflake → schema: raw
   ↓
dbt (staging, intermediate, marts)
   ↓
Analytics, Dashboards, ML
```

Each layer remains **modular and declarative**:
- dltHub handles *extraction and loading*
- dbt handles *transformation and modeling*
- Dagster orchestrates and observes *the entire lifecycle*

---

## Adding a New Source

To create a new dltHub integration:

1. **Create a new folder** under `dlthub/` named after the dataset.  
   Example: `dlthub/github/`
2. **Add three files**:
   - `__init__.py`
   - `data.py`
   - `sources.yaml`
3. **Implement the generator** in `data.py`:
   ```python
   def get_commits(repo):
       url = f"https://api.github.com/repos/{repo}/commits"
       for page in range(1, 10):
           yield requests.get(f"{url}?page={page}").json()
   ```
4. **Configure replication** in `sources.yaml`:
   ```yaml
   resources:
     - entry: github.data.get_commits
       args: ["org/repo"]
       destination: raw.github_commits
       write_disposition: append
   ```
5. **Register the resource** in Dagster to expose it as an asset.

---

## Governance and Observability

All dltHub connectors include:
- **Inline docstrings** describing source purpose and ownership  
- **YAML metadata** for consistent data lineage and auditability  
- **Automatic asset mapping** into Dagster’s lineage graph  

This ensures every dataset — from an external API to the final mart — is fully traceable across ingestion, transformation, and consumption.

---

✅ **Summary**

| Directory | Purpose |
| ---------- | -------- |
| `__init__.py` | Marks the module; defines helper functions or constants |
| `data.py` | Implements the generator that retrieves and yields raw data |
| `sources.yaml` | Defines resource configuration, replication behavior, and destinations |
| Folder (e.g. `exchange_rate/`, `facebook_ads/`) | Represents one external data source |
| Dagster integration | Orchestrates ingestion, monitors runs, and maps lineage |

---

**In short:**  
dltHub is the **ingestion backbone** of the data platform — modular, Pythonic, and orchestrated by Dagster.  
It bridges external data sources to the warehouse, ensuring that **dbt** always operates on clean, current, and governed datasets.
