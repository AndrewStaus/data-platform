import unittest
from unittest.mock import MagicMock, patch

import dagster as dg
from data_science.defs.snowpark.resources import SnowparkResource, defs


class TestResources(unittest.TestCase): ...


class TestGetSessionWithAllParams(TestResources):

    @patch("data_platform_utils.secrets.get_secret_value")
    @patch("data_platform_utils.helpers.get_database_name")
    @patch("data_platform_utils.helpers.get_schema_name")
    @patch("snowflake.snowpark.Session")
    def test_returns_session_and_sets_schema(
        self, mock_session_class, mock_get_schema_name,
        mock_get_database_name, mock_get_secret_value
    ):
        mock_session = MagicMock()
        mock_session_class.builder.configs.return_value.create.return_value = mock_session
        mock_get_database_name.return_value = "test_db"
        mock_get_schema_name.return_value = "test_schema"
        mock_get_secret_value.side_effect = [
            "user", "warehouse", "host", "user", "password", "role"
        ]

        resource = SnowparkResource()
        session = resource.get_session(
            database="test_db",
            schema="test_schema",
            warehouse="test_warehouse"
        )

        self.assertEqual(session, mock_session)
        mock_session.use_schema.assert_called_once_with("test_schema")


class TestGetSessionCreatesSchema(TestResources):

    @patch("data_platform_utils.secrets.get_secret_value")
    @patch("data_platform_utils.helpers.get_database_name")
    @patch("data_platform_utils.helpers.get_schema_name")
    @patch("snowflake.snowpark.Session")
    def test_creates_schema_if_not_exists(
                self,
                mock_session_class,
                mock_get_schema_name,
                mock_get_database_name,
                mock_get_secret_value,
            ):
        mock_session = MagicMock()
        mock_session.use_schema.side_effect = [Exception("missing"), None]
        mock_session_class.builder.configs.return_value.create.return_value = mock_session

        mock_get_database_name.return_value = "test_db"
        mock_get_schema_name.return_value = "test_user"
        mock_get_secret_value.side_effect = [
            "user", "warehouse", "host", "user", "password", "role"
        ]

        resource = SnowparkResource()
        session = resource.get_session(database="test_db")

        self.assertEqual(session, mock_session)
        self.assertEqual(mock_session.use_schema.call_count, 2)

class TestGetSessionWithDefaults(TestResources):

    @patch("data_platform_utils.secrets.get_secret_value")
    @patch("data_platform_utils.helpers.get_database_name")
    @patch("snowflake.snowpark.Session")
    def test_uses_defaults_when_params_not_provided(
        self, mock_session_class, mock_get_database_name, mock_get_secret_value
    ):
        mock_session = MagicMock()
        mock_session_class.builder.configs.return_value.create.return_value = mock_session
        mock_get_database_name.return_value = "default_db"
        mock_get_secret_value.side_effect = [
            "user", "warehouse", "host", "user", "password", "role"
        ]

        resource = SnowparkResource()
        session = resource.get_session()

        self.assertEqual(session, mock_session)


class TestDefs(TestResources):

    def test_defs_returns_definition(self):
        self.assertIsInstance(defs(), dg.Definitions)



if __name__ == "__main__":
    unittest.main()
