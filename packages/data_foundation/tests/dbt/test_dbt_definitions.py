import unittest
from unittest.mock import Mock, patch

import dagster as dg
from data_foundation.defs.dbt.definitions import defs

FACTORY = "data_foundation.defs.dbt.factory.Factory"

class TestDefinitions(unittest.TestCase):

    @patch(f"{FACTORY}.build_definitions")
    def test_defs(self, mock_build_definitions: Mock):
        mock_build_definitions.return_value = dg.Definitions()
        defs()
        mock_build_definitions.assert_called_once()
        args, kwargs = mock_build_definitions.call_args
        dbt_project = args[0]()
        self.assertIsNotNone(dbt_project)


if __name__ == "__main__":
    unittest.main()