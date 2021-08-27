from ftse_predictor import get_model_prediction
import logging
from datetime import datetime
from yahoo_finance_ingestor import ingest_yahoo_finance_data


def handle_api_request(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    request_date = datetime.today().strftime('%Y-%m-%d')
    logging.info(f"request date is: {request_date}")

    get_model_prediction(request_date=request_date)

    ingest_yahoo_finance_data()

    return "success!"


if __name__ == "__main__":
    handle_api_request(request=None)
