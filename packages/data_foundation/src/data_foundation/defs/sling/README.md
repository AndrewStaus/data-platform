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

## Factory
The factory will parse user defined yaml files representing connections and streams into dagster resources and assets.

## Translator
The translator will tell dagster how to translate sling concepts into dagster concepts, such as how a asset key is defined, or a automation condition.

## Resources
The resources will pass all the translated assets to the dagster runtime.