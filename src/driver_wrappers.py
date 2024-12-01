%%capture
# @title Google Drive API Wrapper Class

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

# @title Google Sheets API Wrapper Class

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.colab import auth
import re
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any

class GoogleSheet:
    def __init__(self, url: str):
        self.url = url
        self.spreadsheet_id, self.gid = self._extract_spreadsheet_info(url)
        self.service = self._init_service()
        self.sheet_name = self._get_sheet_name()

    def _init_service(self):
        auth.authenticate_user()
        return build('sheets', 'v4', credentials=None)

    @staticmethod
    def _extract_spreadsheet_info(url: str):
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            raise ValueError("Could not find spreadsheet ID in URL")
        spreadsheet_id = match.group(1)

        parsed = urlparse(url)
        query_params = parse_qs(parsed.fragment or parsed.query)
        gid = query_params.get('gid', ['0'])[0]

        return spreadsheet_id, gid

    def _get_sheet_name(self) -> str:
        sheet_metadata = self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id
        ).execute()

        for sheet in sheet_metadata.get('sheets', ''):
            if sheet['properties']['sheetId'] == int(self.gid):
                return sheet['properties']['title']
        return 'Sheet1'

    def read_to_dataframe(self) -> pd.DataFrame:
        """Read sheet contents into a pandas DataFrame."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_name
        ).execute()

        values = result.get('values', [])
        if not values:
            raise ValueError('No data found in spreadsheet')

        headers = values[0]
        data = values[1:]
        return pd.DataFrame(data, columns=headers)

    def get_metadata(self) -> Dict[str, Any]:
        """Get sheet metadata."""
        return self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id
        ).execute()

    def update_values(self, range_name: str, values: list):
        """Update values in specified range."""
        body = {'values': values}
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

if __name__ == "__main__":
    # Test GoogleSheet functionality
    sheet_url = "https://docs.google.com/spreadsheets/d/1Tarn_9Hou5HVY8nxY7ox84mIvjUFUl9sQKNY4GpU_7g/edit?gid=61014510#gid=61014510"
    sheet = GoogleSheet(sheet_url)
    df = sheet.read_to_dataframe()
    print("First few rows of the Google Sheet:")
    print(df.head())


# @title Google Docs API Wrapper Class

class GoogleDoc:
    def __init__(self, url: str):
        self.url = url
        self.document_id = self._extract_document_id(url)
        self.service = self._init_service()

    def _init_service(self):
        auth.authenticate_user()
        return build('docs', 'v1', credentials=None)

    @staticmethod
    def _extract_document_id(url: str) -> str:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            raise ValueError("Could not find document ID in URL")
        return match.group(1)

    def get_document(self) -> Dict[str, Any]:
        """Retrieve the document's metadata and content."""
        return self.service.documents().get(documentId=self.document_id).execute()

    def read_content(self) -> str:
        """Read the plain text content of the document."""
        document = self.get_document()
        return self._extract_text(document)

    def _extract_text(self, document: Dict[str, Any]) -> str:
        """Extract text from the document's body."""
        text = ''
        for element in document.get('body', {}).get('content', []):
            paragraph = element.get('paragraph')
            if paragraph:
                for elem in paragraph.get('elements', []):
                    if text_run := elem.get('textRun'):
                        text += text_run.get('content', '')
        return text

    def update_content(self, new_text: str):
        """Replace the document's content with new_text."""
        end_index = self._get_end_index()
        # Adjust end_index to exclude the final newline character
        if end_index > 1:
            end_index -= 1

        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': end_index
                    }
                }
            },
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': new_text
                }
            }
        ]
        return self.service.documents().batchUpdate(
            documentId=self.document_id,
            body={'requests': requests}
        ).execute()

    def _get_end_index(self) -> int:
        """Get the end index for deleting content."""
        document = self.get_document()
        return document.get('body').get('content')[-1].get('endIndex', 1)

    def append_content(self, additional_text: str):
        """Append text to the end of the document."""
        requests = [{
            'insertText': {
                'location': {'index': self._get_end_index() - 1},
                'text': additional_text
            }
        }]
        return self.service.documents().batchUpdate(
            documentId=self.document_id,
            body={'requests': requests}
        ).execute()

if __name__ == "__main__":
    # Test GoogleDoc functionality
    doc_url = "https://docs.google.com/document/d/1iuY9x6oBj9LvOaTbGRFkXzxdztPZALGV3Yv0vDkNLgk/edit?tab=t.0"
    doc = GoogleDoc(doc_url)
    content = doc.read_content()
    print("\nContent of the Google Doc:")
    print(content)

    doc.update_content("This is the new content of the document.")
    print("\nGoogle Doc content has been updated.")

    doc.append_content("\nThis text was appended to the document.")
    print("\nAdditional content has been appended to the Google Doc.")