"""
test_google_drive.py

This module tests all google drive functions

Test methods:
    test_get_service
    test_upload_to_drive_new_file
    test_upload_to_drive_existing_file
    test_get_drive_folder
    test_create_folder_path
    test_upload_df_to_drive_async

Usage:
    Run with pytest -v

Author: Mame Mor Mbacke
Date: 2025-07-21
"""

import unittest
from unittest.mock import AsyncMock
import pytest
import httpx
from unittest.mock import patch, MagicMock
from api import create_app
from api.callture import download_recording
from api.google_drive import (
    upload_to_drive,
    get_service,
    get_drive_folder,
    create_folder,
    upload_df_to_drive,
)
from api.pandas_utility import parse_req_to_df, process_df


class TestDrive(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()

    # Test initializing the Google Drive API ----------------------------------
    @patch("api.google_drive.build")
    @patch("api.google_drive.service_account.Credentials.from_service_account_file")
    def test_get_service(self, mock_from_service_account_file, mock_build):
        from api.google_drive import get_service, service_account_file, scopes

        # Mock service account credentials to test Drive API initialization
        mock_creds = MagicMock()
        mock_service = MagicMock()
        mock_from_service_account_file.return_value = mock_creds
        mock_build.return_value = mock_service

        result = get_service()

        mock_from_service_account_file.assert_called_once_with(
            service_account_file, scopes=scopes
        )
        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
        self.assertEqual(result, mock_service)

    # Testing file uploads for files that DON'T exist ----------------------------------
    @patch("api.google_drive.get_service")
    @patch("api.google_drive.MediaIoBaseUpload")
    def test_upload_to_drive_new_file(self, mock_media_upload, mock_get_service):
        from api.google_drive import upload_to_drive

        # Create a fake call recording object to test functions
        MockRecording = MagicMock()
        MockRecording.CDRID = "1234"
        MockRecording.Time = "12:34 2025-07-22"
        MockRecording.Line_No = 1
        MockRecording._fields = ["CDRID", "Time", "Line_No", "Other"]
        MockRecording.Other = "Something"

        # Mock initializing the Drive API
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_files = MagicMock()
        mock_service.files.return_value = mock_files

        # Simulate file not already existing in the drive, mocks list of files that match the name (empty) and creates the new file
        mock_list = MagicMock()
        mock_list.execute.return_value = {"files": []}
        mock_files.list.return_value = mock_list
        mock_create = MagicMock()
        mock_create.execute.return_value = {"id": "file123"}
        mock_files.create.return_value = mock_create

        mock_media_upload.return_value = MagicMock()

        result = upload_to_drive(MockRecording, b"audio-bytes", root_id="root123")

        self.assertEqual(result, mock_files)
        mock_files.list.assert_called_once()
        mock_files.create.assert_called_once()

    # Testing file uploads for files that DO exist ----------------------------------
    @patch("api.google_drive.get_service")
    def test_upload_to_drive_existing_file(self, mock_get_service):
        from api.google_drive import upload_to_drive

        MockRecording = MagicMock()
        MockRecording.CDRID = "1234"
        MockRecording.Time = "02:22 2025-07-22"
        MockRecording.Line_No = 1
        MockRecording._fields = ["CDRID", "Time", "Line_No", "Other"]
        MockRecording.Other = "Something"

        fake_service = MagicMock()
        mock_get_service.return_value = fake_service
        fake_service.files().list().execute.return_value = {
            "files": [{"id": "1234567890"}]
        }

        result = upload_to_drive(MockRecording, b"audio-bytes", root_id="root123")

        self.assertEqual(result, "1234567890")
        fake_service.files().create.assert_not_called()

    # Test accessing a google drive folder ----------------------------------
    @patch("api.google_drive.get_service")
    def test_get_drive_folder(self, mock_get_service):
        from api.google_drive import get_drive_folder

        fake_service = MagicMock()
        mock_get_service.return_value = fake_service

        fake_service.files().list().execute.return_value = {
            "files": [{"id": "123455", "name": "TestFolder"}]
        }

        results = get_drive_folder(name="TestFolder", root_id="root123")

        self.assertEqual(results, [{"id": "123455", "name": "TestFolder"}])
        mock_get_service.assert_called_once()

    # Test creating a new folder in the Google Drive ----------------------------------
    @patch("api.google_drive.get_service")
    def test_create_folder(self, mock_get_service):
        from api.google_drive import create_folder

        fake_service = MagicMock()
        mock_get_service.return_value = fake_service

        fake_service.files().create().execute.return_value = {
            "id": "123456",
            "name": "MyFolder",
        }

        result = create_folder("MyFolder", parent_id="root123")

        self.assertEqual(result["id"], "123456")
        self.assertEqual(result["name"], "MyFolder")

    # Test creating a path of folders in the Google Drive. I.e. 2025/07/... or 2025/09/... ----------------------------------
    @patch("api.google_drive.create_folder")
    def test_create_folder_path(self, mock_create_folder):
        from api.google_drive import create_folder_path

        mock_create_folder.side_effect = lambda name, parent_id: {
            "id": f"id-{name}",
            "name": name,
        }

        result = create_folder_path("Parent/Child", root_id="root123")

        self.assertEqual(result, {"id": "id-Child", "name": "Child"})
        self.assertEqual(mock_create_folder.call_count, 2)

    # Test uploading the Callture call recording data to google drive ----------------------------------
    @patch("api.google_drive._upload_df_async")
    @patch("api.google_drive.asyncio.run")
    def test_upload_df_to_drive_async(self, mock_async_run, mock_upload_async):
        from api.google_drive import upload_df_to_drive
        import pandas as pd

        df = pd.DataFrame({"col": [1, 2]})
        day_id_map = {}

        upload_df_to_drive(df, day_id_map)

        mock_async_run.assert_called_once()
