"""Minimal stub that emulates the subset of Azure Key Vault functionality used."""
from dotenv import find_dotenv


class SecretClient:
    """A stub keyvault to simulate an integration with Azure Keyvault. This would be
    replaced by a keyvault library.
    """

    def get_secret(self, secret_name: str) -> str:
        """returns a secret from the keyvault"""
        secrets = self.__secrets
        location, _, attribute = secret_name.split("__")
        secret = secrets.get(location, {}).get(attribute)

        return secret or ""

    def __init__(
        self, vault_url: str | None = None, credential: str | None = None
    ) -> None:
        secrets = {"SOURCE": {}, "DESTINATION": {}}
  
        if env_path := find_dotenv(usecwd=True):

            with open(env_path) as env:
                for line in env:
                    line = line.strip()
                    if line:
                        key, value = line.split("=")
                        keys = key.split("__")
                        if len(keys) == 2:
                            location, attribute = keys
                            secrets[location][attribute] = value

        self.__secrets = secrets
