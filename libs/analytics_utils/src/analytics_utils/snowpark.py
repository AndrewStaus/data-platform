"""Helpers to make interactive sessions with snowpark more seamless."""
import os
from collections.abc import Collection

import pandas as pd
import pygwalker as pyg
import snowpark_extensions  # pyright: ignore[reportMissingImports]  # noqa: F401
from dotenv import find_dotenv, load_dotenv
from IPython.core.display_functions import display as legacy_display
from pygwalker.api.pygwalker import PygWalker
from pygwalker.data_parsers.database_parser import Connector
from snowflake import snowpark
from snowflake.snowpark import Session


def _var(key) -> str:


    env_path = find_dotenv(raise_error_if_not_found=True,
                            usecwd=True)

    load_dotenv(env_path)
    return os.getenv(key) or ""

def get_session(warehouse=None, verbose=True) -> snowpark.Session:

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

    if verbose:
        print("session_id:", session.session_id)
        print("version:",    session.version)
        print("database:",   session.get_current_database())
        print("schema:",     session.get_current_schema())
        print("user:",       session.get_current_user())

    return session

def display(data: str | snowpark.DataFrame | pd.DataFrame | Collection,
            spec:str|None = None) -> PygWalker | None:
    if isinstance(data, str | snowpark.DataFrame | snowpark.dataframe.DataFrame):
        _display_snowpark(data, spec=spec)
    else:
        try:
            df = pd.DataFrame(data)
            _display_df(df, spec=spec)
        except ValueError:
            legacy_display(data)


def _display_df(df: pd.DataFrame, spec:str|None = None) -> None:
    if spec:
        pyg.render(df, spec, theme_key="streamlit", appearance="light")
    else: 
        pyg.walk(
            df,
            default_tab="data",
            theme_key="streamlit",
            appearance="light",
            show_cloud_tool=False
        )

def _display_snowpark(data: snowpark.DataFrame | str, spec:str|None = None) -> None:
    session = get_session(verbose=False)
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

    try:
        conn = Connector(
            conn_url,
            sql,
            engine_params={"creator": lambda: existing_snowflake_connection}
        )
    except TypeError:
        legacy_display(data)
        return


    if spec:
        pyg.render(conn, spec, theme_key="streamlit", appearance="light")
    else: 
        pyg.walk(
            conn,
            default_tab="data",
            theme_key="streamlit",
            appearance="light",
            show_cloud_tool=False
        )

session = get_session()