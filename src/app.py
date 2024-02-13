from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import message.router as chat_router
from auth.base_config import fastapi_users
from router import router

app = FastAPI(title="PolyTex WebChat", version="0.0.1")

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router.router, tags=["chat"])

app.include_router(router, prefix="/api")

current_user = fastapi_users.current_user()
