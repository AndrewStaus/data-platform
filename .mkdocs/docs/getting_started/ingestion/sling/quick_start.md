# Quick Start

Follow these steps to quickly set up and run your first Sling configuration.

---

## 1. Create Configuration Files

Create a folder named after the database you’re connecting to.  
Inside that folder, create two files:

- `connections.yaml` — defines connection details  
- `replication.yaml` — defines replication (extract & load) behavior

???+ quote "Creating Configuration Files"
    ![Sling Files](../../../assets/images/sling/1_files.gif){ align=left }

---

## 2. Scaffold `connections.yaml`

IntelliSense scaffolds are provided to simplify setup.
Open `connections.yaml` and press `Ctrl + Space` to open the autocomplete pane and select **`sling-connections`** to populate a connection template.

???+ quote "connections.yaml"
    ![Sling Connections](../../../assets/images/sling/2_connections.gif){ align=left }

---

## 3. Scaffold `replication.yaml`

IntelliSense scaffolds are provided to simplify setup.  
Open `replication.yaml` and press `Ctrl + Space` to open the autocomplete pane and select **`sling-replication`** to populate a replication template.

???+ quote "replication.yaml"
    ![Sling Replication](../../../assets/images/sling/3_replication.gif){ align=left }

---

## 4. Configure Streams

Use IntelliSense (`Ctrl` + `Space`) to explore valid stream configuration options.  
Stream-level settings inherit values from the replication defaults unless explicitly overridden.

???+ quote "Configure Streams"
    ![Sling Stream](../../../assets/images/sling/4_streams.gif){ align=left }

---

## 5. YAML Hints

YAML schemas are enabled to validate inputs, provide autocomplete, and display field descriptions — all designed to improve accuracy and speed during setup.

???+ quote "YAML Hints"
    ![YAML Hints](../../../assets/images/sling/5_hints.gif){ align=left }

---

## 6. View and Run in Dagster

Open Dagster to view and run your newly configured replications.
??? hint "dagster dev"
    Run `dagster dev` or press `Reload definitions` in the dagster UI if it is already running.
    This will result in your replications being displayed.  See the [Dagster quick start guide](../../orchestration/dagster/quick_start.md)
    for more info.

---

## 7. Submit a Pull Request

Once you are satisifed with your changes, you may open a pull request to have your
changes merged into the QA branch for testing and validation.
