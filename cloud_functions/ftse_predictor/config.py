import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = "gdelt-ftse"
GOOGLE_SHEET_ID = "1_j1C4hY7hKtuaYzaZSepyM4s_9yY4nY8Y7zEi3-b29o"
SERVICE_ACCOUNT_CREDENTIALS: dict = eval(os.environ.get("service_account_credentials"))
