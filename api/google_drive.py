
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")


def get_service():
  
  SERVICE_ACCOUNT_FILE = "api/callture-service-key.json"
  SCOPES = ['https://www.googleapis.com/auth/drive.file']
  
  credentials = service_account.Credentials.from_service_account_file(
      SERVICE_ACCOUNT_FILE, scopes=SCOPES
  )
  service = build('drive', 'v3', credentials=credentials)
  return service

def upload_to_drive(object_bytes, name, mimetype, root_id=os.environ.get("ROOT_FOLDER")):
  
  object_stream = BytesIO(object_bytes)
  
  try:
    service = get_service()

    file_metadata = {
        "name": name,
        "parents": root_id
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

def drive_folder_exists(name, root_id=os.environ.get("ROOT_FOLDER")):
  try:
    service = get_service()
    
    # results = (
    #   service.files().list(
    #     q=f"name='{name}' and mimeType='application/vnd.google-apps.folder'", 
    #     driveId=root_id,
    #     corpora='drive',
    #     includeItemsFromAllDrives=True,
    #     supportsAllDrives=True
    #   ).execute()
    # )
    # print(f"file is {results["files"]}")
    
    query = f"parents = '{root_id}'"

    response = service.files().list(
      q=query, 
    ).execute()
    
    nextPageToken=response.get("nextPageToken")

    while nextPageToken:
      response = service.files().list(q=query).execute()
      files.extend(response.get('files'))
      nextPageToken=response.get("nextPageToken")

    print(response)
  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return response["files"]

if __name__ == "__main__":
  drive_folder_exists("test")
    