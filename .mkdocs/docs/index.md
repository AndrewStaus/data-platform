# Home
A Dagster project integrating dbt, Sling, dltHub, and Snowflake into a single data platform.
Includes stubs for powerBi, and AzureML, as well as Azure Keyvault to demonstrate
external integrations.


``` mermaid
---
config:
  theme: neutral
---
flowchart LR
  subgraph s1["sling dlt"]
        n1["src"]
        n2["raw"]
  end
  subgraph s2["dbt"]
        n3["pii"]
        n4["stg"]
        n5["snp"]
        n6["int"]
        n7["mrt"]
  end
  subgraph s3["powerbi"]
        n8["sem"]
        n9["exp"]
  end
  subgraph s4["snowpark"]
        n10["ml"]
  end
  n1 --> n2
  n2 --> n3
  n2 --> n4
  n2 --> n5
  n5 --> n6
  n2 --> n6
  n6 --> n7
  n7 --> n8
  n8 --> n9
  n7 --> n10
  n6 --> n10

```

# Getting Started

## Note on Security
This is a simple configuration for demonstration.  Some security best practices have
been skipped in order to make demonstration easier, however oath is supported for a
real deployment to authenticate developers against the resources their accessing.

## uv
This project is configured using the uv python package manager.  To initialize the
project, install uv if you do not have it already, and enter the command:
``` bash
uv sync
```
This will create a virtual environment and install all required dependacies.

## Resources

### Source Database
This demo has been set up using a postgres server with a handful of tables in a single
schema.

### Desination Warehouse
This demo is using a Snowflake warehouse to demonstrate. It assumes the existance of
the following databases:

#### prod
##### analytics
This is where the silver layer data will be stored: staged (stg), incremental (inc),
dimensions (dim), facts (fct).  This is the main destination for dbt models.  
##### raw
The database that stores data ingested from the source systems.
##### snapshots
SCD Type 2 data, that is primaraly captured through dbt eagerly on raw data.

#### qa
The QA environment is not configured for this demonstration, however in a real
deployment this would exist to perform slim CI on pull requests from feature branchs to
develop, and pull requests from develop to main. 

#### dev
The dev databases mirror the production, however each developer will generate shcmeas
tagged with their user name so that they can develop new assets in isolation.
##### _dev_analytics
##### _dev_raw
##### _dev_snapshots

## .env File
The .env file will hold your environment variables.
Create this file in your root project folder and populate it will the correct
credentials for your database and warehouse.

In a true deployment, this would be set up using more secure methods.

```
# .env
TARGET=dev
DAGSTER_HOME=.\\.dagster_home
PYTHONLEGACYWINDOWSSTDIO=1
DBT_PROJECT_DIR=.\\dbt\\
PREPARE_IF_DEV=1

PROD__DESTINATION__DATABASE=raw
PROD__DESTINATION__HOST=<your_hostname>
PROD__DESTINATION__ROLE=<role_with_create_grants_on_prod>
PROD__DESTINATION__USER=<user_with_create_grants_on_prod>
PROD__DESTINATION__PASSWORD=<user_password>
PROD__DESTINATION__WAREHOUSE=<warehouse>

DEV__DESTINATION__DATABASE=raw
DEV__DESTINATION__HOST=<your_hostname>
DEV__DESTINATION__ROLE=<role_with_create_grants_on_dev>
DEV__DESTINATION__USER=<user_with_create_grants_on_dev>
DEV__DESTINATION__PASSWORD=<user_password>
DEV__DESTINATION__WAREHOUSE=<warehouse>

ANY__SOURCE__DATABASE=<demo_database>
ANY__SOURCE__HOST=<demo_host>
ANY__SOURCE__PORT=<demo_port>
ANY__SOURCE__USER=<demo_user>
ANY__SOURCE__PASSWORD=<demo_password>
```
PROD configuration is used on the production deployment, and the credentials should have
appropriate grants for the prod databases on the warehouse.

DEV configuration is used in the local development environment, and should have select
grants to the analytics databases, and create schema grants on the development
databases. 

ANY configuration is shared between dev and prod, and will be used to connect to the
demo database.

# Deployment
## Local Development
Once the above setup steps are complete, you are ready to launch you local development
server.  A task has been defined in vs code to make running the server easy.

1. Open the command pallet: `ctrl+shift+p`
2. Type `>Tasks: Run Task` and hit enter
3. Type `dagster dev` and hit enter

You should now have a dagster development server running on your local machine.

## Production Deployment
To simulate a production deployment a `build and deploy` task has also been created.
This task assumes that you have docker deskop installed and running, with a 'kind'
kubernettes cluster availible.

If so you can run this command to build the 'user code deployment' docker image and
deploy it to the cluster.  Once deployed you can run the `k8s port forward` to make
the web server availible at `http://127.0.0.1:63446/`

# Useful VS Code Extensions
##### Python
Core python extension from microsoft.  This will provide syntax highlighting for .py
files.
##### Ruff
A python linter that will help conform to style guides for the project.  The styles are
enforced through settings in the pyproject file so that all contributers write high
quality, standardized code.
##### Power User for dbt
Allows for advanced functionality of dbt assets while the official dbt extension
becomes availibe in general release.
##### Even Better TOML
Provides syntax highlighting for TOML files which are used for sling configurations.
##### Cron Explained
When hovering over cron expressions, provides a plain english explanation of what the
expression means.
##### Snowflake
Allows for viewing snowflake resources, and performing SQL, DML, and DDL against the
warehouse.
