# Data Platform
**Dagster** + **dbt** + **Snowflake**

This repository contains a reference implementation of a modern data platform
that combines [Dagster](https://dagster.io/) orchestration, [dbt](https://www.getdbt.com/)
transformation pipelines, and Snowflake data warehousing. It is intentionally
organized so that data engineers, analytics engineers, and platform engineers
can collaborate with clear ownership boundaries.

## Repository Layout

| Path | Owner Focus | Description |
| --- | --- | --- |
| `data_foundation/data_foundation/` | Platform | Dagster definitions, resource configuration, and integration glue code. Includes Sling source connection YAML that controls raw data ingestion. |
| `data_foundation/dbt/` | Cross-functional | dbt project containing models, seeds, snapshots, and tests. YAML files document sources, staging models, and marts. |
| `data_science/` | Data & Analytics | Dagster definitions, resource configuration, and integration glue code. Includes Snowpark definitions for ML-Ops. |
| `data_analytics/` | Data & Analytics | Exploratory sql analyses and notebooks. |
| `libs/` | Cross-functional | Shared libraries. |
| `docs/` | Cross-functional | Markdown sources for the MkDocs site published via GitHub Pages. |
| `Dockerfile`, `pyproject.toml`, `uv.lock` | Platform | Runtime dependencies for orchestrator workers and local development. |
| `.github/workflows/` | Platform | CI/CD automation (publishing docs, running checks). |
| `dagster.yaml` | Platform | Shared Dagster instance settings such as telemetry defaults. |
| `mkdocs.yml` | Cross-functional | Documentation site build configuration. |

## Dagster (Platform Engineer View)

Dagster assets and schedules live under `data_platform/defs/`. Key concepts:

- `sling/` contains source replication specifications used to bootstrap raw
  layers in Snowflake. These YAML files now include inline comments describing
  connection secrets, replication cadence, and how Dagster automation metadata
  is applied.
- `dlthub/` contains source replication code to ingest raw layers in Snowflake
  through Python defined logic.
- Dagster uses the `dagster.yaml` file in the repository root for instance
  settings shared across developers and CI, such as disabling telemetry.
- Helm deployment scaffolding is stored in `.helm/values.yaml` to
  help platform engineers customize Kubernetes deployments while preserving
  upstream defaults.

## dbt (Data & Analytics Engineer View)

The dbt project is in the `dbt/` directory and is structured as follows:

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
- `packages.yml` lists third-party macro packages used across the project.

## Documentation Site

- `mkdocs.yml` defines the MkDocs/Material configuration used to render the
  docs stored under `docs/`.
- The GitHub Actions workflow in `.github/workflows/static.yml` publishes the
  static site to GitHub Pages whenever changes land on `main`.
- Documentation can be found on the gitHub pages site:
  #### https://andrewstaus.github.io/data-platform/

## Local Development

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
2. [Install dbt-Fusion](https://docs.getdbt.com/docs/fusion/install-fusion)
3. Copy `.env.example` to `.env` and set Snowflake credentials.
4. Run `uv run ./src/main` to start the Dagster UI with local assets.
5. Orchestrator containers can be started with `docker compose up`. The
   code-server exposes a health check so the webserver waits until assets are
   ready before it boots.
6. Use `dbt deps` and `dbt build` from the `dbt/` directory to compile and test
   models.
7. cd to `.mkdocs` directory and run `mkdocs serve` to preview the documentation site
   locally.

### Secrets and configuration

- Environment-specific secrets are loaded from `.env` file. The Dagster code location
  will still load—when the required secrets are missing,  and a warning is emitted in
  the code-server logs to help track down the missing value. Populate the secret and
  restart the containers to activate the connection.
- If your network proxies TLS, export `DBT_ALLOW_INSECURE_SSL=1` before running
  `docker compose` or `dagster dev`. The code temporarily disables certificate
  verification while dbt downloads packages and restores the settings
  afterwards.

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

## Workspace Layout
```text
data-platform
└── packages
    ├── data_analytics/analyses  .........  Workspace with isolated virtual environment
    │                                        for interactive analytics and science.
    ├── data_foundation  .................  Package for dagster data-foundation dagster
    │   │                                    code location.
    │   ├── dbt  .........................  dbt Project directory that contains all 
    │   │                                    transformation logic.
    │   └── src/data_foundation/defs  ....  Dagster definition files that define assets
    │       │                                and resources.
    │       ├── dbt  .....................  Factories for auto generating dagster assets
    │       │                                 based on dbt project artifacts.
    │       ├── dlthub  ..................  Factories for auto generating dagster assets
    │       │   │                             based on dlthub python scripts.
    │       │   └── dlthub  ..............  Python scripts the utilize the dlthub
    │       │                                 library to provide robust ingestion
    │       └── sling  ...................  Factories for auto generating dagster assets
    │           │                             based on sling replication yaml configs.
    │           └── sling  ...............  Sling replication config yaml files which
    │                                         specify table ingestion specs.
    └── data_science  ....................  Package for dagster data-science dagster
        │                                    code location.
        └── src/data_science/defs  .......
            │
            └── snowpark  ................
                │
                └── snowpark  ............

```