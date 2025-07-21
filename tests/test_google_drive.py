"""
test_flow.py

This module tests all initial callture functions to ensure they function correctly

Test methods:
    test_upload_login_fail
    test_upload_login_success
    test_single_line_upload
    test_multiple_line_upload

Author: Mame Mor Mbacke
Date: 2025-07-21
"""

import unittest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from api import create_app
from api.google_drive import (
    upload_to_drive,
    get_service,
    get_drive_folder,
    create_folder,
    upload_df_to_drive,
)
from api.pandas_utility import parse_req_to_df, process_df


class TestDrive(unittest.TestCase):

    def setUp(self):
        self.app = create_app().test_client()


class TestGoogleDriveFunctions(unittest.TestCase):
    @patch("api.google_drive.build")
    @patch("api.google_drive.get_service")
    def test_get_service(self, test_file, test_build):
        test_creds = MagicMock()
        test_file.return_value = test_creds

        test_service = MagicMock()
        test_build.return_value = test_service
        import api.google_drive as drive_module

        drive_module.service_account_file = ""  # Make fake file path
        drive_module.scopes = ["https://www.googleapis.com/auth/drive"]

        test_file.assert_called_once_with(
            "",
            scopes=[
                "https://www.googleapis.com/auth/drive"
            ],  # Make fake file put in first quotation marks next shift
        )
        test_build.assert_called_once_with("drive", "v3", credentials=test_creds)
        self.assertEqual(get_service(), test_service)

    @patch("api.google_drive.upload_to_drive")
    def test_upload_to_drive(self, fake_upload):
        pass

        upload_to_drive()

    def test_get_drive():
        pass

    def test_create_folder():
        pass

    def test_upload_df():
        pass
