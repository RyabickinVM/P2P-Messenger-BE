from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Index, ForeignKeyConstraint, Boolean, \
    UniqueConstraint

metadata = MetaData()

room = Table(
    "room",
    metadata,
    Column("room_id", Integer, primary_key=True, autoincrement=True),
    Column("room_name", String(40), unique=True, nullable=False),
    Column("is_active", Boolean, default=False, nullable=False),
    Column("creation_date", DateTime, default=datetime.utcnow, nullable=False)
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(40), unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("image_url", String, nullable=True),
    Column("creation_date", DateTime, default=datetime.utcnow, nullable=False),
    Column("last_name", String(20), nullable=True),
    Column("first_name", String(20), nullable=True),
    Column("surname", String(20), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False)
)

room_user = Table(
    "room_user",
    metadata,
    Column("creation_date", DateTime, default=datetime.utcnow, nullable=False),
    Column("update_date", DateTime, default=datetime.utcnow, nullable=True),
    Column("is_chosen", Boolean, default=False, nullable=False),
    Column("is_active", Boolean, default=False, nullable=False),
    Column("is_owner", Boolean, default=False, nullable=False),
    Column("user", Integer, nullable=False),
    Column("room", Integer, nullable=False),
    Index("idx_chosen__room", "room"),
    Index("idx_chosen__user", "user"),
    ForeignKeyConstraint(["room"], ["room.room_id"], ondelete="CASCADE"),
    ForeignKeyConstraint(["user"], ["user.id"], ondelete="CASCADE"),
    UniqueConstraint('user', 'room', name='uq_user_room')
)

message = Table(
    "message",
    metadata,
    Column("message_id", Integer, primary_key=True, autoincrement=True),
    Column("message_data", String(4096), nullable=False),
    Column("media_file_url", String),
    Column("creation_date", DateTime, nullable=False, default=datetime.utcnow),
    Column("user", Integer, nullable=False),
    Column("room", Integer, nullable=False),
    Index("idx_message__room", "room"),
    Index("idx_message__user", "user"),
    ForeignKeyConstraint(["room"], [room.c.room_id], ondelete="CASCADE"),
    ForeignKeyConstraint(["user"], [user.c.id], ondelete="CASCADE")
)