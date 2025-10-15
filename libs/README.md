# libs/

Shared libraries for common functions between packages.

## Purpose

- **DRY** Don't repeat yourself methodology to allowing for common code to be reused in
different packages

## Contents

- `analytics_utils`: Utilities for working with Snowflake and Snowpark easier in
interactive jupyter notebook sessions.
- `data_platform_utils`: Utilities for common integration settings in Dagster across
user code-locations.

## Usage

These modules can be set as dependencies for other modules in the `packages` directory
by adding them to the respective `pyproject.toml` files.

    ```toml
        [project]
        dependencies = ["analytics-utils"]

        [tool.uv.sources]
        analytics-utils = { path = "../../libs/analytics_utils" }
    ```