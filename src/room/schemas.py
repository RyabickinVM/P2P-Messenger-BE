import datetime
from typing import List

from pydantic import BaseModel

from message.schemas import MessageRead
from user.schemas import UserReadRequest


class RoomBaseRequest(BaseModel):
    room_name: str


class RoomCreateRequest(RoomBaseRequest):
    pass


class RoomBaseInfoRequest(RoomBaseRequest):
    room_id: int


class RoomBaseInfoForUserRequest(RoomBaseInfoRequest):
    is_favorites: bool


class RoomBaseInfoForAllUserRequest(RoomBaseInfoForUserRequest):
    is_owner: bool


class RoomReadRequest(RoomBaseInfoRequest):
    members: List[UserReadRequest]
    messages: List[MessageRead]
    room_active: bool
    room_creation_date: datetime.datetime


class FavoriteRequest(BaseModel):
    room_name: str
    is_chosen: bool
