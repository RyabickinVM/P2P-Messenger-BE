import boto3

from config import ENDPOINT, KEY_ID_RO, APPLICATION_KEY_RO

client = boto3.client(
    service_name='s3',
    endpoint_url=ENDPOINT,
    aws_access_key_id=KEY_ID_RO,
    aws_secret_access_key=APPLICATION_KEY_RO
)
