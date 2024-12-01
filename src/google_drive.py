# @title Google Drive

# google_drive.py: Module to interact with Google Drive.

from typing import Dict, Any, Optional, List
from googleapiclient.discovery import build
from google.colab import auth
from googleapiclient.http import MediaFileUpload

class GoogleDrive:
    def __init__(self):
        self.service = self._init_service()

    def _init_service(self):
        """Initialize Google Drive service."""
        auth.authenticate_user()
        return build('drive', 'v3', credentials=None)

    def file_exists(self, file_name: str, parent_id: Optional[str] = None) -> bool:
        """
        Check if a file exists in Drive or specific folder.

        Args:
            file_name: Name of the file to check
            parent_id: Optional parent folder ID

        Returns:
            bool: True if file exists, False otherwise
        """
        query = f"name = '{file_name}' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        return len(results.get('files', [])) > 0

    def directory_exists(self, dir_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Check if directory exists and return its ID if found.

        Args:
            dir_name: Name of the directory to check
            parent_id: Optional parent folder ID

        Returns:
            Optional[str]: Directory ID if exists, None otherwise
        """
        query = f"name = '{dir_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        files = results.get('files', [])
        return files[0]['id'] if files else None

    def create_directory(self, dir_name: str, parent_id: Optional[str] = None) -> str:
        """
        Create a new directory in Drive.

        Args:
            dir_name: Name of the directory to create
            parent_id: Optional parent folder ID

        Returns:
            str: ID of created directory
        """
        file_metadata = {
            'name': dir_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent_id:
            file_metadata['parents'] = [parent_id]

        file = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()

        return file.get('id')

    def create_file(self, file_name: str, mime_type: str, file_path: str,
                   parent_id: Optional[str] = None) -> str:
        """
        Create a new file in Drive.

        Args:
            file_name: Name for the new file
            mime_type: MIME type of the file
            file_path: Path to the file to upload
            parent_id: Optional parent folder ID

        Returns:
            str: ID of created file
        """
        file_metadata = {'name': file_name}
        if parent_id:
            file_metadata['parents'] = [parent_id]

        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')

    def get_files_in_directory(self, dir_id: str) -> List[Dict[str, str]]:
        """
        List all files in a directory.

        Args:
            dir_id: ID of the directory to list

        Returns:
            List[Dict[str, str]]: List of files with their IDs and names
        """
        query = f"'{dir_id}' in parents and trashed = false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)'
        ).execute()

        return results.get('files', [])

if __name__ == "__main__":
    drive = GoogleDrive()

    # Check if ColabAgent folder exists
    colab_folder_id = drive.directory_exists("ColabAgent")

    if not colab_folder_id:
        colab_folder_id = drive.create_directory("ColabAgent")
        print(f"Created ColabAgent folder with ID: {colab_folder_id}")
    else:
        print(f"Found existing ColabAgent folder with ID: {colab_folder_id}")

    # List files in ColabAgent directory
    files = drive.get_files_in_directory(colab_folder_id)
    print("\nFiles in ColabAgent folder:")
    for file in files:
        print(f"- {file['name']} ({file['id']})")