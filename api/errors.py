"""
errors.py

This module contains error handler classes used throughout the API folder

Classes:
    TransferException
    LoginFailedException
    GetCallException
    DownloadCallException
    ParseException

Author: Terry Luan
Created On: 2025-07-16
Updated: 2025-07-17
"""


class TransferException(Exception):
    recording_id: int | None

    def __init__(self, message, recording_id=None):
        super().__init__(message)
        self.recording_id = recording_id


# Cannot login to Callture account
class LoginFailedException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


# Call logs cannot be retrieved from Callture
class GetCallException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


# Calls cannot be downloaded
class DownloadCallException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


# When parsing call logs file to Excel returns an error
class ParseException(Exception):
    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)
