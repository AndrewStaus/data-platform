import os
import unittest
from unittest.mock import patch

from dagster import EnvVar

from data_platform_utils import secrets


class TestSecrets(unittest.TestCase):
    def setUp(self):
        self.env_backup = dict(os.environ)
        self.secret_name = "TEST_SECRET"
        self.secret_value = "super_secret_value"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

    @patch("data_platform_utils.secrets.keyvault")
    def test_get_secret_sets_env_and_returns_envvar(self, mock_keyvault):
        # Arrange
        mock_keyvault.get_secret.return_value = self.secret_value

        # Act
        result = secrets.get_secret(self.secret_name)

        # Assert
        self.assertEqual(os.environ[self.secret_name], self.secret_value)
        self.assertIsInstance(result, EnvVar)
        self.assertEqual(result.get_value(), self.secret_value)
        mock_keyvault.get_secret.assert_called_once_with(self.secret_name)

    @patch("data_platform_utils.secrets.keyvault")
    def test_get_secret_value_returns_secret(self, mock_keyvault):
        # Arrange
        mock_keyvault.get_secret.return_value = self.secret_value

        # Act
        result = secrets.get_secret_value(self.secret_name)

        # Assert
        self.assertEqual(result, self.secret_value)
        mock_keyvault.get_secret.assert_called_once_with(self.secret_name)


if __name__ == "__main__":
    unittest.main()