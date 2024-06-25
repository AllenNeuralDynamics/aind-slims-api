"""Tests methods in configuration module"""

import os
import unittest
from unittest.mock import patch

from aind_slims_api.configuration import AindSlimsApiSettings


class TestAindSlimsApiSettings(unittest.TestCase):
    """Tests methods in AindSlimsApiSettings class"""

    @patch.dict(
        os.environ,
        {},
        clear=True,
    )
    def test_default_settings(self):
        """Tests that the class will be set with defaults"""
        default_settings = AindSlimsApiSettings()

        self.assertEqual(
            "https://aind-test.us.slims.agilent.com/slimsrest/",
            default_settings.slims_url,
        )
        self.assertEqual("", default_settings.slims_username)
        self.assertEqual("", default_settings.slims_password.get_secret_value())

    @patch.dict(
        os.environ,
        {
            "SLIMS_URL": "https://aind.us.slims.agilent.com/slimsrest/",
            "SLIMS_PASSWORD": "password2",
            "SLIMS_USERNAME": "user2",
        },
        clear=True,
    )
    def test_settings_from_env_vars(self):
        """Tests that the class can be set from env vars"""
        default_settings = AindSlimsApiSettings()

        self.assertEqual(
            "https://aind.us.slims.agilent.com/slimsrest/", default_settings.slims_url
        )
        self.assertEqual("user2", default_settings.slims_username)
        self.assertEqual(
            "password2", default_settings.slims_password.get_secret_value()
        )


if __name__ == "__main__":
    unittest.main()
