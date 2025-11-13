# Quick Start

Follow these steps to quickly set up and run your first **dltHub** configuration.

---

## 1. Create Configuration Files

Create a folder named after the dataset or API you’re connecting to.  
Inside that folder, create the following files:

- `__init__.py` — identifies the code as a Python module  
- `data.py` — defines a data generator function  
- `replication.yaml` — defines replication (extract & load) behavior

???+ quote "Creating Configuration Files"
    ![dltHub Files](../../../assets/images/dlt/1_files.gif){ align=left }

---

## 2. Create a Data Generator

In `data.py`, define a generator function that **yields batches of records**.  
Each `yield` returns a small batch of data for dltHub to load incrementally, allowing for **pagination and low memory overhead** during ingestion.

???+ quote "data.py"
    ![dltHub Data](../../../assets/images/dlt/2_data.gif){ align=left }

---

## 3. Configure Resources

The **resources** section defines one or more data generators (resources) that can be run and loaded by dltHub.  
Each resource points to a function defined in your `data.py`.

Press `Ctrl + Space` in VS Code to open IntelliSense and select **`dlt-resources`** to scaffold a resources template.

| Setting | Description |
| -------- | ----------- |
| `entry` | The import path of the function defined in `data.py`, e.g., `data.fetch_users`. |
| `write_disposition` | How data should be written to the destination (`append`, `merge`, `replace`). |
| `primary_key` | Column(s) used for identifying unique records when merging. |
| `args` / `kwargs` | *(Optional)* Additional parameters to pass to the generator function. |

???+ quote "Configure Resource"
    ![dltHub Resource](../../../assets/images/dlt/3_resource.gif){ align=left }

---

## 4. Configure Sources (*Optional*)

Sources group one or more resources under a logical namespace.  
They’re especially useful when combining related resources into a single extract.

Press `Ctrl + Space` and select **`dlt-sources`** to scaffold a sources template.


| Setting | Description |
| -------- | ----------- |
| `sources` | Defines a logical grouping of resources under one connector. |
| `resources` | A list of resource names to include in this source. |
| `meta` | Meta configuration for defining schedules and checks.  Source meta will override any settings in a resources. |

???+ quote "Configure Source"
    ![dltHub Source](../../../assets/images/dlt/4_sources.gif){ align=left }

---

## 5. View and Run in Dagster

Open Dagster to view and run your newly configured replications.
??? hint "dagster dev"
    Run `dagster dev` or press `Reload definitions` in the dagster UI if it is already running.
    This will result in your replications being displayed.  See the [Dagster quick start guide](../../orchestration/dagster/quick_start.md)
    for more info.

---

## 6. Submit a Pull Request

Once you are satisifed with your changes, you may open a pull request to have your
changes merged into the QA branch for testing and validation.
