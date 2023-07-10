from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.chat.models import Message
from app.core.db import get_db
from app.users.models import User
from app.users.schemas import UserGet, UserGetFull, UserCreate, UserBase

user_router = APIRouter()


@user_router.get("/all", response_model=list[UserGet])
async def read_users(offset: int = 0, limit: int = 100, db_session: AsyncSession = Depends(get_db)):
    # print("whatafuck")
    users = await User.get_all(db_session, limit, offset)
    # print(users[0].chats[0].messages[0].message)
    return users


@user_router.get('/me', response_model=UserGetFull)
async def get_me(current_user: UserGetFull = Depends(get_current_user)):
    # print(current_user)
    return current_user


@user_router.get("/{user_id}", response_model=UserGetFull)
async def get_user(user_id: int, db_session: AsyncSession = Depends(get_db)):
    user = await User.get_by_id(db_session, user_id)
    # \print(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return user


@user_router.post("/create", response_model=UserGetFull, status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: UserCreate, db_session: AsyncSession = Depends(get_db)):
    print(dict(request.headers.items()))
    print(dict(request.query_params.items()))
    print(await request.json())
    print(await request.body())
    exist = await User.verify_username(db_session, user.username)
    if exist:
        raise HTTPException(status_code=400, detail="User with this email already exists in the system")

    new_user = await User.user_registration(db_session, user)
    message = await Message.create_message(db_session, "Беседа начата", 0, new_user.id)
    # print(new_user)
    return new_user




