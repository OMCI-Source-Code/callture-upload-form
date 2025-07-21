from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from api.callture import post_download_calls, post_get_calls, post_login
from api.google_drive import setup_date_folders, upload_df_to_drive
from api.pandas_utility import parse_req_to_df, process_df
from api.errors import (TransferException, DownloadCallException, GetCallException, LoginFailedException, ParseException)

def create_app():
    app = Flask(__name__, static_folder='../public', static_url_path='')
    CORS(app)
    load_dotenv()


    @app.route('/')
    def form():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route("/login", methods=["POST"])
    def login():
        try:
            req = post_login()
            if req.status_code != 302:
                raise LoginFailedException("Login failed!", req)
        except LoginFailedException as e:
            return (jsonify({"error": str(e)}), e.response.status_code)


    @app.route("/upload", methods=["POST"])
    def upload():
        def json_error_check(req):
            try:
                return req.json()
            except Exception:
                return 'Something went wrong while fetching the data'
        data = request.get_json()
        line_no = data.get("lineNo")
        print("LINE NUMBEEER: ",line_no)
        ext_no = "All"
        date_range = data.get("dateRange")
        if len(line_no) == 8:
            line_no = "All"

        try:
            req = post_login()
            if req.status_code != 302:
                raise LoginFailedException("Login failed!", req)

            cookies = req.cookies
            req = post_get_calls(cookies, line_no, ext_no, date_range)
            if req.status_code != 200:
                raise GetCallException("Cannot retrieve call logs from Callture, " + json_error_check(req), req)

            req = post_download_calls(cookies)
            if req.status_code != 200:
                raise DownloadCallException("Cannot download call logs from Callture, " + json_error_check(req), req)

            df = parse_req_to_df(req)
            if df is None:
                raise ParseException("Failed to parse call log file to Excel")

        except LoginFailedException as e:
            return (jsonify({"error": str(e)}), e.response.status_code)
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
            upload_df_to_drive(df, day_id_map, True)

            # Sync
            # upload_df_to_drive(df, day_id_map)

            print(f"Uploading finished")

        except TransferException as e:
            print(e)
            return ({"message": str(e)}, 500)
        except Exception as e:
            return ({"message": str(e)}, 500)
        return (jsonify({"message": "Successfully uploaded"}), 200)
    return app
