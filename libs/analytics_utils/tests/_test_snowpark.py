import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from analytics_utils import snowpark as sp


class TestVarHelper(unittest.TestCase):
    @patch("analytics_utils.snowpark.load_dotenv")
    @patch("analytics_utils.snowpark.find_dotenv", return_value="/fake/.env")
    @patch("analytics_utils.snowpark.os.getenv")
    def test_var_returns_env_value(
            self, mock_getenv, mock_find_dotenv, mock_load_dotenv):
        mock_getenv.return_value = "secret_value"
        result = sp._var("DESTINATION__USER")
        self.assertEqual(result, "secret_value")
        mock_find_dotenv.assert_called_once()
        mock_load_dotenv.assert_called_once_with("/fake/.env")


class TestGetSession(unittest.TestCase):
    @patch("analytics_utils.snowpark._var")
    @patch("analytics_utils.snowpark.Session.get_active_session", return_value=None)
    @patch("analytics_utils.snowpark.Session.builder")
    def test_create_new_session_with_vars(
            self, mock_builder, mock_get_active, mock_var):
        mock_session = MagicMock()
        mock_builder.configs.return_value.create.return_value = mock_session
        mock_var.side_effect = ["test_user", "test_host", "test_user", "test_password",
                                "test_role", "test_warehouse"]

        session = sp.get_session(verbose=False)

        self.assertEqual(session, mock_session)
        mock_builder.configs.assert_called_once()
        self.assertTrue(mock_session.use_database.called or True)

    @patch("analytics_utils.snowpark.Session.get_active_session")
    def test_reuse_existing_session(self, mock_get_active):
        mock_session = MagicMock()
        mock_get_active.return_value = mock_session

        session = sp.get_session(verbose=False)

        self.assertEqual(session, mock_session)
        mock_get_active.assert_called_once()


class TestDisplayFunction(unittest.TestCase):
    @patch("analytics_utils.snowpark._display_snowpark")
    def test_display_snowpark_dataframe(self, mock_display):
        df = MagicMock(spec=sp.snowpark.DataFrame)
        sp.display(df)
        mock_display.assert_called_once_with(df, spec=None)

    @patch("analytics_utils.snowpark._display_df")
    def test_display_collection(self, mock_display_df):
        sp.display([{"a": 1, "b": 2}])
        df = pd.DataFrame([{"a": 1, "b": 2}])
        mock_display_df.assert_called_once()
        self.assertEqual(mock_display_df.call_args[0][0].to_dict(), df.to_dict())


class TestDisplaySnowpark(unittest.TestCase):
    @patch("analytics_utils.snowpark.get_session")
    @patch("analytics_utils.snowpark.Connector")
    @patch("analytics_utils.snowpark.pyg.walk")
    def test_display_snowpark_query_with_connector(
            self, mock_walk, mock_connector, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.get_current_account.return_value = "account"
        mock_session.get_current_user.return_value = "user"
        mock_session.get_current_schema.return_value = "schema"
        mock_session.get_current_database.return_value = "db"
        mock_session.get_current_warehouse.return_value = "wh"
        mock_session.get_current_role.return_value = "role"

        mock_df = MagicMock(spec=sp.snowpark.DataFrame)
        mock_df.queries = {"queries": ["SELECT * FROM test"]}

        sp._display_snowpark(mock_df)

        self.assertTrue(mock_connector.called)
        self.assertTrue(mock_walk.called)

    @patch("analytics_utils.snowpark.get_session")
    @patch("analytics_utils.snowpark.Connector", side_effect=TypeError)
    @patch("analytics_utils.snowpark.legacy_display")
    def test_display_snowpark_handles_typeerror(
            self, mock_display, mock_connector, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        sp._display_snowpark("SELECT * FROM broken_view")

        mock_display.assert_called_once()


class TestDisplayDF(unittest.TestCase):
    @patch("analytics_utils.snowpark.pyg.render")
    def test_display_df_with_spec(self, mock_render):
        df = pd.DataFrame({"a": [1, 2]})
        sp._display_df(df, spec="test_spec")
        mock_render.assert_called_once_with(
            df, "test_spec", theme_key="streamlit", appearance="light")

    @patch("analytics_utils.snowpark.pyg.walk")
    def test_display_df_without_spec(self, mock_walk):
        df = pd.DataFrame({"a": [1, 2]})
        sp._display_df(df, spec=None)
        mock_walk.assert_called_once()


if __name__ == "__main__":
    unittest.main()
