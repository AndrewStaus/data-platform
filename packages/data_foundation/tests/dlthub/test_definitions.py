import os
import unittest
from unittest.mock import patch

import dagster as dg
from data_foundation.defs.dlthub.definitions import defs

FACTORY = "data_foundation.defs.dlthub.factory.Factory"

class TestDefs(unittest.TestCase):

    @patch("data_platform_utils.keyvault_stub.SecretClient.get_secret")
    @patch(f"{FACTORY}.build_definitions")
    def test_defs(self, mock_build_definitions, mock_get_secret) -> None:

        mock_get_secret.return_value = "x"
        mock_build_definitions.return_value = dg.Definitions()
        
        defs()

        host = os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__HOST")
        username = os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME")
        password = os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__PASSWORD")
        database = os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__DATABASE")
        role = os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__ROLE")
        warehouse = os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__WAREHOUSE")

        self.assertEqual(host, "x")
        self.assertEqual(username, "x")
        self.assertEqual(password, "x")
        self.assertEqual(database, "x")
        self.assertEqual(role, "x")
        self.assertEqual(warehouse, "x")