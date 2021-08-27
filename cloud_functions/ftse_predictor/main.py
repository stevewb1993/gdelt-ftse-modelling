import pandas as pd
import json
from googleapiclient import discovery
from typing import Dict, List
from google_sheets_helper import GoogleSheetsHelper
from dotenv import load_dotenv
import os
import logging
from google.cloud import bigquery

load_dotenv()

PROJECT_ID = "gdelt-ftse"
MODEL_NAME = "gdelt_ftse_regression_model"
GDELT_SPREADSHEET_NAME = "predictions"
FTSE_PREDICTIONS_SHEET_ID = "1_j1C4hY7hKtuaYzaZSepyM4s_9yY4nY8Y7zEi3-b29o"


def run_ai_platform_prediction(project: str, model: str, instances, version=None):
    """Send json data to a deployed model for prediction.
    Args:
        project (str): project where the AI Platform Model is deployed.
        model (str): model name.
        instances ([Dict[str: object]]): Keys should be the names of Tensors
            your deployed model expects as inputs. Values should be datatypes
            convertible to Tensors, or (potentially nested) lists of datatypes
            convertible to tensors.
        version: str, version of the model to target.
    Returns:
        Dict[str: any]: dictionary of prediction results defined by the
            model.
    """
    # Create the AI Platform service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    service = discovery.build('ml', 'v1')
    name = f'projects/{project}/models/{model}'

    if version is not None:
        name += f'/versions/{version}'

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    if 'error' in response:
        logging.error(f"Error in response from AI Platform: {response['error']}")
        raise RuntimeError(response['error'])

    logging.info("Successfully polled model")
    return response['predictions'][0]


def get_gdelt_data(bq_client: bigquery.Client, event_date: str) -> pd.DataFrame:
    base_query: str = f"""
                            SELECT
                                PARSE_DATE("%Y%m%d",CAST(SQLDATE as string)) as EventDate
                                , avg(AvgTone) as AvgTone
                                , STDDEV(AvgTone) as StdDevTone
                                , avg(GoldsteinScale) as AvgGoldstein
                                , STDDEV(GoldsteinScale) as StdDevGoldstein
                            FROM 
                                `gdelt-bq.gdeltv2.events` 
                            where 
                                PARSE_DATE("%Y%m%d",CAST(SQLDATE as string)) = DATE "{event_date}"
                            AND
                                (Actor1CountryCode = 'GBR'
                                or 
                                Actor2CountryCode = 'GBR')
                            GROUP BY
                                1
                        """

    return (
        bq_client.query(base_query)
            .result()
            .to_dataframe(create_bqstorage_client=True)
    )


def parse_gdelt_to_model_format(df: pd.DataFrame):
    return df[["AvgTone", "StdDevTone", "AvgGoldstein", "StdDevGoldstein"]].values.tolist()


def parse_ftse_predictions_as_df(model_prediction: float, request_date) -> pd.DataFrame:
    data = [[request_date, model_prediction]]
    return pd.DataFrame(data, columns=['request_date', 'model_prediction'])


def main(request_date: str):
    # get gdelt data needed for prediction
    bq_client = bigquery.Client()
    parsed_gdelt_data = (
        parse_gdelt_to_model_format(
            get_gdelt_data(bq_client, event_date=request_date)
        )
    )
    logging.info("Successfully parsed GDELT data")

    logging.info("starting to get predictions")
    # run predictions and parse outputs to dataframe
    model_predictions = run_ai_platform_prediction(PROJECT_ID, MODEL_NAME, parsed_gdelt_data)
    logging.info("successfully got model predictions")
    logging.info("starting to parse predictions")
    parsed_predictions = parse_ftse_predictions_as_df(model_predictions, request_date)
    logging.info("successfully parsed predictions")

    # use google sheets client to save down data
    logging.info("attempting to get service account creds")
    service_account_credentials: dict = eval(os.environ.get("service_account_credentials"))
    logging.info(f"credentials are: {service_account_credentials}")
    google_sheets_helper = GoogleSheetsHelper(service_account_credentials)
    google_sheets_helper.append_df_to_google_sheet(FTSE_PREDICTIONS_SHEET_ID, GDELT_SPREADSHEET_NAME,
                                                   parsed_predictions)


def handle_api_request(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    request_json = request.get_json()
    request_args = request.args

    if request_json and 'request_date' in request_json:
        request_date = request_json['request_date']
    elif request_args and 'request_date' in request_args:
        request_date = request_args['request_date']
    else:
        return 'request is missing the request_date parameter'

    logging.info(f"request date is: {request_date}")

    main(request_date=request_date)

    return "success!"


if __name__ == "__main__":
    main(request_date="2020-10-01")
