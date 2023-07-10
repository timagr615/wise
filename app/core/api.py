from fastapi import APIRouter

from app.auth.router import auth_router
from app.chat.router import chat_router
from app.users.router import user_router

api_router = APIRouter()
api_router.include_router(user_router, prefix='/user', tags=['users'])
api_router.include_router(chat_router, prefix='/chat', tags=['chats'])
api_router.include_router(auth_router, tags=['auth'])
