from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from api.callture import post_download_calls, post_get_calls, post_login
from api.google_drive import setup_date_folders, upload_df_to_drive
from api.pandas_utility import parse_req_to_df, process_df

def create_app():
    app = Flask(__name__, static_folder='../public', static_url_path='')
    CORS(app)
    load_dotenv()


    @app.route('/')
    def form():
        return send_from_directory(app.static_folder, 'index.html')

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
