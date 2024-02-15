from datetime import datetime
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    last_name: Optional[str]
    first_name: Optional[str]
    surname: Optional[str]
    image_url: Optional[str]
    creation_date: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    surname: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
