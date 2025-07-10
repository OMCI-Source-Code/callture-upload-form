
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
  SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly']
  
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

def get_drive_folder(name=None, root_id=os.environ.get("ROOT_FOLDER")):
  """
  Searches for all Google Drive folders matching the given name.

  Args:
      name (str): The name of the folder to search for.
      root_id (str, optional): The ID of the parent folder to search within. 
          Defaults to the value of the "ROOT_FOLDER" environment variable.

  Returns:
      List[Dict[str, str]]: A list of folders matching the name, where each folder is represented
      as a dictionary with 'id' and 'name' keys.
  """
  try:
    service = get_service()
    
    results = (
      service.files().list(
        q=f"name='{name}' and " if name else ""
          f"mimeType='application/vnd.google-apps.folder' and "
          f"trashed = false and "
          f"'{root_id}' in parents",
        driveId=os.environ.get("DRIVE_ID"),
        corpora='drive',
        fields="files(id, name)",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
      ).execute()
    )
    
  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return results["files"]

def create_folder_path(path: str, root_id: str=os.environ.get("ROOT_FOLDER")):
  """
  Creates a folder path in Google Drive under the specified root folder.

  Args:
      path (str): The folder path to create (e.g., "Parent/Child/Subfolder").
      root_id (str): The ID of the root folder under which the path will be created.

  Returns:
      Dict[str, str]: A dictionary containing the 'id' and 'name' of the final folder in the path.
  """
  path = path.split("/")
  
  current_parent_id = root_id
  folder = None
  for current_folder in path:
    folder = create_folder(current_folder, current_parent_id)
    current_parent_id = folder.get("id")
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
  folders = get_drive_folder()
  print(folders)
    