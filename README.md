# Data Platform
**Dagster** + **dbt** + **Snowflake**

This repository contains a reference implementation of a modern data platform that
combines [Dagster](https://dagster.io/) orchestration, [dbt](https://www.getdbt.com/)
transformation pipelines, and Snowflake data warehousing. It is intentionally organized
so that data engineers, analytics engineers, and platform engineers can collaborate with
clear ownership boundaries.

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

## Local Development

### Setup

1. Open VS Code.
2. *Windows*: Install the `WSL` Extension.
3. *Windows*: Press `CTRL SHIFT P` and run `>WSL: Connect to WSL`.
4. Install the `Dev Containers` Extension.
5. *Windows*: Select `Clone Repository` to download to your Linux filesystem for better
performance.
6. Copy `.env.example` to `.env` and set your development credentials.
7. Press `CTRL SHIFT P` and run `>Dev Containers: Open in container`.
8. install Docker for WSL if prompted (This is the free community edition of docker).
9. Run `uv sync --all-packages` in the terminal.

*Note:* Windows Subsystem for Linux with an installed distribution is required for
developers using a Windows based local machine.

### Usage
- dbt-Fusion and its extensions will be automatically installed in the container.
You can run dbt models directly from VS Code.
- Snowflake extension is also installed to execute non-dbt scripts from VS Code.
- environments for libs, and packages/data_analytics will not be automatically
installed.  For a better development experience, you should run `uv sync` from within
the project directories to install the appropriate virtual environments.

## Dagster (Platform Engineer View)

Dagster assets and schedules live under
`packages/data_foundation/src/data_foundation/defs/`
### Key concepts:
- `sling/` contains source replication specifications used to ingest raw layers in
Snowflake. These YAML files now include inline comments describing connection secrets,
replication cadence, and ingestion pattern.
- `dlthub/` contains source replication code to ingest raw layers in Snowflake through
Python defined logic.  Python code is used to generate structured and semi-structured
data (dataframes, lists of lists, lists of dicts, etc.), and dlt will wrap that logic
and provide control over replication cadence, ingestion patterns, and normalization.
- Dagster uses the `dagster.yaml` file in the repository root for instance
settings shared across developers and CI, such as disabling telemetry.
- Helm deployment values are stored in `.helm/values.yaml` to control the configuration
of the Kubernetes deployments while preserving upstream defaults.

## dbt (Data & Analytics Engineer View)

The dbt project is in the `packages/data_foundation/dbt/` directory and is structured as
follows:

- `dbt_project.yml` and `profiles.yml` capture project-wide behavior and
  environment-specific Snowflake credentials. Comments highlight the
  relationship between Dagster, dbt, and warehouse settings.
- `models/` holds staging layers grouped by source system as well as mart
  models such as `marts/common/fct_common__fct_transactions.sql`. Each model has
  an accompanying YAML file that documents columns, tests, and freshness checks.
- `snapshots/` preserves historical slowly-changing dimensions and facts. Inline
  comments describe retention and privacy handling for sensitive domains.
- `seeds/` contains CSV-backed reference data with YAML documentation.
- `groups/` assigns ownership metadata so alerts and governance roll to the
  appropriate teams.
- `macros/` provides shared macros similar to UDF's that enables complex logic to be
defined in one place and reused across the project.
- `packages.yml` lists third-party macro packages used across the project.

## Documentation Site

- `.mkdocs/mkdocs.yml` defines the MkDocs/Material configuration used to render the
  docs stored under `docs/`.
- The GitHub Actions workflow in `.github/workflows/docs.yml`  will regenerate and 
publishes the documentation to based on comments and doc strings in the source code to
a GitHub Pages whenever changes land on `main`.
- Documentation can be found on the gitHub pages site:
  #### https://andrewstaus.github.io/data-platform/

### Secrets and configuration

- Environment-specific secrets are loaded from `.env` file which the user must create
using `.env.example` as a template. The Dagster code location will still load—when the
required secrets are missing, however assets will fail to materialize successfully if
their secrets are not present.

- If the `.env` file is changed, the dev container must be reloaded before the change
will take effect.
- If your network proxies TLS, export `DBT_ALLOW_INSECURE_SSL=1` before running
`dagster dev`. The code temporarily disables certificate verification while dbt
downloads packages and restores the settings afterwards.

## Contribution Guidelines

- Keep YAML comments up to date—they explain how orchestration, ingestion, and
modeling pieces fit together for the next engineer who reads the config.
- When adding a new source system, define the Sling connection in
`data_foundation/src/defs/sling/sling/` and create matching dbt source definitions
under `data_foundation/dbt/models/staging/<system>/`.
- All production-facing changes should include tests (`dbt test`) and, when
relevant, updates to the documentation site.

## Further Reading

- Project docs: <https://andrewstaus.github.io/data-platform/>
- Dagster docs: <https://docs.dagster.io/>
- dbt docs: <https://docs.getdbt.com/>
- Snowflake docs: <https://docs.snowflake.com/>
