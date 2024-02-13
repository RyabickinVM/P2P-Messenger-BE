import os

from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

ENDPOINT = os.environ.get("ENDPOINT")
KEY_ID_RO = os.environ.get("KEY_ID_RO")
APPLICATION_KEY_RO = os.environ.get("APPLICATION_KEY_RO")
AWS_BUCKET = os.environ.get("AWS_BUCKET")

SECRET_AUTH = os.environ.get("SECRET_AUTH")
