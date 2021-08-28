from datetime import datetime

import pandas as pd
from config import GOOGLE_SHEET_ID, SERVICE_ACCOUNT_CREDENTIALS
from utils.google_sheets_helper import GoogleSheetsHelper
from yahoo_fin.stock_info import get_data

FTSE_SPREADSHEET_NAME = "ftse"
FTSE_TICKR = "^ftse"


def ingest_yahoo_finance_data() -> None:
    yahoo_finance_data: pd.DataFrame = get_historical_prices(
        tickr=FTSE_TICKR,
        start_date="12/04/2009",
        end_date=datetime.today().strftime("%d-%m-%Y"),
        index_as_date=False,
        interval="1d",
    )

    # use google sheets client to save down data
    google_sheets_helper = GoogleSheetsHelper(SERVICE_ACCOUNT_CREDENTIALS)
    google_sheets_helper.write_df_to_google_sheet(
        GOOGLE_SHEET_ID, FTSE_SPREADSHEET_NAME, yahoo_finance_data
    )


def get_historical_prices(
    tickr: str, start_date: str, end_date: str, index_as_date: bool, interval: str
) -> pd.DataFrame:
    """

    Args:
        tickr: tickr of instrument to be valued
        start_date: start date of request
        end_date: end date of request
        index_as_date: whether the date should be the index of the df
        interval: daily, weekly etc

    Returns:
        pd.DataFrame: dataframe of prices
    """
    # Get historical FTSE data that can be used for training and testing
    return get_data(
        tickr,
        start_date=start_date,
        end_date=end_date,
        index_as_date=index_as_date,
        interval=interval,
    )


if __name__ == "__main__":
    ingest_yahoo_finance_data()
