import dagster as dg
from dagster.components import definitions


class SnowparkResource(dg.ConfigurableResource):
    """Resource class for managing Snowpark sessions"""

    def __init__(self, **kwargs) -> None:     
        super().__init__(**kwargs)
        self._session = None

    def get_session(self, database="analytics",
                    schema: str | None = None,
                    warehouse: str|None = None) -> "snowflake.snowpark.Session":  # type: ignore # noqa
        """Get or create a Snowpark session"""
        import os
        import sys

        from snowflake.snowpark import Session

        from ...utils.helpers import get_database_name, get_schema_name

        if sys.platform == "win32":
            import pathlib
            pathlib.PosixPath = pathlib.PurePosixPath

        if schema:
            schema = get_schema_name(schema)
        else:
            schema = os.getenv("DESTINATION__USER", "")

        
        if not warehouse:
            warehouse = os.getenv("DESTINATION__WAREHOUSE", "")

        self._session = (
            Session.builder.configs({ 
                "database":  get_database_name(database),
                "account":   os.getenv("DESTINATION__HOST", ""),
                "user":      os.getenv("DESTINATION__USER", ""),
                "password":  os.getenv("DESTINATION__PASSWORD", ""),
                "role":      os.getenv("DESTINATION__ROLE", ""),
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