import os

import flask_login
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory
from flask_cors import CORS

from api.callture import post_download_calls, post_get_calls, post_login
from api.errors import (
    DownloadCallException,
    GetCallException,
    LoginFailedException,
    ParseException,
    TransferException,
)
from api.google_drive import setup_date_folders, upload_df_to_drive
from api.pandas_utility import parse_req_to_df, process_df


def create_app():
    app = Flask(__name__, static_folder="../public", static_url_path="", template_folder="../templates")
    CORS(app)
    load_dotenv()

    app.secret_key = os.environ.get("SECRET_KEY")

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    class User(flask_login.UserMixin):
        def __init__(self, username, password):
            self.id = username
            self.password = password

    users = {
        os.environ.get("SITE_USERNAME"): User(
            os.environ.get("SITE_USERNAME"), os.environ.get("SITE_PASSWORD")
        )
    }

    @login_manager.user_loader
    def user_loader(id):
        return users.get(id)

    @app.get("/login")
    def login():
        return """<form method=post>
          Username: <input name="username"><br>
          Password: <input name="password" type=password><br> <br>
          <button>Log In</button>
        </form>"""

    @app.post("/login")
    def func_login():
        user = users.get(request.form["username"])

        if user is None or user.password != request.form["password"]:
            return redirect("login")

        flask_login.login_user(user)
        return redirect("/")

    @app.route("/")
    def form():
        if flask_login.current_user.is_authenticated:
            return send_from_directory(app.static_folder, "index.html")
        return render_template("msg_login_required.html")

    @app.route("/logout")
    def logout():
        flask_login.logout_user()
        return render_template("msg_logout.html")

    @app.route("/upload", methods=["POST"])
    def upload():
        def json_error_check(req):
            try:
                return req.json()
            except Exception:

                return "Something went wrong while fetching the data"

        data = request.get_json()
        line_no = data.get("lineNo")
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
                raise GetCallException(
                    "Cannot retrieve call logs from Callture, " + json_error_check(req),
                    req,
                )

            req = post_download_calls(cookies)
            if req.status_code != 200:
                raise DownloadCallException(
                    "Cannot download call logs from Callture, " + json_error_check(req),
                    req,
                )

            df = parse_req_to_df(req)
            if df is None:
                raise ParseException("Failed to parse call log file to Excel")

        except LoginFailedException as e:
            return (e.response.json(), e.response.status_code)
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

    return app
