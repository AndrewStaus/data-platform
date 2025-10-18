# Sling
https://slingdata.io/
<br>https://github.com/slingdata-io/sling-cli
> Sling is a Powerful Data Integration tool enabling seamless ELT operations as well as quality checks across files, databases, and storage systems.

## Structure
``` mermaid
---
config:
  theme: neutral
---
flowchart LR
 subgraph s1["definitions"]
        n4["assets_definition"]
        n5["resource"]
  end
    n1["replication_config.yaml"] --> n3["factory"]
    n2["translator"] --> n3
    n3 --> n4
    n5 --> n7["run"]
    n4 --> n7
    n6["context"] --> n7
    n4@{ shape: doc}
    n5@{ shape: proc}
    n1@{ shape: docs}
    n3@{ shape: procs}
    n2@{ shape: rect}
    n7@{ shape: proc}
    n6@{ shape: proc}
```

### Factory
The factory will parse user defined yaml files representing connections and streams into dagster resources and assets.

### Translator
The translator will tell dagster how to translate sling concepts into dagster concepts, such as how a asset key is defined, or a automation condition.

### Resources
The resources will pass all the translated assets to the dagster runtime.

## Configs

### Connection Config
https://docs.slingdata.io/sling-cli/environment#sling-env-file-env.yaml

The connection config defines the database, or file system connection details so that
it can be used as a source or desintation on replications.  It follows the similar
patterns as the sling env file, however additional functionality iis applied for secret
management through the keyvault.

For values which are stored in the key vault, you can specify the key name, and if
you wish for the key to be shown in plain text on the dagster front end, or if it should
be securly masked.

``` yaml
connections:
  -name: database_name
   type: oracle
   database: {SOURCE__ON_PREM_OLTP__CREDENTIALS__DATABASE: show}
   host: {SOURCE__ON_PREM_OLTP__CREDENTIALS__HOST: show}
   port: {SOURCE__ON_PREM_OLTP__CREDENTIALS__PORT: mask}
   user: {SOURCE__ON_PREM_OLTP__CREDENTIALS__USER: mask}
   password: {SOURCE__ON_PREM_OLTP__CREDENTIALS__PASSWORD: mask}
```

### Replication Config
https://docs.slingdata.io/concepts/replication
Replications are how extract and loads are defined.  Source name, and target names
reference connections you have defined in the connections section.  The connection does
not need to be defined in the yaml file you are referencing it in.  Typically there will
be a single yaml file for each connection, with replications showing egress from that
connection to another system.

``` yaml
replications:
  - name: source_name->desitnation_name
    env: {SLING_LOADED_AT_COLUMN: timestamp}
    source: source_name
    target: target_name
    defaults:
      mode: incremental
      object: '{stream_schema_upper}.{stream_table_upper}'
      primary_key: [id]
      update_key: updated_at
      target_options:
        column_casing: snake
        add_new_columns: true
        adjust_column_type: true
      meta:
        dagster:
          automation_condition: "on_cron_no_deps"
          automation_condition_config: {"cron_schedule":"@daily", "cron_timezone":"utc"}
          freshness_lower_bound_delta: 1800
    streams:
      source_schema.table_one:
        tags: ['contains_pii']
      source_schema.table_two:
        primary_key: [pk_column]

```

Streams are the tables, or files to transfer, settings from the default section are
applied to all streams, unless specific configuartion is applied to that stream in which
case the stream config takes precedence.
