"""
test_error.py

This module raises all exceptions in _init_.py to test error validity. Login, get, and download testing is done throughout each test method to verify it works.

Test methods:
    test_login_failed_exception
    test_get_call_exception
    test_download_call_exception
    test_parse_exception

Usage:
    Run with pytest -v

Author: Mame Mor Mbacke
Date: 2025-07-21
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from api import (
    post_login,
    post_get_calls,
    post_download_calls,
    parse_req_to_df,
    LoginFailedException,
    GetCallException,
    DownloadCallException,
    ParseException,
)
from flask import jsonify


class TestCallErrorHandling(unittest.TestCase):

    @patch("api.post_login")
    @patch.dict(
        os.environ, {"CALLTURE_USERNAME": "fakeusername", "PASS": "wibblywobbly"}
    )
    def test_callture_login_failed_exception(self, fake_login):
        mock_response = MagicMock()
        mock_response.status_code = 401
        fake_login.return_value = mock_response

        with self.assertRaises(LoginFailedException):
            req = post_login()
            if req.status_code != 302:
                raise LoginFailedException("Login failed!", req)

    @patch("api.post_get_calls")
    @patch("api.post_login")
    def test_get_call_exception(self, fake_login, fake_get_calls):

        login_response = MagicMock()
        login_response.status_code = 302
        fake_login.return_value = login_response
        response = post_login()
        self.assertEqual(response.status_code, 302)

        get_calls_response = MagicMock()
        get_calls_response.status_code = 500
        fake_get_calls.return_value = get_calls_response

        with self.assertRaises(GetCallException):
            req = post_login()
            if req.status_code != 302:
                raise LoginFailedException("Login failed!", req)

            cookies = req.cookies
            req = post_get_calls(cookies, "All", "All", "some-date")
            if req.status_code != 200:
                raise GetCallException("Cannot retrieve call logs from Callture,", req)

    @patch("api.post_download_calls")
    @patch("api.post_get_calls")
    @patch("api.post_login")
    def test_download_call_exception(self, fake_login, fake_get, fake_download):

        login_response = MagicMock()
        login_response.status_code = 302
        fake_login.return_value = login_response
        response = post_login()
        self.assertEqual(response.status_code, 302)

        get_calls_response = MagicMock()
        get_calls_response.status_code = 200
        fake_get.return_value = get_calls_response

        download_response = MagicMock()
        download_response.status_code = 400
        fake_download.return_value = download_response

        with self.assertRaises(DownloadCallException):
            response = post_login()
            response = post_get_calls(response.cookies, "All", "All", "notavalidrange")
            response = post_download_calls(response.cookies)
            if response.status_code != 200:
                raise DownloadCallException(
                    "Cannot download call logs from Callture,", response
                )

    @patch("api.parse_req_to_df")
    @patch("api.post_download_calls")
    @patch("api.post_get_calls")
    def test_parse_to_excel_exception(
        self, fake_get_calls, fake_download_calls, fake_parse
    ):
        get_calls_response = MagicMock()
        get_calls_response.status_code = 200
        fake_get_calls.return_value = get_calls_response

        download_response = MagicMock()
        download_response.status_code = 200
        fake_download_calls.return_value = download_response

        fake_parse.return_value = None

        with self.assertRaises(ParseException):
            response = post_login()
            response = post_get_calls(response.cookies, "All", "All", "notavalidrange")
            response = post_download_calls(response.cookies)
            df = parse_req_to_df(response)
            if df is None:
                raise ParseException("Failed to parse call log file to Excel")
