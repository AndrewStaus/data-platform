import unittest
from unittest.mock import patch

import dagster as dg
from data_foundation.defs.sling.definitions import defs

FACTORY = "data_foundation.defs.sling.factory.Factory"

class TestDefs(unittest.TestCase):

    @patch(f"{FACTORY}.build_definitions")
    def test_defs(self, mock_build_definitions) -> None:

        mock_build_definitions.return_value = dg.Definitions()
        self.assertTrue(defs())


if __name__ == "__main__":
    unittest.main()