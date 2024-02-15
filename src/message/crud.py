import logging
from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from aws.service import upload_from_base64
from message.schemas import MessageRead, MemberRead
from models.models import room, user, message, room_user
from user.crud import get_user_by_id

logger = logging.getLogger(__name__)


async def upload_message_to_room(session: AsyncSession, room_name: str, user_name: str, message_data: str):
    try:
        room_id = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        user_id = (await session.execute(select(user).filter_by(username=user_name))).scalar_one()
        await session.execute(insert(message).values(message_data=message_data, user=user_id, room=room_id))
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding message to DB: {type(e)} {e}")
        await session.rollback()
        return False


async def upload_message_with_file_to_room(session: AsyncSession,
                                           room_name: str,
                                           user_name: str,
                                           data_message:str,
                                           base64_data: str,
                                           file_type: str) -> str:
    try:
        room_id = (await session.execute(select(room).filter_by(room_name=room_name))).scalar_one()
        user_id = (await session.execute(select(user).filter_by(username=user_name))).scalar_one()
        media_file_url = await upload_from_base64(base64_data, file_type)
        if "https" not in media_file_url.file_name:
            media_file_url = "https://f003.backblazeb2.com/file/gleb-bucket/" + media_file_url.file_name
        else:
            media_file_url = media_file_url.file_name
        await session.execute(
            insert(message).values(user=user_id, room=room_id, message_data=data_message, media_file_url=media_file_url, ))
        await session.commit()
        return media_file_url
    except Exception as e:
        logger.error(f"Error adding message to DB: {type(e)} {e}")
        await session.rollback()


async def get_messages_in_room(session: AsyncSession, room_id: int) -> List[MessageRead]:
    result = await session.execute(
        select(message)
        .join(room, room.c.room_id == message.c.room)
        .where(room.c.room_id == room_id)
    )
    rows = result.fetchall()
    messages: List[MessageRead] = list()
    for row in rows:
        user_read_request = await get_user_by_id(session, row[4])
        messages.append(MessageRead(
            message=row[1],
            media_file_url=row[2],
            user=user_read_request,
        ))
    await session.commit()
    return messages


async def get_members_in_room(session: AsyncSession, room_id: int) -> List[MemberRead]:
    result = await session.execute(
        select(room_user)
        .join(user, user.c.id == room_user.c.user)
        .where(room.c.room_id == room_id)
    )
    rows = result.fetchall()
    members: List[MemberRead] = list()
    for row in rows:
        members.append(MemberRead(
            user_id=row[0],
            username=row[6],
            profile_pic_img_src=row[9],
            date_created=row[10]
        ))
    await session.commit()
    return members
