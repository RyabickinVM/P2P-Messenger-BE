from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.schemas import UserRead
from database import get_async_session
from src.user.crud import update_user_data, update_user_image
from src.user.schemas import UserUpdateRequest, UserBaseReadRequest

router = APIRouter()


@router.put("/update/me")
async def update_me(
        request: UserUpdateRequest,
        session: AsyncSession = Depends(get_async_session),
        current_user: UserRead = Depends(fastapi_users.current_user()),
) -> None:
    """
    Update the current user
    """
    return await update_user_data(session, current_user, request)


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



