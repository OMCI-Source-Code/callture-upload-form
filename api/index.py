from flask import Flask
from callture import post_login, post_get_calls, post_download_calls
from utility import parse_req_to_ids

app = Flask(__name__)

download_path = "."

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/callture_login')
def login_page():
    req = post_login()
    cookies = req.cookies
    if req.status_code != 302:
        return "Failed"
    req = post_get_calls(cookies)
    req = post_download_calls(cookies)
    id_list = parse_req_to_ids(req)
    
    
    return "Succeeded"
    
    
    