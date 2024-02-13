from datetime import datetime
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_name: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(20))
    surname: Mapped[Optional[str]] = mapped_column(String(20))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
