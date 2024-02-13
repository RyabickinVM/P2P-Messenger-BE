import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.schemas import UserRead
from database import get_async_session
from ratelimiter import limiter
from room.crud import add_user_to_room, get_rooms, filter_rooms, delete_room, get_user_favorite, \
    get_user_favorite_like_room_name, alter_favorite
from room.schemas import FavoriteRequest

router = APIRouter()
logger = logging.getLogger(__name__)


@router.put("/room/{room_name}")
@limiter.limit("1000/minute")
async def add_user_to_room_members(request: Request,
                                   room_name: str,
                                   current_user: UserRead = Depends(fastapi_users.current_user()),
                                   session: AsyncSession = Depends(get_async_session)):
    """
    Add a user to the room's members
    """
    row = await add_user_to_room(session, current_user.username, room_name)
    return row


@router.get("/rooms")
async def get_all_rooms(page: int = 1, limit: int = 10,
                        current_user: UserRead = Depends(fastapi_users.current_user()),
                        session: AsyncSession = Depends(get_async_session)):
    """
    Get all rooms
    """
    rooms = await get_rooms(session, current_user.id, page, limit)
    return rooms


@router.get("/rooms/{room_name}")
async def filter_out_rooms(room_name: str, page: int = 1, limit: int = 10,
                           current_user: UserRead = Depends(fastapi_users.current_user()),
                           session: AsyncSession = Depends(get_async_session)):
    """
    Filter all rooms
    """
    rooms = await filter_rooms(session, current_user.id, room_name, page, limit)
    return rooms


@router.delete("/room/{room_name}", dependencies=[Depends(fastapi_users.current_user())])
async def delete_room_by_room_name(room_name: str, session: AsyncSession = Depends(get_async_session)):
    """
    Delete Room by room name
    """
    await delete_room(session, room_name)


@router.get("/favorites")
async def get_favorite_rooms(page: int = 1, limit: int = 10, session: AsyncSession = Depends(get_async_session),
                             current_user: UserRead = Depends(fastapi_users.current_user())):
    """
    Get favorites Room objects from a user
    """
    rooms = await get_user_favorite(session, current_user.id, page, limit)
    return rooms


@router.get("/favorite/{room_name}")
async def get_favorite_rooms_by_room_name(room_name: str, page: int = 1, limit: int = 10,
                                          session: AsyncSession = Depends(get_async_session),
                                          current_user: UserRead = Depends(fastapi_users.current_user())):
    """
    Get favorites Room objects from a user
    """
    rooms = await get_user_favorite_like_room_name(session, room_name, current_user.id, page, limit)
    return rooms


@router.post("/favorite")
@limiter.limit("1000/minute")
async def alter_favorite_room(request: Request,
                              favrequest: FavoriteRequest,
                              session: AsyncSession = Depends(get_async_session),
                              current_user: UserRead = Depends(fastapi_users.current_user())):
    """
    Add or remove a favorite room from a user
    the request.is_chosen should be either "true" or "false"
    """
    row = await alter_favorite(session, current_user.id, favrequest)
    return row
