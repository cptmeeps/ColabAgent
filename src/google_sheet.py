# @title Google Sheet

# google_sheet.py: Module to interact with the Google Sheets API for reading and updating sheets.

import pandas as pd
import re
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, List
from googleapiclient.discovery import build
from google.colab import auth

class GoogleSheet:
    """
    The GoogleSheet class provides methods to interact with Google Sheets.
    It allows reading sheet data into a pandas DataFrame, updating sheet values, and retrieving metadata.
    """
    
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

    def get_values(self, range_name: str) -> List[List[Any]]:
        """Get values from the specified range."""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])

if __name__ == "__main__":
    # Test GoogleSheet functionality
    sheet_url = "https://docs.google.com/spreadsheets/d/1Tarn_9Hou5HVY8nxY7ox84mIvjUFUl9sQKNY4GpU_7g/edit?gid=61014510#gid=61014510"
    sheet = GoogleSheet(sheet_url)
    df = sheet.read_to_dataframe()
    print("First few rows of the Google Sheet:")
    print(df.head())