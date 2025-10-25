# Data Analytics

The **Analytics** module extends the data platform with an **interactive Snowpark integration**, enabling data scientists and analysts to explore, transform, and visualize Snowflake data directly from **Jupyter Notebooks** — without needing Dagster orchestration or manual connection setup.

This workspace bridges the gap between production data pipelines and exploratory analysis, providing a seamless, secure, and developer-friendly environment.

---

## Core Purpose

The Analytics environment is designed to:

- Connect effortlessly to **Snowflake Snowpark** using pre-configured credentials.  
- Support **ad-hoc analysis**, **prototyping**, and **data visualization** outside the main Dagster orchestration.  
- Provide a consistent **local experience** across engineering, data science, and analytics teams.  
- Enable fast feedback loops while maintaining access to production-like data.  

---

## Session Management
??? example "notebook.ipynb"

    ```python
    from analytics_utils.snowpark import session
    ```

At the heart of the Analytics integration is the `session` helper, which creates and
manages a **Snowpark session** automatically upon import.

- Loads credentials from your local .env file.
- Uses the _dev_analytics database by default.
- Automatically connects to your assigned schema, role, and warehouse.
- Prints session details for transparency.

---

## Data Exploration
??? example "notebook.ipynb"

    ```python
    from analytics_utils.snowpark import display
    ```

The integrated visualization experience lets you pivot, plot, and profile your Snowflake
datasets directly in your notebook — no export, no friction.

Display renders data visually with PyGWalker (interactive charts, data profiling)
Falls back to classic IPython.display() for unsupported formats
Supports custom visualization specs with the spec argument

Rendered tables and charts are pre-aggregated on snowflake, and delivered in a
paginated format to ensure a seamless, performant and rich user experience.

---

## Intelligent Behavior

The utility handles many connection details behind the scenes:

- Keeps Snowflake connections persistent for your notebook session.
- Reuses existing Snowpark sessions when available.
- Intercepts low-level connector behavior for compatibility with visual tools.
- Supports secure connection interpolation and role switching via environment variables.

---

## Why Use Data Analytics?

- Fast and secure access to Snowflake data
- Seamless integration with your .env credentials
- Interactive data exploration via PyGWalker
- Unified Python + Snowpark environment
- Bridges the gap between pipelines and ad-hoc exploration

The Analytics workspace empowers teams to go beyond production pipelines — bringing
notebook interactivity to the enterprise-grade data platform.