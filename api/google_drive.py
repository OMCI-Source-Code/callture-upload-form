
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
    
    query = f"'{root_id}' in parents"

    response = service.files().list(
      q=query, 
    ).execute()

    print(response)
  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return response["files"]

def create_folder_path(path: str, root_id: str=os.environ.get("ROOT_FOLDER")):
  """Create a folder path in G-Drive, given the root id, and path

  Args:
      path (str): the path to create
      root_id (str): ID of the root folder

  Returns:
      {id: str, name: str}: the very last folder created
  """
  path = path.split("/")
  
  current_parent_id = root_id
  folder = None
  for current_folder in path:
    folder = create_folder(current_folder, current_parent_id)
    print("")
    current_parent_id = folder.get("id")
  print(f"Last folder is {folder}")
  return folder
    
    

def create_folder(name, parent_id):
  service = get_service()
  folder_metadata = {
    'name': name,
    'mimeType': 'application/vnd.google-apps.folder',
    'parents': [parent_id]
  }
  
  try:
    file = (
          service.files()
          .create(body=folder_metadata, fields="id, name", supportsAllDrives=True)
          .execute()
      )
  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None
  return file

if __name__ == "__main__":
  create_folder_path("TEST2/test")
    