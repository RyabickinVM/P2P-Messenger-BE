from typing import Optional

from pydantic import BaseModel

from user.schemas import UserReadRequest


class MessageRead(BaseModel):
    message: str
    media_file_url: Optional[str]
    user: UserReadRequest


class MemberRead(BaseModel):
    user_id: int
    username: str
    profile_pic_img_src: Optional[str]
    date_created: str
