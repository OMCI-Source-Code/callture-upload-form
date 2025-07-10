from flask import Flask
from callture import post_login, post_get_calls, post_download_calls
from api.pandas_utility import parse_req_to_df, process_df
import pandas as pd

app = Flask(__name__)

@app.route('/callture_login')
def login_page():
    req = post_login()
    cookies = req.cookies
    if req.status_code != 302:
        return "Failed"
    req = post_get_calls(cookies)
    req = post_download_calls(cookies)
    
    df = parse_req_to_df(req)
    df = process_df(df)
    
    for recording in df.head(5).itertuples():
        
        print(f"recording: {recording}")
    
    
    return "Succeeded"