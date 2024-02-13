import base64
import time
from io import BytesIO
from typing import Optional
from uuid import uuid4

import av
import magic
from PIL import Image
from fastapi import HTTPException, Response, UploadFile, status

from aws.constants import MB, SUPPORTED_FILE_TYPES_FORM_IMAGE, SUPPORTED_FILE_TYPES_FORM_AUDIO, \
    SUPPORTED_FILE_TYPES_FORM_VIDEO, SUPPORTED_FILE_TYPES_FORM_APPLICATION
from aws.schemas import FileRead
from aws.utils import s3_download, s3_upload, s3_URL

import shotstack_sdk
from shotstack_sdk.api import edit_api
from shotstack_sdk.model.clip import Clip
from shotstack_sdk.model.edit import Edit
from shotstack_sdk.model.output import Output
from shotstack_sdk.model.timeline import Timeline
from shotstack_sdk.model.track import Track
from shotstack_sdk.model.video_asset import VideoAsset
import certifi

from config import SHOTSTACK_API


async def compress_video(video_data: bytes, file_type: str, resize_flag: bool) -> FileRead:
    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_APPLICATION[file_type]}'
    await s3_upload(contents=video_data, key=file_name)

    current_video_url_in_backblaze = await get_url(file_name)

    configuration = shotstack_sdk.Configuration(host='https://api.shotstack.io/stage')
    configuration.ssl_ca_cert = certifi.where()
    configuration.verify_ssl = False
    configuration.api_key['DeveloperKey'] = SHOTSTACK_API

    with shotstack_sdk.ApiClient(configuration) as api_client:
        api_instance = edit_api.EditApi(api_client)

        api_response = api_instance.probe(current_video_url_in_backblaze)

        streams = api_response['response']['metadata']['streams']

        duration = None
        for stream in streams:
            if stream['codec_type'] == "video":
                duration = stream['duration']

        video_asset = VideoAsset(
            src=current_video_url_in_backblaze
        )

        video_clip = Clip(
            asset=video_asset,
            start=0.0,
            length=float(duration)
        )

        track = Track(clips=[video_clip])

        timeline = Timeline(
            background="#000000",
            tracks=[track]
        )
        if resize_flag:
            output = Output(format="mp4", resolution="hd")
        else:
            output = Output(format="mp4", resolution="sd")

        edit = Edit(timeline=timeline, output=output)

        url = None
        try:
            api_id = api_instance.post_render(edit)
            id = api_id['response']['id']

            while True:
                api_response = api_instance.get_render(id, data=False, merged=True)
                status = api_response['response']['status']
                if status == "done":
                    url = api_response['response']['url']
                    break
                elif status == 'failed':
                    print(">> Something went wrong, rendering has terminated and will not continue.")
                    break
                print('Status: ' + status.upper() + '\n')
                time.sleep(1)

        except Exception as e:
            print(f"Unable to resolve API call: {e}")

    return FileRead(file_name=str(url))


async def compress_image(file_type: str, image_data: bytes) -> bytes:
    try:
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        img_io = BytesIO()

        if width >= 2048 or height >= 1080:
            img.thumbnail((2048, 1080))

        img.save(img_io, format=SUPPORTED_FILE_TYPES_FORM_IMAGE[file_type])

        return img_io.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error compressing image: {str(e)}'
        )


async def upload_from_base64(base64_data: str, file_type: str) -> Optional[FileRead]:
    if not base64_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Base64 data not found!'
        )

    contents = base64.b64decode(base64_data)
    size = len(contents)

    if file_type in SUPPORTED_FILE_TYPES_FORM_AUDIO:
        max_size = 8 * MB
        error_message = f'Audio file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.'

    elif file_type in SUPPORTED_FILE_TYPES_FORM_VIDEO:
        max_size = 50 * MB
        error_message = f'Video file size exceeds the maximum allowed one of {max_size / MB} MB. Try another one.'

        container = av.open(BytesIO(contents))
        video_stream_info = container.streams.video[0]
        width = video_stream_info.width
        height = video_stream_info.height

        resize_flag = width >= 1920 or height >= 1080
        size_flag = size >= 8 * MB

        if resize_flag or size_flag:
            return await compress_video(contents, file_type, resize_flag)

        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    elif file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
        max_size = 10 * MB
        error_message = 'Image file size should not exceed 10 MB.'
        img = Image.open(BytesIO(contents))
        width, height = img.size

        if width < 100 or height < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Image size is too small. More than 100x100 is required.'
            )
        if (width > 2048 or height > 1080) or (1 * MB <= size <= 10 * MB):
            contents = await compress_image(file_type, contents)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. '
                   f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO}'
                   f'{SUPPORTED_FILE_TYPES_FORM_VIDEO}'
                   f'{SUPPORTED_FILE_TYPES_FORM_IMAGE}'
        )

    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_APPLICATION[file_type]}'
    await s3_upload(contents=contents, key=file_name)
    return FileRead(file_name=file_name)


async def upload(file: Optional[UploadFile] = None) -> Optional[FileRead]:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File not found!'
        )

    contents = await file.read()
    size = len(contents)

    file_type = magic.from_buffer(buffer=contents, mime=True)
    file_name = ''

    if file_type in SUPPORTED_FILE_TYPES_FORM_IMAGE:
        try:
            img = Image.open(BytesIO(contents))
            width, height = img.size

            if width <= 10 or height <= 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Image size is too small to be previewed. More than 10x10 is required.'
                )
            if (width > 2048 or height > 1080) or (1 * MB <= size <= 10 * MB):
                contents = await compress_image(file_type, contents)
            if size > 10 * MB:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Image file size should not exceed 10 MB. '
                )
            file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES_FORM_APPLICATION[file_type]}'
        except Exception:
            print("Compression failed.")
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. '
                   f'Supported types are {SUPPORTED_FILE_TYPES_FORM_AUDIO + SUPPORTED_FILE_TYPES_FORM_VIDEO + SUPPORTED_FILE_TYPES_FORM_IMAGE}'
        )

    await s3_upload(contents=contents, key=file_name)
    return FileRead(file_name=file_name)


async def get_url(file_name: Optional[str] = None):
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided.'
        )

    contents = await s3_URL(key=file_name)
    return contents


async def download(file_name: Optional[str] = None) -> Response:
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file name provided.'
        )

    contents = await s3_download(key=file_name)
    return Response(
        content=contents,
        headers={
            'Content-Disposition': f'attachment;filename={file_name}',
            'Content-Type': 'application/octet-stream',
        }
    )
