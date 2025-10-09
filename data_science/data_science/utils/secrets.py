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
    used securly with dagsters EnvVar class.
    """
    if secret := keyvault.get_secret(env_var_name):
        os.environ[env_var_name] = secret
        return dg.EnvVar(env_var_name)

    raise ValueError(
        f"Secret for key '{env_var_name}' not found."
        "Please check that this is the correct key."
    )
