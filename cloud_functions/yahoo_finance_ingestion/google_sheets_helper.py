import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe


class GoogleSheetsHelper():
    def __init__(self, path_to_service_account_key: str = None):
        """an authenticated connection to google sheets via a service account

        Args:
            path_to_service_account_key (str, optional): Path to the key to the service account. Has default value based on windows / mac. 
            https://docs.gspread.org/en/latest/oauth2.html
        """
        self.gc = gspread.service_account(path_to_service_account_key)

    def _open_sheet(self, sheet_key: str):
        return self.gc.open_by_key(sheet_key)

    def read_google_sheet_as_df(self, sheet_key: str) -> pd.DataFrame:
        """read contents of sheet to a pandas dataframe

        Args:
            sheet_key (str): key for the google sheet

        Returns:
            pd.DataFrame: the conents of the google sheet as a dataframe
        """
        return get_as_dataframe(self._open_sheet(sheet_key))

    def write_df_to_google_sheet(self, sheet_key: str, df: pd.DataFrame) -> None:
        """write dataframe to an existing sheet. overwrites existing content

        Args:
            sheet_key (str): key for the google sheet
            df (pd.DataFrame): dataframe to load
        """
        ws = self._open_sheet(sheet_key)
        set_with_dataframe(ws, df)

    def append_df_to_google_sheet(self, sheet_key: str, df: pd.DataFrame) -> None:
        """Append a dataframe to an existing sheet

        Args:
            sheet_key (str): key for the google sheet
            df (pd.DataFrame): data frame to append
        """
        ws = self._open_sheet(sheet_key)
        existing_records = self.get_as_dataframe(ws)
        updated = existing_records.append(df)
        set_with_dataframe(ws, updated)