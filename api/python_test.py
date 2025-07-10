import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account


def upload_basic():
  """Insert new file.
  Returns : Id's of the file uploaded

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  
  SERVICE_ACCOUNT_FILE = "callture-service-key.json"
#   SCOPES = ['/home/luanterr/cmc/callture-backend/api/callture-service-key.json']
  SCOPES = ['https://www.googleapis.com/auth/drive.file']
  FOLDER_ID = "14aQz6OvPyb9UY4KfBbJP9vrl9eqZ3dJx"
  try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        "name": "download.text",
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload("download.text", mimetype="audio/mpeg")
    # pylint: disable=maybe-no-member
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    print(f'File ID: {file.get("id")}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.get("id")


if __name__ == "__main__":
  upload_basic()