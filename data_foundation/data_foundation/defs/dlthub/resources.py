from dagster import Definitions
from dagster.components import definitions


@definitions
def defs() -> Definitions:
    """Returns set of definitions explicitly available and loadable by Dagster tools.
    Will be automatically dectectd and loaded by the load_defs function in the root
    definitions file.

    Assets and asset checks for dltHub are defined in the dlthub subfolder in the
    definitions.py file for each resource.

    @definitions decorator will provides lazy loading so that the assets are only
    instantiated when needed.
    """
    import os

    import dagster as dg
    from dagster_dlt import DagsterDltResource

    from ...utils.keyvault_stub import SecretClient

    kv = SecretClient(
        vault_url=os.getenv("AZURE_KEYVAULT_URL"),
        credential=os.getenv("AZURE_KEYVAULT_CREDENTIAL"),
    )

    os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__HOST"] = kv.get_secret(
        "DESTINATION__SNOWFLAKE__HOST"
    )
    os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME"] = kv.get_secret(
        "DESTINATION__SNOWFLAKE__USER"
    )
    os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__PASSWORD"] = kv.get_secret(
        "DESTINATION__SNOWFLAKE__PASSWORD"
    )
    os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__DATABASE"] = kv.get_secret(
        "DESTINATION__SNOWFLAKE__DATABASE"
    )
    os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__ROLE"] = kv.get_secret(
        "DESTINATION__SNOWFLAKE__ROLE"
    )
    os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__WAREHOUSE"] = kv.get_secret(
        "DESTINATION__SNOWFLAKE__WAREHOUSE"
    )

    os.environ["ENABLE_DATASET_NAME_NORMALIZATION"] = "false"

    return dg.Definitions(resources={"dlt": DagsterDltResource()})
