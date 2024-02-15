from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.schemas import UserRead
from database import get_async_session
from user.crud import update_user_image
from user.schemas import UserBaseReadRequest

router = APIRouter()


@router.post("/profile_picture")
async def upload_profile_picture(
        file: Optional[UploadFile] = None,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> Optional[UserBaseReadRequest]:
    """
    Upload a profile picture for the current user
    """
    return await update_user_image(session, current_user, file)
