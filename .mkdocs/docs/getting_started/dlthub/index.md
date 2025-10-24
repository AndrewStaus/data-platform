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

### 2. `data.py`
??? example "data.py"

      ```python
      import requests

      def get_exchange_rates():
         url = "https://api.exchangerate.host/latest"
         response = requests.get(url)
         data = response.json()

         # Yield in pages or time slices if needed
         yield data["rates"]
      ```

The **`data.py`** script defines the **data generator** — a Python function that yields data in batches.  
Each yield represents a page or chunk of records fetched from the source system (API, file, or database).

This generator pattern allows dltHub to:
- Stream large datasets efficiently  
- Handle pagination and rate limits  
- Maintain memory efficiency during ingestion  

Ingestion functions can also accept arguments (like date ranges or filters), allowing Dagster to parametrize runs dynamically.

---

### 3. `sources.yaml`
??? example "source.yaml"

      ```yaml
      resources:
         exchange_rate.usd:
            entry: data.get_exchange_rates
            arguments: [usd]
            write_disposition: replace
      ```

The **`sources.yaml`** file defines the **replication and resource configuration** for dltHub.  
It tells dltHub how to call the generator and where to send the resulting data.

Typical fields include:

| Key | Description |
| ---- | ------------ |
| `entry` | The import path to the generator function, e.g. `exchange_rate.data.get_exchange_rates` |
| `arguments` | Optional positional arguments passed to the function to select a generator |
| `keword_arguments` | Optional keyword arguments passed to the function to select a generator |
| `write_disposition` | Defines whether data is appended, replaced, or merged |



---

## Integration with Dagster

**Dagster** is responsible for **executing**, **monitoring**, and **documenting** all dltHub pipelines.  

Each dltHub resource is automatically materialized as a **Dagster asset**, allowing you to:
- Schedule ingestion jobs (hourly, daily, weekly)
- Track lineage from **source → raw → dbt staging → marts**
- Visualize dependencies between connectors and downstream dbt models
- Surface metadata such as run duration, success/failure, and record counts

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
