class TransferException(Exception):
    recording_id: int | None

    def __init__(self, message, recording_id=None):
        super().__init__(message)
        self.recording_id = recording_id
        
class LoginFailedException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)

class GetCallException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)

class DownloadCallException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)

class ParseException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)

