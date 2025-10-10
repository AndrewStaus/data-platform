# dltHub
https://dlthub.com/
<br>[docs](https://dlthub.com/docs/intro)

>dlt is the most popular production-ready Python library for moving data. It loads data from various and often messy data sources into well-structured, live datasets.
>
>Unlike other non-Python solutions, with dlt, there's no need to use any backends or containers. We do not replace your data platform, deployments, or security models. Simply import dlt in your favorite AI code editor, or add it to your Jupyter Notebook. You can load data from any source that produces Python data structures, including APIs, files, databases, and more.

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
    n1["dlt_source.py"] --> n3["factory"]
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
The factory will parse user defined python scripts into dagster resources and assets.

### Translator
The translator will tell dagster how to translate dltHub concepts into dagster concepts, such as how a asset key is defined, or a automation condition.

### Resources
The resources will pass all the translated assets to the dagster runtime.

## Artifacts
### definitions.py
The reources file is what is ingested through the factory to create the dltHub assets
in dagster.  The user will provide a lists of resources, typically one for each endpoint
that will materialize as an asset in dagster.

``` python
# definitions.py
from .data import api_generator
...
ConfigurableDltResource.config(
    dlt.resource(
        # the generator you defined in the data.py file
        api_generator,
        # the schema and table to materialize on the 
        name="schema.table", warehouse 
        table_name="table",
        primary_key="id", # the primary key column
        write_disposition="merge", # how to incrementally load
    ),
    kinds={"api"},
    # aditional dagster configuration for orchestration and checks
    meta={
        "dagster": { 
            "automation_condition": "on_schedule", 
            "automation_condition_config": {
                "cron_schedule": "@daily",
                "cron_timezone": "utc",
            },
            "freshness_lower_bound_delta_seconds": 108000
        }
    },
)
...
```
### data.py
The code to generate data, this will be imported into the definitions.py module.  dltHub
can accept any arbitrary code as long as it yields a python data object.  Suported 
formats include avro data frames, json in the form of python dictonaries

``` python
# data.py
from collections.abc import Callable, Generator
from typing import Any

import requests

def api_generator() -> Generator[Any, Any, None]:
    uri = "https://www.api.com/endpoint"
    response = requests.get(uri)
    yield response.json()
    while next_uri := response.json().get("next_page"):
        response = requests.get(next_uri)
        yield response.json()
```

A common design pattern for api's with multiple endpoints is to use a factory function
that will return a different generator for different enpoints.

``` python
# data.py
from collections.abc import Callable, Generator
from typing import Any

import requests

def get_api_generator(endpoint: str) -> Callable[[], Any]:
    base_uri = "https://www.api.com/"

    def api_generator() -> Generator[Any, Any, None]:
        response = requests.get(base_uri+endpoint)
        yield response.json()
        while next_uri := response.json().get("next_page"):
            response = requests.get(next_uri)
            yield response.json()
    
    return api_generator
```
This can then be reused in the resources.py module

``` python
# definitions.py
from .data import get_api_generator
...
ConfigurableDltResource.config(
    dlt.resource(
        get_api_generator("endpoint_one"),
        name="schema.table_one",
        table_name="table_one",
        primary_key="id",
        write_disposition="merge",
    ),
    kinds={"api"}
),
ConfigurableDltResource.config(
    dlt.resource(
        get_api_generator("endpoint_two"),
        name="schema.table_two",
        table_name="table_two",
        primary_key="id",
        write_disposition="merge",
    ),
    kinds={"api"}
),
...
```


## Other dltHub concepts
On its own dltHub has other concepts that you may see in their documentation such as pipelines, desinations, state, schema, however these have been abstracted away in the data platform, so all a developer needs to focus on is creating a generator, and defining it as a dagster asset in the definitions.py file.
