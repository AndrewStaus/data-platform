import os
from collections.abc import Collection
from pathlib import Path

import pandas as pd
import pygwalker as pyg
import snowpark_extensions
from pygwalker.api.pygwalker import PygWalker
from pygwalker.data_parsers.database_parser import Connector
from snowflake import snowpark
from snowflake.snowpark import Session


def _var(key) -> str:

    from dotenv import load_dotenv

    path = Path(__file__).joinpath("../../../../.env.dev").resolve()
    load_dotenv(path)
    return os.getenv(key) or ""

def get_session(warehouse=None) -> snowpark.Session:

    if not warehouse:
        warehouse = _var("DESTINATION__WAREHOUSE")

    session = Session.get_active_session()
    if not session:
        session = (
            Session.builder.configs({ 
                "database":  "_dev_analytics",
                "schema":    _var("DESTINATION__USER"),
                "account":   _var("DESTINATION__HOST"),
                "user":      _var("DESTINATION__USER"),
                "password":  _var("DESTINATION__PASSWORD"),
                "role":      _var("DESTINATION__ROLE"),
                "warehouse": warehouse,
            }) 
            .create()
        )

        print("session_id:", session.session_id)
        print("version:",    session.version)
        print("database:",   session.get_current_database())
        print("schema:",     session.get_current_schema())
        print("user:",       session.get_current_user())

    return session

def display(data: str | snowpark.DataFrame | pd.DataFrame | Collection) -> PygWalker | None:
    if isinstance(data, str | snowpark.DataFrame):
        _display_snowpark(data)
    else:
        df = pd.DataFrame(data)
        _display_df(df)


def _display_df(df: pd.DataFrame) -> None:
    pyg.walk(
        df,
        default_tab="data",
        theme_key="streamlit",
        appearance="light",
        show_cloud_tool=False
    )

def _display_snowpark(data: snowpark.DataFrame | str) -> None:
    session = get_session()
    sql = data.queries["queries"][0] if isinstance(data, snowpark.DataFrame) else data

    account = session.get_current_account() or ''
    user = session.get_current_user() or ''
    schema = session.get_current_schema() or ''
    database = session.get_current_database() or ''
    opts = ""
    if session.get_current_warehouse() is not None:
        opts += f"&warehouse={session.get_current_warehouse()}"
    if session.get_current_role() is not None:
        opts += f"&role={session.get_current_role()}"
    
    conn_url = f"snowflake://{user}@{account}/{database}/{schema}?{opts}"

    existing_snowflake_connection = session._conn._conn
    setattr(existing_snowflake_connection,"_interpolate_empty_sequences", False)  # noqa: B010
    existing_snowflake_connection._paramstyle = "pyformat"

    conn = Connector(
        conn_url,
        sql,
        engine_params={"creator": lambda: existing_snowflake_connection}
    )

    pyg.walk(
        conn,
        default_tab="data",
        theme_key="streamlit",
        appearance="light",
        show_cloud_tool=False
    )

session = get_session()