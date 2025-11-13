# .yaml/

Configuration files for the YAML vs code extension to enable intellisense on YAML files
for sling and dlt.

## Purpose

- **Templates:** Provide easy to understand templates for interacting with YAML files.
- **Error Catching:** intellisense will provide feedback if a YAML file contains
    invalid properties or values, reducing time in runtime debugging.

## Contents

- `dlthub`: YAML Schemas and example config files for dlthub to use in reference.
- `sling` YAML Schemas and example config files for sling to use in reference.

## Usage

Ensure that the YAML vscode extension is installed, and workspace/user settings provide
mappings for the files and associations:

```json
# .vscode/settings.json
{
    # ...
    "yaml.schemas": {
        "/workspaces/data-platform/.yaml/dlthub/sources.json": "**/dlthub/**/*.yaml",
        "/workspaces/data-platform/.yaml/sling/connections.json": "**/sling/**/connections.yaml",
        "/workspaces/data-platform/.yaml/sling/replication.json": "**/sling/**/*replication*.yaml"
    },
    # ...
}
``` 