

class TransferException(Exception):
    recording_id: int | None

    def __init__(self, message, recording_id=None):
        super().__init__(message)
        self.recording_id = recording_id