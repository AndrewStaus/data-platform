# Home

**Dagster** • **dbt** • **Snowflake**

A modern, modular data platform for end-to-end orchestration, transformation, and analytics.

---

## What It Is

This repository is a **reference implementation** of a modern data stack that unifies:

- **Dagster** for orchestration and observability  
- **dbt** for SQL-based transformation and testing  
- **Snowflake** for scalable cloud warehousing  
- **dltHub** for Pythonic ingestion and normalization of semi-structured data  
- **Sling** for declarative configuration of replication pipelines from databases and filesystems

It’s designed for **data engineers**, **analytics engineers**, and **platform engineers** to work side-by-side with clear boundaries, strong governance, and simple local development.

---

## Core Layers

### **Dagster** — Orchestration & Lineage  
Dagster ties everything together:

- Executes Sling and dltHub pipelines  
- Runs dbt transformations in sequence  
- Surfaces metadata, lineage, and freshness in one unified graph  

➡ See [Dagster Overview](getting_started/orchestration/dagster/index.md)

---

### **dbt** — Transformations & Marts  
SQL transformations that model raw data into **clean, analytics-ready marts**.  
Includes:

- Staging layers organized by source system  
- Shared dimensions and fact models (`marts/`)  
- Tests, freshness checks, and ownership metadata  

➡ See [dbt Overview](getting_started/transformation/dbt/index.md)

---

### **Sling** — Declarative Replication  
YAML-based configuration for **extract and load (EL)** pipelines.  
Sling connects external databases or APIs to Snowflake’s **raw** layer, defining:

- Connection details (`connections.yaml`)
- Replication rules and stream settings (`replication.yaml`)

➡ See [Sling Overview](getting_started/ingestion/sling/index.md)

---

### **dltHub** — Pythonic Ingestion  
Lightweight Python connectors for APIs and semi-structured sources.  
Each module defines:

- `data.py`: a generator yielding structured data batches  
- `sources.yaml`: replication and destination mapping  

Ideal for dynamic datasets or paginated APIs.

➡ See [dltHub Overview](getting_started/ingestion/dlthub/index.md)

---

## Repository Layout

| Path | Owner Focus | Description | 
| --- | --- | --- |
| **.dagster_home/** | Platform | persistent storage for development settings such as telemetry defaults. |
| **.devconatainer/** | Platform | Visual Studio Code Dev Container to share development environment for local development. |
| **.github/** | Platform | CI/CD automation (publishing docs, running checks). |
| **.helm** | Platform | Deployment values for helm chart to deploy to Kubernetes. |
| **.mkdocs/** | Cross-functional | Markdown sources for the MkDocs site published via GitHub Pages. |
| **.vscode/** | Cross-functional | Shared workspace settings, including code snippets for faster development. |
| **docs/** | Cross-functional | Static documentation pages. Prioritize placing documentation in the relevant area of the project, however this space can be used for documentation does not otherwise have an appropriate location. |
| **libs/** | Cross-functional | Shared libraries for common functions between packages. |
| **packages/** | --- | Code locations which are deployed as separate docker images providing environment isolation so that multiple teams can manage their own code. |
| **packages/data_analytics/** | Data & Analytics | Exploratory sql analyses and notebooks. |
| **packages/data_science/** | Data & Analytics | Dagster definitions, resource configuration, and integration glue code. Includes Snowpark definitions for ML-Ops. |
| **packages/data_foundation/** | --- | Foundational data assets that are used across the business.  Contains ingestion's and the main dbt project |
| **../../src/data_foundation** | Platform | Dagster definitions, resource configuration, and integration glue code. Includes Sling source connection YAML that controls raw data ingestion   |
| **../../dbt/** | Cross-functional | dbt project containing models, seeds, snapshots, and tests. YAML files document sources, staging models, and marts. |
| **.env.example** | Cross-functional | Environment variable template for local development.  Should be copied to `.env` and have values replaced with correct credentials. |
| **Dockerfile**, **pyproject.toml**, **uv.lock** | Platform | Runtime dependencies for orchestrator workers. |
| **workspaces** | Platform | Dagster code location configuration for local development. |

---

## Local Development

- Consistent containerized environment across all engineers
- Fast iteration with instant feedback from Dagster & dbt
- Test and debug orchestration locally before deployment
- Safe sandboxing with isolated Snowflake schemas
- Reproducible builds via Dev Container configuration
- Preinstalled extensions for dbt, Snowflake, and Python

---

## Governance & Observability

- **YAML-first configuration** for transparency and version control  
- **Dagster lineage graphs** linking ingestion → transformation → marts  
- **Automated docs** published via MkDocs and GitHub Pages  
- **Secrets** securely managed via `.env` and vault integration  
- **CI checks** for linting, unit tests, and dbt validation

---

## Learn More

| Topic | Documentation |
| ------ | -------------- |
| **Sling** | [Extract & Load Configuration](getting_started/ingestion/sling/index.md) |
| **dltHub** | [Python Connectors & API Sources](getting_started/ingestion/dlthub/index.md) |
| **dbt** | [Transformations, Marts, and Testing](getting_started/transformation/dbt/index.md) |
| **Dagster** | [Orchestration and Asset Graph](getting_started/orchestration/dagster/index.md) |
| **Local Setup** | [Developer Quick Start](getting_started/index.md) |

---

## Contributing

- Keep YAML comments current — they document orchestration and ownership.  
- Add new sources via **Sling** or **dltHub**, then create matching dbt sources.  
- All production changes must include **tests** and **docs** updates.

---

## Links
  
- ⚙️ **Dagster Docs:** [docs.dagster.io](https://docs.dagster.io/)  
- 🧠 **dbt Docs:** [docs.getdbt.com](https://docs.getdbt.com/)  
- ❄️ **Snowflake Docs:** [docs.snowflake.com](https://docs.snowflake.com/)  
- 🔁 **dltHub Docs:** [dlthub.com/docs](https://dlthub.com/docs/intro)  
- ⚡ **Sling Docs:** [slingdata.io/docs](https://docs.slingdata.io/)  
