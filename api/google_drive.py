
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from api.callture import download_recording
import pandas as pd

load_dotenv()


def get_service():
  
  SERVICE_ACCOUNT_FILE = "service_account.json"
  SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.readonly']
  
  credentials = service_account.Credentials.from_service_account_file(
      SERVICE_ACCOUNT_FILE, scopes=SCOPES
  )
  service = build('drive', 'v3', credentials=credentials)
  return service

def upload_to_drive(object_bytes, name, mimetype, description, root_id=os.environ.get("ROOT_FOLDER_ID")):
  
  object_stream = BytesIO(object_bytes)
  
  try:
    service = get_service()

    file_metadata = {
        "name": name,
        "parents": [root_id],
        "description": description
    }
    media_stream = MediaIoBaseUpload(object_stream, mimetype=mimetype, resumable=True)
    # pylint: disable=maybe-no-member
    file = (
        service.files()
        .create(
          body=file_metadata, 
          media_body=media_stream, 
          fields="id",
          supportsAllDrives=True
        ).execute()
    )

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.get("id")

def get_drive_folder(name=None, root_id=os.environ.get("ROOT_FOLDER_ID")):
  """
  Searches for all Google Drive folders matching the given name.

  Args:
      name (str): The name of the folder to search for.
      root_id (str, optional): The ID of the parent folder to search within. 
          Defaults to the value of the "ROOT_FOLDER_ID" environment variable.

  Returns:
      List[Dict[str, str]]: A list of folders matching the name, where each folder is represented
      as a dictionary with 'id' and 'name' keys.
  """
  try:
    service = get_service()
    
    query = f"name='{name}' and " if name else ""
    query += (
      f"mimeType='application/vnd.google-apps.folder' and "
      f"trashed = false and "
      f"'{root_id}' in parents"
    )
    
    
    results = (
      service.files().list(
        q=query,
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

def create_folder_path(path: str, root_id: str=os.environ.get("ROOT_FOLDER_ID")):
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

def create_folder(name, parent_id=os.environ.get("ROOT_FOLDER_ID")):
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

def upload_df_to_drive(df: pd.DataFrame):
    pd.set_option('display.max_columns', None)
  
    current_folder = {}
    
    for recording in df.itertuples():
        current_year = recording.Year
        current_month = recording.Month
        current_day = recording.Day
        if "Year" not in current_folder or current_folder["Year"][0] != current_year:
            folder = get_drive_folder(current_year)
            if not folder:
                folder = [create_folder(current_year)]
            folder = folder[0]
            current_folder["Year"] = (current_year, folder["id"])
            
        if "Month" not in current_folder or current_folder["Month"][0] != current_month:
            folder = get_drive_folder(current_month, current_folder["Year"][1])
            if not folder:
                folder = [create_folder(current_month, current_folder["Year"][1])]
            folder = folder[0]
            current_folder["Month"] = (current_month, folder["id"])

        if "Day" not in current_folder or current_folder["Day"][0] != current_day:
            folder = get_drive_folder(current_day, current_folder["Month"][1])
            if not folder:
                folder = [create_folder(current_day, current_folder["Month"][1])]
            folder = folder[0]
            current_folder["Day"] = (current_day, folder["id"])
            
        
        day_folder_id = current_folder["Day"][1]
        
        recording_id = recording.CDRID
        
        # For some reason, when downloading from the new interface, it does not include the extension number
        # name = "_".join(recording.Time.split()[::-1]) + "_" + str(recording.Line_No) + "_" + str(recording.Ext_No) + "_" + str(recording_id)
        name = "_".join(recording.Time.split()[::-1]) + "_" + str(recording.Line_No) + "_" + str(recording_id)
        description = "\n".join([f"{field}: {getattr(recording, field)}" for field in recording._fields[1:] if field not in ["Year", "Month", "Day"]])


        req = download_recording(recording_id)
        upload_to_drive(req.content, name, "audio/mpeg", description, day_folder_id)

if __name__ == "__main__":
  folders = get_drive_folder()
    