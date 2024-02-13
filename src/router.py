from fastapi import APIRouter

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead

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