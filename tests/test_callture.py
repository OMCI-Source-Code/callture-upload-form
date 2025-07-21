"""
test_callture.py

This module tests all initial callture functions to ensure they function correctly

Test methods:
    test_fail
    test_success
    test_get_calls
    test_parse_exception
    test_download_calls

Author: Mame Mor Mbacke
Date: 2025-07-17
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from api import post_login, create_app, post_get_calls, post_download_calls
from api.callture import a_download_recording, download_recording


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.app = create_app().test_client()

    @patch("api.post_login")
    @patch.dict(
        os.environ, {"CALLTURE_USERNAME": "fakeusername", "PASS": "wibblywobbly"}
    )
    def test_fail(self, fake_login):
        test_response = MagicMock()
        test_response.status_code != 302
        fake_login.return_value = test_response

        response = post_login()
        print(response.status_code)

        self.assertNotEqual(response.status_code, 302)

    @patch("api.post_login")
    def test_success(self, fake_login):
        test_response = MagicMock()
        test_response.status_code = 302
        fake_login.return_value = test_response
        response = post_login()

        self.assertEqual(response.status_code, 302)


class TestCalls(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()

    @patch("api.post_get_calls")
    def test_get_calls(self, fake_login):
        test_response = MagicMock()
        test_response.status_code = 200
        fake_login.return_value = test_response
        lineNo = "All"
        extNo = "All"
        dateRange = "07 Jul 2025 12:00 AM - 10 Jul 2025 12:00 AM"

        response = post_login()
        response = post_get_calls(response.cookies, lineNo, extNo, dateRange)

        self.assertEqual(response.status_code, 200)

    @patch("api.post_download_calls")
    def test_download_calls(self, fake_login):
        test_response = MagicMock()
        test_response.status_code = 200
        fake_login.return_value = test_response

        response = post_login()
        response = post_download_calls(response.cookies)

        self.assertEqual(response.status_code, 200)
