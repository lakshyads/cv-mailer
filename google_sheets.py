"""
Google Sheets integration for reading and updating job application data.
"""
import logging
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import os
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Client for interacting with Google Sheets."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, spreadsheet_id: str, worksheet_name: str = None):
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_name = worksheet_name or Config.WORKSHEET_NAME
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API."""
        creds = None
        token_file = "token.pickle"
        
        # Try to load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Try service account first, then OAuth
                if os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                    try:
                        # Check if it's a service account JSON
                        creds = service_account.Credentials.from_service_account_file(
                            Config.GOOGLE_CREDENTIALS_FILE,
                            scopes=self.SCOPES
                        )
                    except Exception:
                        # If not service account, use OAuth flow
                        from google_auth_oauthlib.flow import InstalledAppFlow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            Config.GOOGLE_CREDENTIALS_FILE,
                            self.SCOPES
                        )
                        creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully authenticated with Google Sheets API")
    
    def list_all_sheets(self) -> List[Dict]:
        """
        List all worksheets in the spreadsheet.
        
        Returns:
            List of dictionaries with 'title' and 'sheetId' keys
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = []
            for sheet in spreadsheet.get('sheets', []):
                properties = sheet.get('properties', {})
                sheets.append({
                    'title': properties.get('title'),
                    'sheetId': properties.get('sheetId')
                })
            
            logger.info(f"Found {len(sheets)} sheets in spreadsheet")
            return sheets
            
        except HttpError as error:
            logger.error(f"Error listing sheets: {error}")
            raise
    
    def read_all_rows(self, worksheet_name: str = None) -> List[Dict]:
        """
        Read all rows from the worksheet.
        Assumes first row contains headers.
        Returns list of dictionaries with column names as keys.
        
        Args:
            worksheet_name: Name of the worksheet to read. If None, uses self.worksheet_name
        """
        sheet_name = worksheet_name or self.worksheet_name
        try:
            range_name = f"{sheet_name}!A:Z"  # Adjust range as needed
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning(f"No data found in worksheet: {sheet_name}")
                return []
            
            # First row is headers
            headers = values[0]
            
            # Convert rows to dictionaries
            rows = []
            for i, row in enumerate(values[1:], start=2):  # Start at row 2 (1-indexed)
                row_dict = {header: row[j] if j < len(row) else "" 
                           for j, header in enumerate(headers)}
                row_dict['_row_number'] = i  # Store row number for reference
                row_dict['_sheet_name'] = sheet_name  # Store sheet name for reference
                rows.append(row_dict)
            
            logger.info(f"Read {len(rows)} rows from worksheet: {sheet_name}")
            return rows
            
        except HttpError as error:
            logger.error(f"Error reading from Google Sheets: {error}")
            raise
    
    def read_all_sheets(self, sheet_filter: Optional[str] = None) -> List[Dict]:
        """
        Read all rows from all worksheets in the spreadsheet.
        
        Args:
            sheet_filter: Optional regex pattern to filter sheet names. 
                         If None, reads all sheets.
        
        Returns:
            List of dictionaries with column names as keys, including '_sheet_name'
        """
        all_rows = []
        sheets = self.list_all_sheets()
        
        import re
        pattern = re.compile(sheet_filter) if sheet_filter else None
        
        for sheet in sheets:
            sheet_name = sheet['title']
            
            # Apply filter if provided
            if pattern and not pattern.search(sheet_name):
                logger.debug(f"Skipping sheet (doesn't match filter): {sheet_name}")
                continue
            
            try:
                rows = self.read_all_rows(sheet_name)
                all_rows.extend(rows)
                logger.info(f"Read {len(rows)} rows from sheet: {sheet_name}")
            except Exception as e:
                logger.warning(f"Error reading sheet {sheet_name}: {e}")
                continue
        
        logger.info(f"Total rows read from all sheets: {len(all_rows)}")
        return all_rows
    
    def update_cell(self, row: int, column: str, value: str, worksheet_name: str = None):
        """
        Update a specific cell in the worksheet.
        
        Args:
            row: Row number (1-indexed)
            column: Column letter (e.g., 'A', 'B', 'C')
            value: Value to set
            worksheet_name: Name of worksheet. If None, uses self.worksheet_name
        """
        sheet_name = worksheet_name or self.worksheet_name
        try:
            range_name = f"{sheet_name}!{column}{row}"
            body = {
                'values': [[value]]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated cell {column}{row} in {sheet_name} with value: {value}")
            
        except HttpError as error:
            logger.error(f"Error updating Google Sheets: {error}")
            raise
    
    def update_row(self, row: int, updates: Dict[str, str], worksheet_name: str = None):
        """
        Update multiple cells in a row.
        
        Args:
            row: Row number (1-indexed)
            updates: Dictionary mapping column names to values
            worksheet_name: Name of worksheet. If None, uses self.worksheet_name
        """
        sheet_name = worksheet_name or self.worksheet_name
        try:
            # First, get headers to map column names to letters
            range_name = f"{sheet_name}!1:1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            headers = result.get('values', [])[0] if result.get('values') else []
            column_map = {header.strip().lower(): (chr(65 + i), header) for i, header in enumerate(headers)}
            
            # Update each cell
            for column_name, value in updates.items():
                # Try exact match first, then case-insensitive
                col_key = column_name.strip().lower()
                if col_key in column_map:
                    col_letter, _ = column_map[col_key]
                    self.update_cell(row, col_letter, str(value), worksheet_name=sheet_name)
            
        except HttpError as error:
            logger.error(f"Error updating row in Google Sheets: {error}")
            raise
    
    def get_column_letter(self, column_name: str, worksheet_name: str = None) -> Optional[str]:
        """
        Get the column letter for a given column name.
        
        Args:
            column_name: Name of the column
            worksheet_name: Name of worksheet. If None, uses self.worksheet_name
        
        Returns:
            Column letter (e.g., 'A', 'B') or None if not found
        """
        sheet_name = worksheet_name or self.worksheet_name
        try:
            range_name = f"{sheet_name}!1:1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            headers = result.get('values', [])[0] if result.get('values') else []
            col_key = column_name.strip().lower()
            
            for i, header in enumerate(headers):
                if header.strip().lower() == col_key:
                    return chr(65 + i)  # A=0, B=1, etc.
            
            return None
            
        except HttpError as error:
            logger.error(f"Error getting column letter: {error}")
            return None

