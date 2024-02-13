from pydantic import BaseModel


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


class FavoriteRequest(BaseModel):
    room_name: str
    is_chosen: bool
