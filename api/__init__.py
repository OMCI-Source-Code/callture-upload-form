from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from api.callture import post_download_calls, post_get_calls, post_login
from api.errors import TransferException
from api.google_drive import setup_date_folders, upload_df_to_drive
from api.pandas_utility import parse_req_to_df, process_df
from api.errors import (
    TransferException,
    DownloadCallException,
    GetCallException,
    LoginFailedException,
    ParseException,
)


def create_app():
    app = Flask(__name__, static_folder="../public", static_url_path="")
    CORS(app)
    load_dotenv()

    @app.route("/")
    def form():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/login", methods=["POST"])
    def login():
        pass

    @app.route("/upload", methods=["POST"])
    def upload():
        def json_error_check(req):
            try:
                return req.json()
            except Exception:

                return "Something went wrong while fetching the data"

        def process_info(line_no):
            try:
                req = post_get_calls(cookies, line_no, ext_no, date_range)
                if req.status_code != 200:
                    raise GetCallException(
                        "Cannot retrieve call logs from Callture, "
                        + json_error_check(req),
                        req,
                    )
                if "No Call Logs" in req.content.decode("utf-8", errors="ignore"):
                    print("No Call Logs, returning")
                    return
                req = post_download_calls(cookies)
                if req.status_code != 200:
                    raise DownloadCallException(
                        "Cannot download call logs from Callture, "
                        + json_error_check(req),
                        req,
                    )

                df = parse_req_to_df(req)
                if df is None:
                    raise ParseException("Failed to parse call log file to Excel")
            except GetCallException as e:
                print("Prematurely Exiting")
                return (jsonify({"error": str(e)}), e.response.status_code)
            except DownloadCallException as e:
                print("Prematurely Exiting")
                return (jsonify({"error": str(e)}), e.response.status_code)
            except ParseException as e:
                print("Prematurely Exiting")
                return (jsonify({"error": str(e)}), e.response.status_code)

            df = process_df(df)

            try:
                day_id_map = setup_date_folders(date_range)
                upload_df_to_drive(df, day_id_map)
                print(f"Uploading finished")

            except TransferException as e:
                print(e)
                return ({"message": str(e)}, 500)
            except Exception as e:
                return ({"message": str(e)}, 500)
            return (jsonify({"message": "Successfully uploaded"}), 200)

        data = request.get_json()
        line_no = data.get("lineNo")
        ext_no = "All"
        date_range = data.get("dateRange")
        if not line_no:
            return ({"message": "No line number selected"}, 500)
        try:
            req = post_login()
            if req.status_code != 302:
                raise LoginFailedException("Login failed!", req)
            cookies = req.cookies
        except LoginFailedException as e:
            return (e.response.json(), e.response.status_code)

        for line in line_no:
            print(f"Processing line.no {line}")
            processResponse = process_info(line)
        return processResponse

    return app
