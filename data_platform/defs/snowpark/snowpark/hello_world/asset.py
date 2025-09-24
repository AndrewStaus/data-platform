from typing import Any

import dagster as dg
from snowflake.snowpark.session import Session


def materialize(
        session: Session,
        context: dg.AssetExecutionContext,
        ) -> dict[str, Any]:
    
    context.log.info("hello world")
    
    return {}