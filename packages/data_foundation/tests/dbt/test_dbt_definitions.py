import unittest
from unittest.mock import patch

import dagster as dg
from data_foundation.defs.dbt.definitions import defs

FACTORY = "data_foundation.defs.dbt.factory.Factory"

class TestDefinitions(unittest.TestCase):

    @patch("dagster_dbt.DbtProject.__init__")
    @patch(f"{FACTORY}.build_definitions")
    def test_defs(self, mock_build_definitions, mock_dbt_project_init):
        mock_build_definitions.return_value = dg.Definitions()
        self.assertIsNotNone(defs())


if __name__ == "__main__":
    unittest.main()