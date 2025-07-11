from flask import Flask, request, jsonify
from flask_cors import CORS
from api.callture import post_login, post_get_calls, post_download_calls
from api.pandas_utility import parse_req_to_df, process_df
from api.google_drive import upload_df_to_drive

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=["POST"])
def login():
    pass

@app.route('/upload', methods=["POST"])
def upload():
    data = request.get_json()
    lineNo = data.get("lineNo")
    extNo = "All"
    dateRange = data.get("dateRange")
    if len(lineNo) == 8:
        lineNo = "All"
    
    req = post_login()
    cookies = req.cookies
    if req.status_code != 302:
        print("Prematurely exiting")
        return (req.json() , req.status_code)
    req = post_get_calls(cookies, lineNo, extNo, dateRange)
    req = post_download_calls(cookies)
    
    df = parse_req_to_df(req)
    df = process_df(df)
    
    try:
        upload_df_to_drive(df)
    except Exception as e:
        print(e)
        return ({"error": str(e)}, 401)
    return (jsonify({"message": "Successfully uploaded"}), 200)