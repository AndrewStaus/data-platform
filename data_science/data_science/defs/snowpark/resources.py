import dagster as dg
from dagster.components import definitions
from data_platform_utils.secrets import get_secret_value


class SnowparkResource(dg.ConfigurableResource):
    """Resource class for managing Snowpark sessions"""

    def __init__(self, **kwargs) -> None:     
        super().__init__(**kwargs)
        self._session = None

    def get_session(self, database="analytics",
                    schema: str | None = None,
                    warehouse: str|None = None) -> "snowflake.snowpark.Session":  # type: ignore # noqa
        """Get or create a Snowpark session"""
        import sys

        from data_platform_utils.helpers import get_database_name, get_schema_name
        from snowflake.snowpark import Session

        if sys.platform == "win32":
            import pathlib
            pathlib.PosixPath = pathlib.PurePosixPath

        if schema:
            schema = get_schema_name(schema)
        else:
            schema = get_secret_value("DESTINATION_SNOWFLAKE_USER")

        
        if not warehouse:
            warehouse = get_secret_value("DESTINATION_SNOWFLAKE_WAREHOUSE")

        self._session = (
            Session.builder.configs({ 
                "database":  get_database_name(database),
                "account":   get_secret_value("DESTINATION_SNOWFLAKE_HOST"),
                "user":      get_secret_value("DESTINATION_SNOWFLAKE_USER"),
                "password":  get_secret_value("DESTINATION_SNOWFLAKE_PASSWORD"),
                "role":      get_secret_value("DESTINATION_SNOWFLAKE_ROLE"),
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