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
from api import (
    post_login,
    create_app,
    post_get_calls,
    post_download_calls,
    setup_date_folders,
)
from api.callture import a_download_recording, download_recording
from api.google_drive import upload_df_to_drive
from api.pandas_utility import parse_req_to_df, process_df


class TestUpload(unittest.TestCase):

    def setUp(self):
        self.app = create_app().test_client()

    @patch("api.post_login")
    def test_upload_login_fail(self, fake_login):
        test_response = MagicMock()
        test_response.status_code = 500
        test_response.json.return_value = {"error": "Login failed!"}
        fake_login.return_value = test_response

        response = self.app.post("/login")
        self.assertEqual(response.status_code, 500)

        response = self.app.post(
            "/upload",
            json={"lineNo": "12345678", "dateRange": "2000-01-01 to 2025-12-31"},
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Login failed", response.get_data(as_text=True))

    @patch("api.post_login")
    def test_upload_login_success(self, fake_login):
        test_response = MagicMock()
        test_response.status_code = 302
        fake_login.return_value = test_response

        response = post_login()
        self.assertEqual(response.status_code, 302)

        response = self.app.post("/upload", json={"lineNo": "All", "dateRange": "All"})

        self.assertEqual(response.status_code, 302)

    def test_single_line_upload(self):

        lineNo = "All"
        extNo = "All"
        dateRange = "07 Jul 2025 - 10 Jul 2025"

        testBody = {
            "dateRange": dateRange,
            "lineNo": "5",
        }

        req = post_login()
        cookies = req.cookies
        req = post_get_calls(cookies, lineNo, extNo, dateRange)
        req = post_download_calls(cookies)

        self.app.post("/upload", json=testBody)
        print(testBody.get("lineNo"))
        # self.assertEqual(response.status_code, 200)

    def test_multiple_line_upload(self):

        lineNo = ["2", "5"]
        extNo = "All"
        dateRange = "07 Jul 2025 - 10 Jul 2025"

        testBody = {"dateRange": dateRange, "lineNo": ["2", "5"]}

        req = post_login()
        cookies = req.cookies
        req = post_get_calls(cookies, lineNo, extNo, dateRange)
        req = post_download_calls(cookies)

        self.app.post("/upload", json=testBody)
        print(testBody.get("lineNo"))
        # self.assertEqual(response.status_code, 200)
