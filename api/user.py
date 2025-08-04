import flask_login

class User(flask_login.UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password