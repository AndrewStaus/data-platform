"""A wrapper for a keyvault to integrate with the Dagster EnvVar class for secure
secret usage in dagster.
"""
import os

import dagster as dg

from .keyvault_stub import SecretClient

keyvault = SecretClient(
    vault_url=dg.EnvVar("AZURE_KEYVAULT_URL"),
    credential=dg.EnvVar("AZURE_KEYVAULT_CREDENTIAL"),
)


def get_secret(env_var_name: str) -> dg.EnvVar:
    """A wrapper for a keyvault to integrate with the Dagster EnvVar class.

    Returns a secret from the keyvault and set it to an environment variable that can be
    used securely with dagster's EnvVar class.
    """
    secret = keyvault.get_secret(env_var_name)
    os.environ[env_var_name] = secret
    return dg.EnvVar(env_var_name)


def get_secret_value(env_var_name: str) -> str:
    """A wrapper for a keyvault to integrate with the Dagster EnvVar class.

    Returns a secret from the keyvault and set it to an environment variable that can be
    used securely with dagster's EnvVar class.
    """
    return keyvault.get_secret(env_var_name)

def set_dlt_credentials() -> None:
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