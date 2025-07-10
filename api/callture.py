
from dotenv import load_dotenv
import os
import httpx
from datetime import datetime

load_dotenv(dotenv_path=".env.local")

login_url = "https://users.fibrehub.org/clnt"
def post_login():
    headers = {}
    form_data = { "UserName": os.environ.get("USERNAME"), "Password": os.environ.get("PASSWORD")}
    req = httpx.post(login_url, data=form_data, headers=headers, timeout=10.0)
    return req

call_log_url = "https://users.fibrehub.org/clnt/ExtCall/Logs"
def post_get_calls(cookies, lineNo="All", extNo="All", dateRange=None):
    if not dateRange:
        formated_today = datetime.now().strftime("%d %b %Y")
        dateRange = formated_today + " - " + formated_today
    
    form_data = {
        "LineNo": lineNo,
        "ExtNo": extNo,
        "DateRange": dateRange,
        "Button": "Search"
    }
        
    req = httpx.post(call_log_url, data=form_data, cookies=cookies, timeout=10.0)
    return req

normal_call_log_url = "https://users.fibrehub.org/clnt/Call/Logs"
def post_download_calls(cookies):
    form_data = {
        "Button": "Download"
    }
        
    req = httpx.post(call_log_url, data=form_data, cookies=cookies, timeout=10.0)
    return req

download_file_url = f"https://users.fibrehub.org/FileHandler/downloadfile?TypeID=4&ClientID=${os.environ.get('CALLTURE_CLIENT_ID')}&LineNo=${os.environ.get('CALLTURE_LINE_NO')}&FileID="
def download_recording(recording_id):
    curr_file_url = download_file_url + str(recording_id)
    req = httpx.get(curr_file_url, timeout=10.0)
    return req