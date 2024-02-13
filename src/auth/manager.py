import re
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException, schemas, exceptions
from sqlalchemy import select

from config import SECRET_AUTH
from auth.exceptions import InvalidLoginException
from auth.models import User
from auth.schemas import UserCreate
from auth.utils import get_user_db
from database import get_async_session_context


async def get_by_username(username: str) -> Optional[User]:
    async with get_async_session_context() as session:
        user = await session.execute(select(User).filter(User.username == username))
        return user.scalar_one_or_none()


async def validate_username(username: str) -> None:
    regex = r"^(?=.*[A-Za-zА-Яа-я])(?=.*[0-9]).{4,20}$"
    if not re.search(regex, username):
        raise InvalidLoginException(
            reason="Login must consist of upper/lowercase letters (cyrillic, latin) and digits.")
    if not (4 <= len(username) <= 20):
        raise InvalidLoginException(
            reason="Login's length must be from 4 to 20 symbols.")


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_AUTH
    verification_token_secret = SECRET_AUTH

    # если логин все таки это email удалить данную фукнцию!
    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> Optional[User]:
        user = await get_by_username(credentials.username)

        if user is None:
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_password_hash})

        return user

    async def create(self, user_create: schemas.UC, safe: bool = True, request: Optional[Request] = None) -> User:

        await validate_username(user_create.username)

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def validate_password(self, password: str, user: Union[UserCreate, User]) -> None:
        if not (6 <= len(password) <= 40):
            raise InvalidPasswordException(
                reason="Password's length must be from 6 to 40 symbols.")
        if not any(char.isalpha() for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one letter.")
        if not any(char.isdigit() for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one digit.")
        if not any(char.isalnum() or char in "!@#$%^&*()-_=+" for char in password):
            raise InvalidPasswordException(
                reason="Password must contain at least one special character.")

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
