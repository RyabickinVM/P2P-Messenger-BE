import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, insert, delete, and_, update
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import room, user, room_user, message
from room.schemas import RoomBaseInfoForUserRequest, FavoriteRequest, RoomBaseInfoForAllUserRequest

logger = logging.getLogger(__name__)


async def delete_room(session: AsyncSession, room_name: str) -> None:
    try:
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).one()
        room_id = room_instance.room_id
        await session.execute(delete(room).filter_by(room_id=room_id))
        await session.execute(delete(room_user).filter_by(room=room_id))
        await session.execute(delete(message).filter_by(room=room_id))
        await session.commit()
    except Exception as e:
        logger.error(f"Error deleting room: {e}")
        await session.rollback()


async def filter_rooms(session: AsyncSession, current_user_id: int, room_name: str, page: int = 1, limit: int = 10) \
        -> Optional[List[RoomBaseInfoForUserRequest]]:
    try:
        query = await session.execute(
            select(
                room.c.room_id,
                room.c.room_name,
                room_user.c.is_chosen,
                room_user.c.creation_date
            )
            .join(room_user, and_(room.c.room_id == room_user.c.room, room_user.c.user == current_user_id),
                  isouter=True)
            .filter(room.c.room_name.ilike(f'%{room_name}%'))
            .order_by(
                room_user.c.update_date.desc(),
                room_user.c.is_chosen.desc()
            )
            .limit(limit)
            .offset((page - 1) * limit)
        )
        rooms: List[RoomBaseInfoForUserRequest] = list()
        rows = query.fetchall()
        for row in rows:
            rooms.append(
                RoomBaseInfoForUserRequest(
                    room_id=row[0],
                    room_name=row[1],
                    is_favorites=row[2] if row[2] is not None else False
                )
            )
        rooms.sort(key=lambda x: x.is_favorites, reverse=True)
        await session.commit()
        return rooms
    except Exception as e:
        logger.error(f"Error filtering rooms: {e}")
        return None


# todo: добавить значени если пользователь в первый раз заходит в команту.
async def add_user_to_room(session: AsyncSession, username: str, room_name: str):
    try:
        user_instance = (await session.execute(select(user).filter_by(username=username))).scalar_one()
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        entity_room_user = (await session.execute(
            select(room_user)
            .where(and_(room_user.c.user == user_instance, room_user.c.room == room_instance))
        )).scalar_one_or_none()
        if entity_room_user is None:
            association = room_user.insert().values(user=user_instance, room=room_instance, is_active=True)
            await session.execute(association)
            await session.commit()
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error adding user to room: {e}")
        await session.rollback()
        return None


async def set_user_room_activity(session: AsyncSession, username: str, room_name: str, is_active: bool):
    try:
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        user_instance = (await session.execute(select(user).filter_by(username=username))).scalar_one()
        await session.execute(
            update(room_user).where(
                and_(room_user.c.user == user_instance, room_user.c.room == room_instance)
            ).values(is_active=is_active)
        )
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error removing user from room: {e}")
        await session.rollback()
        return False


async def set_room_activity(session: AsyncSession, room_name: str, activity_bool: bool):
    try:
        await session.execute(update(room).where(room.c.room_name == room_name).values(is_active=activity_bool))
        room_instance = (await session.execute(select(room).filter_by(room_name=room_name))).one()
        await session.commit()
        return room_instance
    except Exception as e:
        logger.error(f"Error setting room activity: {e}")
        await session.rollback()
        return None


async def get_rooms(session: AsyncSession, current_user_id: int, page: int = 1, limit: int = 10) \
        -> Optional[List[RoomBaseInfoForUserRequest]]:
    try:
        query = await session.execute(
            select(
                room.c.room_id,
                room.c.room_name,
                room_user.c.is_chosen,
                room_user.c.creation_date
            )
            .join(room_user, and_(room.c.room_id == room_user.c.room, room_user.c.user == current_user_id),
                  isouter=True)
            .order_by(
                room_user.c.update_date.desc(),
                room_user.c.is_chosen.desc()
            )
            .limit(limit)
            .offset((page - 1) * limit)
        )
        rooms: List[RoomBaseInfoForUserRequest] = list()
        rows = query.fetchall()
        for row in rows:
            rooms.append(
                RoomBaseInfoForUserRequest(
                    room_id=row[0],
                    room_name=row[1],
                    is_favorites=row[2] if row[2] is not None else False
                )
            )
        rooms.sort(key=lambda x: x.is_favorites, reverse=True)
        await session.commit()
        return rooms
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return None


async def get_user_favorite(session: AsyncSession, current_user_id: int, page: int = 1, limit: int = 10) \
        -> Optional[List[RoomBaseInfoForAllUserRequest]]:
    try:
        query = await (session.execute(
            select(room, room_user)
            .join(room_user, and_(room.c.room_id == room_user.c.room, room_user.c.user == current_user_id,
                                  room_user.c.is_chosen is True))
            .order_by(room_user.c.update_date.desc())
            .limit(limit)
            .offset((page - 1) * limit)
        ))
        rooms = list()
        rows = query.fetchall()
        for row in rows:
            rooms.append(
                RoomBaseInfoForAllUserRequest(
                    room_id=row[0],
                    room_name=row[1],
                    is_favorites=row[6] if row[6] is not None else False,
                    is_owner=row[8] if row[8] is not None else False
                )
            )
        await session.commit()
        return rooms
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return None


async def get_user_favorite_like_room_name(session: AsyncSession, room_name: str, current_user_id: int, page: int = 1,
                                           limit: int = 10) \
        -> Optional[List[RoomBaseInfoForAllUserRequest]]:
    try:
        query = await (session.execute(
            select(room, room_user)
            .join(room_user, and_(room.c.room_id == room_user.c.room, room_user.c.user == current_user_id,
                                  room_user.c.is_chosen is True, room.c.room_name.ilike(f'%{room_name}%')))
            .order_by(room_user.c.update_date.desc())
            .limit(limit)
            .offset((page - 1) * limit)
        ))
        rooms = list()
        rows = query.fetchall()
        for row in rows:
            rooms.append(
                RoomBaseInfoForAllUserRequest(
                    room_id=row[0],
                    room_name=row[1],
                    is_favorites=row[6] if row[6] is not None else False,
                    is_owner=row[8] if row[8] is not None else False
                )
            )
        await session.commit()
        return rooms
    except Exception as e:
        logger.error(f"Error getting rooms: {e}")
        return None


async def alter_favorite(session: AsyncSession, current_user_id: int, request: FavoriteRequest) -> None:
    try:
        room_instance = (await session.execute(select(room).filter_by(room_name=request.room_name))).scalar_one()
        entity_room_user = (await session.execute(
            select(room_user)
            .where(and_(room_user.c.user == current_user_id, room_user.c.room == room_instance))
        )).scalar_one_or_none()
        if entity_room_user is not None:
            await (session.execute(
                update(room_user)
                .where(and_(room_user.c.user == current_user_id, room_user.c.room == room_instance))
                .values(is_chosen=request.is_chosen, update_date=datetime.now())
            ))
            await session.commit()
        else:
            await (session.execute(
                insert(room_user)
                .values(user=current_user_id, room=room_instance, is_chosen=request.is_chosen,
                        creation_date=datetime.now())
            ))
            await session.commit()
    except NoResultFound as e:
        logger.error(f"Error: {e}. The requested data does not exist in the database.")
        await session.rollback()
    except MultipleResultsFound as e:
        logger.error(f"Error: {e}. Multiple results found for the query.")
        await session.rollback()
    except Exception as e:
        logger.error(f"Error altering room: {e}")
        await session.rollback()
        return None
