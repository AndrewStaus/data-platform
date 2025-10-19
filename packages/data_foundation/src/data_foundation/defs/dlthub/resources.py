"""Resource definitions for dltHub integrations."""

import os
from pathlib import Path

from dagster import Definitions
from dagster.components import definitions
from data_platform_utils.keyvault_stub import SecretClient

from .factory import Factory


@definitions
def defs() -> Definitions:
    """Instantiate the dltHub resources required by the Dagster definitions.

    Returns:
        dagster.Definitions: Definitions exposing the ``dlt`` resource configured with
            credentials sourced from the local key vault stub. The helper ensures
            environment variables expected by dlt are populated before constructing the
            resource.
    """
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
    
    # Resolve the root folder containing dlt configuration files and scripts.
    config_dir = Path(__file__).joinpath(*[".."], "dlthub").resolve()

    return Factory.build_definitions(config_dir)
