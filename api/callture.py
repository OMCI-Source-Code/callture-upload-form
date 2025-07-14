import os
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

LOGIN_URL = "https://users.fibrehub.org/clnt"
CALL_LOG_URL = "https://users.fibrehub.org/clnt/Call/Logs"
DOWNLOAD_URL = f"https://users.fibrehub.org/FileHandler/downloadfile?TypeID=4&ClientID=${os.environ.get('CALLTURE_CLIENT_ID')}&LineNo=${os.environ.get('CALLTURE_LINE_NO')}&FileID="


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
        dateRange = formated_today + " - " + formated_today

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


def download_recording(recording_id):
    curr_file_url = DOWNLOAD_URL + str(recording_id)
    req = httpx.get(curr_file_url, timeout=10.0)
    return req
