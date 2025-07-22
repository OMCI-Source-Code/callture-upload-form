"""
callture.py

This module provides utilities for anything Callture related

Functions:
    post_login
    post_get_calls
    post_download_calls
    download_recording

Misc variables:


Author: Terry Luan
Date: 2025-07-14
"""

import os
from datetime import datetime

import httpx

from api.pandas_utility import PersonRow

LOGIN_URL = "https://users.fibrehub.org/clnt"
CALL_LOG_URL = "https://users.fibrehub.org/clnt/Call/Logs"
DOWNLOAD_URL = f"https://users.fibrehub.org/FileHandler/downloadfile?TypeID=4&ClientID={os.environ.get('CALLTURE_CLIENT_ID')}&LineNo="


def post_login():
    headers = {}
    form_data = {
        "UserName": os.environ.get("USERNAME"),
        "Password": os.environ.get("PASSWORD"),
    }
    req = httpx.post(LOGIN_URL, data=form_data, headers=headers, timeout=10.0)
    return req


def post_get_calls(cookies, line_no="All", ext_no="All", date_range=None):
    if not date_range:
        formated_today = datetime.now().strftime("%d %b %Y")
        date_range = formated_today + " - " + formated_today

    form_data = {
        "LineNo": line_no,
        "ExtNo": ext_no,
        "DateRange": date_range,
        "Button": "Search",
    }

    req = httpx.post(CALL_LOG_URL, data=form_data, cookies=cookies, timeout=10.0)
    return req


def post_download_calls(cookies):
    form_data = {"Button": "Download"}

    req = httpx.post(CALL_LOG_URL, data=form_data, cookies=cookies, timeout=10.0)
    return req


def download_recording(recording: PersonRow):
    print(f"Downloading {recording.CDRID}")
    line_number = recording.Line_No
    recording_id = recording.CDRID
    curr_file_url = DOWNLOAD_URL + str(line_number) + "&FileID=" + str(recording_id)
    req = httpx.get(curr_file_url, timeout=10.0)
    return req


async def a_download_recording(recording: PersonRow):
    print(f"Downloading {recording.CDRID}")
    line_number = recording.Line_No
    recording_id = recording.CDRID
    curr_file_url = DOWNLOAD_URL + str(line_number) + "&FileID=" + str(recording_id)
    try:
        async with httpx.AsyncClient() as client:
            req = await client.get(curr_file_url, timeout=100.0)
    except Exception as e:
        print(f"Exception is {e}")
    return req
