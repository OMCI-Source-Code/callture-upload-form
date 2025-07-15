"""
google_drive.py

This module provides utilities for anything Google Drive related

Functions:
    create_service
    upload_to_drive
    get_drive_folder
    create_folder_path
    create_folder
    setup_date_folders
    upload_df_to_drive
    transfer_file
    a_upload_df_to_drive
    a_upload_to_drive

Author: Terry Luan
Date: 2025-07-14
"""
import asyncio
import os
import warnings
from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from api.callture import download_recording, a_download_recording
# from api.callture import a_download_recording
from api.pandas_utility import PersonRow

load_dotenv()

callture_semaphore = asyncio.Semaphore(100)
google_semaphore = asyncio.Semaphore(100)


def get_service():

    service_account_file = "service_account.json"
    scopes = [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes
    )
    service = build("drive", "v3", credentials=credentials)
    return service


def upload_to_drive(
    recording, object_bytes: bytes, root_id=os.environ.get("ROOT_FOLDER_ID")
):
    # print(f"Uploading {record_id}")
    recording_id = recording.CDRID
    
    # For some reason, when downloading from the new interface, it does not include the extension number
    # name = "_".join(recording.Time.split()[::-1]) + "_" + str(recording.Line_No) + "_" + str(recording.Ext_No) + "_" + str(recording_id)
    name = (
        "_".join(recording.Time.split()[::-1])
        + "_"
        + str(recording.Line_No)
        + "_"
        + str(recording_id)
    )
    description = "\n".join(
        [
            f"{field}: {getattr(recording, field)}"
            for field in recording._fields[1:]
            if field not in ["Year", "Month", "Day"]
        ]
    )
    mime_type="audio/mpeg"

    object_stream = BytesIO(object_bytes)

    try:
        service = get_service()

        file_metadata = {"name": name, "parents": [root_id], "description": description}
        media_stream = MediaIoBaseUpload(
            object_stream, mimetype=mime_type, resumable=True
        )
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media_stream,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
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
        List[dict[str, str]]: A list of folders matching the name, where each folder is represented
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
            service.files()  # pylint: disable=maybe-no-member
            .list(
                q=query,
                driveId=os.environ.get("DRIVE_ID"),
                corpora="drive",
                fields="files(id, name)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )

    except HttpError as error:
        print(f"An error occurred: {error}")

    return results["files"]


def create_folder_path(path: str, root_id=os.environ.get("ROOT_FOLDER_ID")):
    """
    Creates a folder path in Google Drive under the specified root folder.

    Args:
        path (str): The folder path to create (e.g., "Parent/Child/Subfolder").
        root_id (str, optional): The ID of the root folder under which the path will be created.
                                 Defaults to os.environ.get("ROOT_FOLDER_ID").

    Returns:
        dict[str, str]: A dictionary containing the 'id' and 'name' of the final folder in the path.
    """
    path_dir = path.split("/")

    current_parent_id = root_id
    folder = None
    for current_folder in path_dir:
        folder = create_folder(current_folder, current_parent_id)
        current_parent_id = folder.get("id")
    return folder


def create_folder(name, parent_id=os.environ.get("ROOT_FOLDER_ID")):
    """
    Creates a specific folder in Google Drive under the specified root folder.

    Args:
        name (str): The folder to create
        parent_id (str, optional): The id of the parent folder under which to create the folder.
                                   Defaults to os.environ.get("ROOT_FOLDER_ID").

    Returns:
        dict[str, str]: A dictionary containing the 'id' and 'name' of the folder created.
    """

    service = get_service()
    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }

    try:
        file = (
            service.files()  # pylint: disable=no-member
            .create(body=folder_metadata, fields="id, name", supportsAllDrives=True)
            .execute()
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
    return file


def setup_date_folders(
    date_range: str, root_folder_id=os.environ.get("ROOT_FOLDER_ID")
):
    """
    Checks if date folders are correctly set up for the given range, and creates them if not.

    The structure will be:
    - Root folder
      - Year folders (e.g., 2024)
        - Month folders (e.g., 01, 02, ...)
          - Day folders (e.g., 01, 02, ...)

    Args:
        date_range (str): A string describing the date range to check/create folders for.
                   Format: '%d %b %Y %I:%M %p - %d %b %Y %I:%M %p'
        root_folder_id (str, optional): ID of the parent folder under which to organize the structure.
                                      Defaults to os.environ.get("ROOT_FOLDER_ID").

    Returns:
        dict[str, dict[str, dict[str, str]]]: Nested dicts mapping [month][day][year] to folder ID.
        Example: result["01"]["12"]["2020"] returns the folder ID for Jan 12, 2020.
    """

    start_date, end_date = date_range.split(" - ")

    # A list of dictionaries which relate folders to ids
    # The dictionaries correspond to the year, month and day
    year_id_map = {}
    month_id_map: dict[str, dict[str, str]] = defaultdict(dict)
    day_id_map: dict[str, dict[str, dict[str, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )

    date_format = '%d %b %Y %I:%M %p'

    dt_start_date = datetime.strptime(start_date, date_format)
    dt_end_date = datetime.strptime(end_date, date_format)

    current_date = dt_start_date

    current_year, current_month = "", ""

    while current_date <= dt_end_date:
        if current_date.strftime("%Y") != current_year:
            current_year = current_date.strftime("%Y")
            folder = get_drive_folder(current_year, root_folder_id)
            if not folder:
                folder = create_folder(current_year, root_folder_id)
            elif len(folder) != 1:
                warnings.warn(
                    f"WARNING - Year: There are multiple folders under the parent folder {root_folder_id} with name {current_year}."
                )
            else:
                folder = folder[0]
            year_id_map[current_year] = folder["id"]

        year_folder_id = year_id_map[current_year]

        if current_date.strftime("%m") != current_month:
            current_month = current_date.strftime("%m")
            folder = get_drive_folder(current_month, year_folder_id)
            if not folder:
                folder = create_folder(current_month, year_folder_id)
            elif len(folder) != 1:
                warnings.warn(
                    f"WARNING - Month: There are multiple folders under the parent folder {year_folder_id} with name {current_month}."
                )
            else:
                folder = folder[0]
            month_id_map[current_year][current_month] = folder["id"]

        month_folder_id = month_id_map[current_year][current_month]

        current_day = current_date.strftime("%d")
        folder = get_drive_folder(current_day, month_folder_id)
        if not folder:
            folder = create_folder(current_day, month_folder_id)
        elif len(folder) != 1:
            warnings.warn(
                f"WARNING - Day: There are multiple folders under the parent folder {month_folder_id} with name {current_day}."
            )
        else:
            folder = folder[0]
        day_id_map[current_year][current_month][current_day] = folder["id"]
        current_date += timedelta(days=1)

    return day_id_map


def upload_df_to_drive(df: pd.DataFrame, day_id_map: dict[str, dict[str, dict[str, str]]]):
    print("Starting to Upload Sync")

    for recording in df.itertuples():
        day_folder_id = day_id_map[recording.Year][recording.Month][recording.Day]
        req = download_recording(recording)
        upload_to_drive(recording, req.content, day_folder_id)


async def transfer_file(recording: PersonRow, day_folder_id: str, use_semaphore: bool):
    if use_semaphore:
        async with callture_semaphore:
            req = await a_download_recording(recording)
        async with google_semaphore:
            await a_upload_to_drive(
                recording, req.content, day_folder_id
            )
    else:
        req = await a_download_recording(recording)
        await a_upload_to_drive(
            recording, req.content, day_folder_id
        )

async def a_upload_df_to_drive(
    df: pd.DataFrame, day_id_map: dict[str, dict[str, dict[str, str]]], use_semaphore: bool, batched: bool, batch_size: int
):
    print("Starting to Upload Async")
    # async with asyncio.TaskGroup() as tg:
    #     tasks = []
    #     for recording in df.itertuples():
    #         tasks.append(tg.create_task(
    #             transfer_file(
    #                 recording, day_id_map[recording.Year][recording.Month][recording.Day]
    #             )
    #         ))
    await asyncio.gather(
        *(
            transfer_file(
                recording, day_id_map[recording.Year][recording.Month][recording.Day], use_semaphore
            )
            for recording in df.itertuples()
        )
    )


async def a_upload_to_drive(
    recording: PersonRow, object_bytes: bytes, root_id=os.environ.get("ROOT_FOLDER_ID")
):
    # print(f"Uploading {record_id}")
    recording_id = recording.CDRID
    
    # For some reason, when downloading from the new interface, it does not include the extension number
    # name = "_".join(recording.Time.split()[::-1]) + "_" + str(recording.Line_No) + "_" + str(recording.Ext_No) + "_" + str(recording_id)
    name = (
        "_".join(recording.Time.split()[::-1])
        + "_"
        + str(recording.Line_No)
        + "_"
        + str(recording_id)
    )
    description = "\n".join(
        [
            f"{field}: {getattr(recording, field)}"
            for field in recording._fields[1:]
            if field not in ["Year", "Month", "Day"]
        ]
    )
    mime_type="audio/mpeg"

    object_stream = BytesIO(object_bytes)

    try:
        service = get_service()

        file_metadata = {"name": name, "parents": [root_id], "description": description}
        media_stream = MediaIoBaseUpload(
            object_stream, mimetype=mime_type, resumable=True
        )
        # pylint: disable=no-member
        file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media_stream,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")
