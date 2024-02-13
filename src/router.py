from fastapi import APIRouter

import room.router as room_router
import user.router as user_router
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserUpdate, UserRead

router = APIRouter()

# auth
# include login & logout
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])

# registration
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), tags=["auth"])

# verify
# include verify & request-verify-token
router.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])

# reset
# include forgot-password & reset-password
router.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])

# update user
router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/user", tags=["users"])

# Get URL of current user's profile picture & update profile picture
router.include_router(user_router.router, prefix="/user", tags=["users"])

# rooms
router.include_router(room_router.router, tags=["rooms"])
