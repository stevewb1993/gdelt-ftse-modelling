import pandas as pd
from googleapiclient import discovery
from utils.google_sheets_helper import GoogleSheetsHelper
import logging
from google.cloud import bigquery
from config import PROJECT_ID, GOOGLE_SHEET_ID, SERVICE_ACCOUNT_CREDENTIALS

MODEL_NAME = "gdelt_ftse_regression_model"
PREDICTIONS_SPREADSHEET_NAME = "predictions"


def run_ai_platform_prediction(project: str, model: str, instances, version=None) -> float:
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
    """
    returns summarised GDELT event data for a given date

    Args:
        bq_client: bigquery client
        event_date: date to retrive summarised information for

    Returns:
        pd.Dataframe: summarised GDELT events
    """
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


def parse_gdelt_to_model_format(df: pd.DataFrame) -> list:
    """
    parses gdelt dataframe into suitable format for regression model
    Args:
        df: summarised GDELT data

    Returns:
        list: summarised gdelt data in format for regression model
    """
    return df[["AvgTone", "StdDevTone", "AvgGoldstein", "StdDevGoldstein"]].values.tolist()


def parse_ftse_predictions_as_df(model_prediction: float, request_date: str) -> pd.DataFrame:
    """
    parses the AI platform prediction into dataframe format
    Args:
        model_prediction: prediction from the model
        request_date: date of the prediction

    Returns:
        pd.DataFrame: dataframe of ftse prediction
    """
    data = [[request_date, model_prediction]]
    return pd.DataFrame(data, columns=['request_date', 'model_prediction'])


def get_model_prediction(request_date: str):
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
    google_sheets_helper = GoogleSheetsHelper(SERVICE_ACCOUNT_CREDENTIALS)
    google_sheets_helper.append_df_to_google_sheet(GOOGLE_SHEET_ID, PREDICTIONS_SPREADSHEET_NAME,
                                                   parsed_predictions)


if __name__ == "__main__":
    get_model_prediction(request_date="2020-10-01")
