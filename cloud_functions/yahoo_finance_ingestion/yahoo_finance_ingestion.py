import argparse
from common_functions.google_sheets_helper import GoogleSheetsHelper
import json
import yahoo_fin
import pandas as pd
import os
from common_functions import postgres_helper
from dotenv import load_dotenv

load_dotenv()


def handle_api_request(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    print(f"request is {request}")
    request_json = request.get_json()

    tickr = request_json['tickr']
    start_date = request_json['start_date']
    end_date = request_json['end_date']

    main(
        tickr = tickr,
        start_date = start_date,
        end_date = end_date,
    )

    return "success!"

def main(tickr: str, start_date: str, end_date: str) -> None:
    
    yahoo_finance_data: pd.DataFrame = get_historical_prices(
    tickr = tickr, 
    start_date = start_date, 
    end_date = end_date, 
    index_as_date = False, 
    interval = "1d")

    yahoo_finance_sheet_id = os.environ.get('yahoo_finance_sheet_id')

    google_sheets_helper = GoogleSheetsHelper(path_to_service_account_key = None)

    google_sheets_helper.write_df_to_google_sheet(yahoo_finance_sheet_id, yahoo_finance_data)
    

def get_historical_prices(tickr: str, start_date: str, end_date: str, index_as_date: bool, interval: str) -> pd.DataFrame:
    
    # Get historical FTSE data that can be used for training and testing
    return yahoo_fin.get_data(tickr, start_date= start_date, end_date = end_date, index_as_date = index_as_date, interval=interval)