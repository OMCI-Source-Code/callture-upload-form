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
    """
    Raised when there is an error transferring a call recording.

    Attributes:
        response: ID of the recording that caused the exception or nothing.
    """

    recording_id: int | None

    def __init__(self, message, recording_id=None):
        super().__init__(message)
        self.recording_id = recording_id


# Cannot login to Callture account


class LoginFailedException(Exception):
    """
    Raised when login to the Callture account fails.

    Attributes:
        response: Optional HTTP or response object related to the failure.
    """

    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


# Call logs cannot be retrieved from Callture
class GetCallException(Exception):
    """
    Raised when call logs cannot be retrieved from Callture.

    Attributes:
        response: Optional HTTP or API response object related to the error.
    """

    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


# Calls cannot be downloaded


class DownloadCallException(Exception):
    """
    Raised when there is an error downloading call recordings.

    Attributes:
        response: Optional HTTP or response object related to the error.
    """

    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)


# When parsing call logs file to Excel returns an error
class ParseException(Exception):
    """
    Raised when there is an error parsing the call logs into Excel format.

    Attributes:
        response: Optional data or object providing details of the parse failure.
    """

    def __init__(self, message, response=None):
        self.response = response
        super().__init__(message)
