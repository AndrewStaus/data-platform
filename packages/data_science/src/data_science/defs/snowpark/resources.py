"""An I/O Manager for handling the connection to Snowpark."""

import dagster as dg
from dagster.components import definitions
from data_platform_utils.secrets import get_secret_value


class SnowparkResource(dg.ConfigurableResource):
    """I/O Manager Resource class for managing Snowpark sessions"""

    def __init__(self, **kwargs) -> None:     
        super().__init__(**kwargs)
        self._session = None

    def get_session(self, database="analytics",
                    schema: str | None = None,
                    warehouse: str|None = None) -> "snowflake.snowpark.Session":  # type: ignore # noqa
        """Create a session with snowpark to allow for control of the remote execution
        environment.

        Args:
            database: Specify a specific database to use to remove requiring referencing
                assets by their fully qualified name.
            schema: Specify a specific schema to use to remove requiring referencing
                assets by their fully qualified name.
            warehouse: The compute warehouse to run on so that the appropriate resources
                are utilized.

        Returns:
            snowflake.snowpark.Session: A session which will allow for remote code
            execution on a snowflake warehouse.
        """
        import sys

        from data_platform_utils.helpers import get_database_name, get_schema_name
        from snowflake.snowpark import Session

        if sys.platform == "win32":
            # hotfix to prevent path conversion issue on windows installations
            # should be able to remove once resolved in snowflake.snowpark
            import pathlib
            pathlib.PosixPath = pathlib.PurePosixPath

        if schema:
            schema = get_schema_name(schema)
        else:
            schema = get_secret_value("DESTINATION__SNOWFLAKE__USER")

        
        if not warehouse:
            warehouse = get_secret_value("DESTINATION__SNOWFLAKE__WAREHOUSE")

        self._session = (
            Session.builder.configs({ 
                "database":  get_database_name(database),
                "account":   get_secret_value("DESTINATION__SNOWFLAKE__HOST"),
                "user":      get_secret_value("DESTINATION__SNOWFLAKE__USER"),
                "password":  get_secret_value("DESTINATION__SNOWFLAKE__PASSWORD"),
                "role":      get_secret_value("DESTINATION__SNOWFLAKE__ROLE"),
                "warehouse": warehouse,
            })
            .create()
        )

        try:
            self._session.use_schema(schema)
        except Exception:
            self._session.sql(f"create schema if not exists {schema}")
            self._session.use_schema(schema)

        return self._session


@definitions
def defs() -> dg.Definitions:
    return dg.Definitions(resources={"snowpark": SnowparkResource()})