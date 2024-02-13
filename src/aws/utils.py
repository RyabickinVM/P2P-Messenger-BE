import logging

from src.aws.client import client
from src.config import AWS_BUCKET


async def s3_upload(contents: bytes, key: str) -> None:
    try:
        if len(key) == 0:
            raise ValueError("Invalid 'key' length: 0")

        logging.info(f'Uploading {key} to S3...')
        client.put_object(Key=key, Body=contents, Bucket=AWS_BUCKET)
        logging.info(f'{key} successfully uploaded to S3')
    except Exception as e:
        logging.error(f'Error uploading {key} to S3: {str(e)}')
