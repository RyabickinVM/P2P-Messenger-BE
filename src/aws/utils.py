import logging
from typing import Optional

from botocore.exceptions import ClientError

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


async def s3_URL(key: str) -> Optional[str]:
    try:
        url = client.generate_presigned_url('get_object', Params={'Bucket': AWS_BUCKET, 'Key': key})
        return url
    except ClientError as e:
        print(f"Error generating presigned URL: {str(e)}")
        return None


async def s3_download(key: str) -> bytes:
    logging.info(f'Downloading {key} from s3...')
    try:
        response = client.get_object(Bucket=AWS_BUCKET, Key=key)
        return response['Body'].read()
    except ClientError as err:
        logging.error(str(err))
