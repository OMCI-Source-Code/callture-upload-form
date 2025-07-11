from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")


def upload_basic():
  """Insert new file.
  Returns : Id's of the file uploaded

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  
  SERVICE_ACCOUNT_FILE = "api/callture-service-key.json"
#   SCOPES = ['/home/luanterr/cmc/callture-backend/api/callture-service-key.json']
  SCOPES = ['https://www.googleapis.com/auth/drive.file']
  FOLDER_ID = os.environ.get("ROOT_FOLDER")
  try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        "name": "TEST.txt",
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload("api/TEST1.txt", mimetype="audio/mpeg")
    # pylint: disable=maybe-no-member
    file = (
        service.files()
        .create(body=file_metadata,
                media_body=media, 
                fields="id",
                supportsAllDrives=True)
        .execute()
    )

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.get("id")


if __name__ == "__main__":
  upload_basic()