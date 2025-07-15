from flask import Flask, jsonify, request
from flask_cors import CORS

from api.callture import post_download_calls, post_get_calls, post_login
from api.google_drive import setup_date_folders, upload_df_to_drive
from api.pandas_utility import parse_req_to_df, process_df
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()


@app.route("/login", methods=["POST"])
def login():
    pass


@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    line_no = data.get("lineNo")
    ext_no = "All"
    date_range = data.get("dateRange")
    if len(line_no) == 8:
        line_no = "All"

    req = post_login()
    cookies = req.cookies
    if req.status_code != 302:
        print("Prematurely exiting")
        return (req.json(), req.status_code)
    req = post_get_calls(cookies, line_no, ext_no, date_range)
    req = post_download_calls(cookies)

    df = parse_req_to_df(req)
    df = process_df(df)

    try:
        day_id_map = setup_date_folders(date_range)
        folder_id = upload_df_to_drive(df, day_id_map)
        print(f"uploaded {folder_id}")

    except Exception as e:
        print(e)
        return ({"error": str(e)}, 401)
    return (jsonify({"message": "Successfully uploaded"}), 200)
