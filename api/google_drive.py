
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account


def upload_to_drive(object_bytes, name, parent, mimetype):
  
  object_stream = BytesIO(object_bytes)
  
  SERVICE_ACCOUNT_FILE = "callture-service-key.json"
  SCOPES = ['https://www.googleapis.com/auth/drive.file']
  try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        "name": name,
        "parents": parent
    }
    media_stream = MediaIoBaseUpload(object_stream, mimetype=mimetype, resumable=True)
    # pylint: disable=maybe-no-member
    file = (
        service.files()
        .create(body=file_metadata, media_body=media_stream, fields="id")
        .execute()
    )
    print(f'File ID: {file.get("id")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.get("id")


if __name__ == "__main__":
  upload_basic()
    