import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import logging

class GoogleSheetsHelper:
    def __init__(self, credentials: dict):
        """an authenticated connection to google sheets via a service account

        Args: credentials (dict): credentials for service account
        based on windows / mac.
        """
        self.gc = gspread.service_account_from_dict(credentials)

    def _open_sheet(self, sheet_key: str, sheet_name: str):
        return self.gc.open_by_key(sheet_key).worksheet(sheet_name)

    def read_google_sheet_as_df(self, sheet_key: str, sheet_name: str) -> pd.DataFrame:
        """read contents of sheet to a pandas dataframe

        Args:
            sheet_name (str): name of the sheet within the spreadsheet to be accessed
            sheet_key (str): key for the google sheet

        Returns:
            pd.DataFrame: the conents of the google sheet as a dataframe
        """
        return get_as_dataframe(self._open_sheet(sheet_key, sheet_name))

    def write_df_to_google_sheet(self, sheet_key: str, sheet_name: str, df: pd.DataFrame) -> None:
        """write dataframe to an existing sheet. overwrites existing content

        Args:
            sheet_name:
            sheet_key (str): key for the google sheet
            df (pd.DataFrame): dataframe to load
        """
        ws = self._open_sheet(sheet_key, sheet_name)
        set_with_dataframe(ws, df)

    def append_df_to_google_sheet(self, sheet_key: str, sheet_name: str, df: pd.DataFrame) -> None:
        """Append a dataframe to an existing sheet

        Args:
            sheet_name (str): name of the sheet within the spreadsheet to be accessed
            sheet_key (str): key for the google sheet
            df (pd.DataFrame): data frame to append
        """
        ws = self._open_sheet(sheet_key, sheet_name)
        # check if there is any data in the sheet already
        check_cell = ws.acell('A1').value
        if check_cell is not None:
            logging.info("appending dataframe")
            existing_records = get_as_dataframe(ws)
            # the get_as_dataframe function pulls in all cells regardless of if they have data,
            # so these need to be dropped
            legitimate_cols = [c for c in df.columns if c.lower()[:7] != 'unnamed']
            existing_records = existing_records[legitimate_cols].dropna().drop_duplicates()
            combined = existing_records.append(df)
            set_with_dataframe(ws, combined)
        else:
            logging.info("no data in sheet. loading fresh df")
            set_with_dataframe(ws, df)
