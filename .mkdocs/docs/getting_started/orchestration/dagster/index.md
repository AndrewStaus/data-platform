# Dagster

Dagster is the **data orchestration layer** of the platform — the control center where ingestion, transformation, and quality workflows come together.  
It enables **observability**, **automation**, and **governance** across the full data lifecycle.


## Core Concepts

### Factories

The implementation of dagster relies heavily on factory models.  This allows users to
define their assets, and dagster will discover and build the asset graph.

---

### Assets
Assets are the building blocks of your data platform.  
Each asset represents a table, dataset, or derived output.  This differs from other
orchestration tools which focus more around pipeline definitions.

- Defined with clear dependencies.
- Automatically builds pipelines based on linage.
- Automatically visualized in the **Asset Graph**.
- Materialized on demand or via automated schedules.

---

### Jobs & Runs

A job defines how assets are executed.
A run is an instance of that execution, capturing all logs, metadata, and results.
You can:

- Trigger runs manually from the Dagster UI.
- Schedule them via automation conditions.
- Monitor and retry failed steps interactively.

---

### Automation Conditions

??? example "automation condition"

    ``` yaml
    meta:
      dagster:
        automation_condition: "on_cron_no_deps"
        automation_condition_config:
          cron_schedule: "@daily"
          cron_timezone: "utc"
    ```

Automation conditions are lightweight configurations defined in metadata that tell Dagster when to run assets automatically.
Common conditions include:

| Condition | Behavior |
| --------- | -------- |
| **on_cron_no_deps** |	Runs on a defined cron schedule, independent of dependencies. |
| **on_cron_with_deps** |	Runs on a schedule after upstream assets succeed. |
| **on_upstream_change** |	Automatically triggers when an upstream asset is updated. |
| **manual_only** |	Requires explicit user-triggered materialization. |


---

### Schedules & Sensors

Dagster automates when and how assets are refreshed.

| Type         | Description                                              | Example                       |
| ------------ | -------------------------------------------------------- | ----------------------------- |
| **Schedule** | Runs on a fixed cron schedule                            | `@daily`, `0 2 * * *`         |
| **Sensor**   | Reacts to an event (e.g., upstream completion, new file) | New S3 file, dbt model update |

---

### Code Locations

- User code can be split into separate code locations, which allow for different
  code dependencies and environments to coincide together in one asset graph.
- Keeps teams isolated by responsibility (ingestion, transformation, etc.)
- Enables independent deployment and testing.
- Unified in the Dagster UI for complete lineage visibility.

---

### Integration with the Platform

Dagster orchestrates across all layers:

| Component     | Role                                        | Dagster’s Function                         |
| ------------- | ------------------------------------------- | ------------------------------------------ |
| **Sling**     | Raw ingestion via YAML-defined replication  | Schedules and monitors replication runs    |
| **dltHub**    | Python-based data extraction and generation | Executes ingestion and normalization code  |
| **dbt**       | SQL-based transformation and testing        | Orchestrates dbt models and freshness runs |
| **Snowflake** | Central data warehouse                      | All assets ultimately materialize here     |
| **Snowpark**  | Python-based machine learning and analytics  | Runs feature engineering and model scoring within Snowflake compute |


---

### Observability & Debugging

- Run logs show detailed execution flow per step.
- Metadata and lineage views visualize upstream/downstream dependencies.
- Auto-retries, failure notifications, and event-based triggers reduce manual overhead.
- Dagster tracks data freshness, versioning, and success status across all assets.

---

### Why Dagster?

- Unified orchestration, providing the ability to glue different resources together.
- Built-in data lineage, freshness tracking, and type safety.
- Simplified CI/CD integration and local development (dagster dev).
- First-class UI for developers and analysts alike.
- Dagster connects your data sources, transformations, and consumers into a cohesive, observable, and automated data platform.
