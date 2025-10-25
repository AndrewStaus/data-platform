[![Unit Tests](https://github.com/AndrewStaus/data-platform/actions/workflows/check__unit_tests.yml/badge.svg)](https://github.com/AndrewStaus/data-platform/actions/workflows/check__unit_tests.yml)
[![Linting](https://github.com/AndrewStaus/data-platform/actions/workflows/check__linting.yml/badge.svg)](https://github.com/AndrewStaus/data-platform/actions/workflows/check__linting.yml)
[![dbt Checks](https://github.com/AndrewStaus/data-platform/actions/workflows/check__dbt_checks.yml/badge.svg)](https://github.com/AndrewStaus/data-platform/actions/workflows/check__dbt_checks.yml)
[![CodeQL](https://github.com/AndrewStaus/data-platform/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/AndrewStaus/data-platform/actions/workflows/github-code-scanning/codeql)
# Data Platform

**Dagster** • **dbt** • **Snowflake**

A modern, modular data platform for end-to-end orchestration, transformation, and analytics.

---

## 🚀 What It Is

This repository is a **reference implementation** of a modern data stack that unifies:

- **Dagster** for orchestration and observability  
- **dbt** for SQL-based transformation and testing  
- **Snowflake** for scalable cloud warehousing  
- **dltHub** for Pythonic ingestion and normalization of semi-structured data  
- **Sling** for declarative configuration of replication pipelines from databases and filesystems

It’s designed for **data engineers**, **analytics engineers**, and **platform engineers** to work side-by-side with clear boundaries, strong governance, and simple local development.

---

## 🧩 Core Layers

### **Dagster** — Orchestration & Lineage  
Dagster ties everything together.  
It:
- Executes Sling and dltHub pipelines  
- Runs dbt transformations in sequence  
- Surfaces metadata, lineage, and freshness in one unified graph  

➡ See [Dagster Overview](dagster/index.md)

---

### **dbt** — Transformations & Marts  
SQL transformations that model raw data into **clean, analytics-ready marts**.  
Includes:
- Staging layers organized by source system  
- Shared dimensions and fact models (`marts/`)  
- Tests, freshness checks, and ownership metadata  

➡ See [dbt Project](getting_started/dbt/index.md)

---

### **Sling** — Declarative Replication  
YAML-based configuration for **extract and load (EL)** pipelines.  
Sling connects external databases or APIs to Snowflake’s **raw** layer, defining:
- Connection details (`connections.yaml`)
- Replication rules and stream settings (`replication.yaml`)

➡ See [Sling Overview](getting_started/sling/index.md)

---

### **dltHub** — Pythonic Ingestion  
Lightweight Python connectors for APIs and semi-structured sources.  
Each module defines:
- `data.py`: a generator yielding structured data batches  
- `sources.yaml`: replication and destination mapping  

Ideal for dynamic datasets or paginated APIs.

➡ See [dltHub Overview](getting_started/dlthub/index.md)

---

## 🏗️ Repository Layout

| Path | Purpose |
| --- | --- |
| `.devcontainer/` | Shared VS Code development container |
| `.github/` | CI/CD pipelines (tests, linting, docs, security) |
| `packages/data_foundation/` | Core ingestion, transformation, and orchestration code |
| `packages/data_analytics/` | Exploratory SQL and notebooks |
| `packages/data_science/` | Machine learning integrations and Snowpark definitions |
| `.mkdocs/` | Documentation site configuration |
| `.env.example` | Template for local environment variables |

---

## 💻 Local Development

1. Open in VS Code (Dev Container ready)  
2. Copy `.env.example` → `.env` and set credentials  
3. Run `uv sync --all-packages` to install dependencies  
4. Launch Dagster with `dagster dev`  

*Windows users*: ensure [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) is installed and connected before opening the Dev Container.

---

## 🔍 Governance & Observability

- **YAML-first configuration** for transparency and version control  
- **Dagster lineage graphs** linking ingestion → transformation → marts  
- **Automated docs** published via MkDocs and GitHub Pages  
- **Secrets** securely managed via `.env` and vault integration  
- **CI checks** for linting, unit tests, and dbt validation

---

## 📘 Learn More

| Topic | Documentation |
| ------ | -------------- |
| **Sling** | [Extract & Load Configuration](getting_started/sling/index.md) |
| **dltHub** | [Python Connectors & API Sources](getting_started/dlthub/index.md) |
| **dbt** | [Transformations, Marts, and Testing](getting_started/dbt/index.md) |
| **Dagster** | [Orchestration and Asset Graph](getting_started/dagster/index.md) |
| **Local Setup** | [Developer Quick Start](getting_started/index.md) |

---

## 🤝 Contributing

- Keep YAML comments current — they document orchestration and ownership.  
- Add new sources via **Sling** or **dltHub**, then create matching dbt sources.  
- All production changes must include **tests** and **docs** updates.

---

## 🌐 Links

- 📄 **Project Docs:** [andrewstaus.github.io/data-platform](https://andrewstaus.github.io/data-platform/)  
- ⚙️ **Dagster Docs:** [docs.dagster.io](https://docs.dagster.io/)  
- 🧠 **dbt Docs:** [docs.getdbt.com](https://docs.getdbt.com/)  
- ❄️ **Snowflake Docs:** [docs.snowflake.com](https://docs.snowflake.com/)

