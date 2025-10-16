# data_analytics/

Data analytics space for exploration, research, and ad-hoc analysis.

## Purpose

Exploration space to perform analysis using sql, python, snowpark, etc.
These are not pipelines, but a space to have version controlled analysis.
This would likely be split into domain specific repos.

## Setup
Run `uv sync` from within the data_analytics directory to install the virtual
environment.  The version of python is pegged at 3.10 which is different than the rest
of the workspace in order to support pygwalker.

## Usage

1. Create a jupyter notebook in a folder in the analyses directory.
2. Select the data-analytics kernel.
3. Add the following code:
        ```python
        from analytics_utils.snowpark import display, session
        ```
    to the first cell in a jupyter notebook. This will start an interactive snowpark
    session, based on your .env file credentials and provide a display class to provide
    paginated display of dataframes, and a graphical plotting interface.

## Features
- Tables can be loaded in multiple ways:
    1. table method:
        ```python
        df = session.table("database.schema.table")
        ```
    2. sql method:
        ```python
            df = session.sql(""" --begin-sql
                select * from database.schema.table
            """)
        ```
        The `--begin-sql` flag is optional, but will tell jupyter that the multi-line
        string should be interpreted as sql code for highlighting.
    3. sql magic:

        ```python
        %%sql
        select * from database.schema.table
        ```

        the output can be access in python via the _ variable in the following cell.

        ```python
        df = _
        ```

        Alternatively, a sql statement can be placed in a variable directly:

        ```python
        %%sql df
        select * from database.schema.table
        ```

        ```python
        display(df)
        ```

- The display function
    The `display()` function can be used to show the table in a graphical interface
    provided by pygwalker.
    1. The `data` tab will automatically only retrieve only 100 rows of data by default,
    removing the need to limit query results.
    2. The `visualizations` tab provides a drag and drop gui for rapid exploration of
    the data.


