from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.chat.models import Chat, Message
from app.chat.schemas import ChatGet, MessageGet, ChatGetAdmin, MessageLast, MessageCreate
from app.core.db import get_db
from app.users.models import User
from app.users.schemas import UserGetName, UserGetFull

chat_router = APIRouter()


@chat_router.get("/all", response_model=list[ChatGet])
async def get_chats(offset: int = 0, limit: int = 100, session: AsyncSession = Depends(get_db)):
    chats = await Chat.get_chats(session, limit, offset)

    return chats


@chat_router.post("/create", response_model=ChatGet)
async def create_chat(user_id: int, session: AsyncSession = Depends(get_db)):
    chat = await Chat.create_chat(session, user_id)
    return chat


@chat_router.get("/{chat_id}", response_model=ChatGet)
async def get_chat(chat_id: int, session: AsyncSession = Depends(get_db),
                   current_user: UserGetFull = Depends(get_current_user)):
    chat = await Chat.get_chat(session, chat_id)
    return chat


@chat_router.get("/{chat_id}/messages", response_model=list[MessageGet])
async def get_messages_by_chat(chat_id: int, session: AsyncSession = Depends(get_db)):
    messages = await Message.get_messages_by_chat_id(session, chat_id)
    return messages


@chat_router.get("/admin/{user_id}", response_model=list[ChatGetAdmin])
async def get_chat_by_admin(user_id: int, session: AsyncSession = Depends(get_db),
                           current_user: UserGetFull = Depends(get_current_user)):
    if current_user.role != "superuser":
        raise HTTPException(status_code=400, detail="Permission denied!")
    chat = await Chat.get_chat_by_user(session, user_id)

    chats = []

    for c in chat:
        # print("messages", c.messages)
        msg = sorted(c.messages, key=lambda x: x.created_at)
        last_msg = msg[-1]
        last_msg_user = await User.get_by_id(session, last_msg.user_id)
        user = None
        for u in c.users:
            if u.role == "guest":
                user = u
        user = UserGetName(id=user.id, username=user.username, role=user.role)
        last_message = MessageLast(id=last_msg.id, message=last_msg.message,
                                   created_at=last_msg.created_at, username=last_msg_user.username)
        current_chat = ChatGetAdmin(id=c.id, user=user, last_message=last_message)
        chats.append(current_chat)
    return chats


@chat_router.get("/user/{user_id}", response_model=list[ChatGetAdmin])
async def get_chat_by_user(user_id: int, session: AsyncSession = Depends(get_db),
                           current_user: UserGetFull = Depends(get_current_user)):
    if current_user.role == "superuser":
        raise HTTPException(status_code=400, detail="Permission denied!")
    chat = await Chat.get_chat_by_user(session, user_id)

    chats = []

    for c in chat:
        # print("messages", c.messages)
        msg = sorted(c.messages, key=lambda x: x.created_at)
        last_msg = msg[-1]
        last_msg_user = await User.get_by_id(session, last_msg.user_id)
        user = None
        for u in c.users:
            if u.role == "superuser":
                user = u
        user = UserGetName(id=user.id, username=user.username, role=user.role)
        last_message = MessageLast(id=last_msg.id, message=last_msg.message,
                                   created_at=last_msg.created_at, username=last_msg_user.username)
        current_chat = ChatGetAdmin(id=c.id, user=user, last_message=last_message)
        chats.append(current_chat)
    return chats


@chat_router.get("/user/{user_id}/messages", response_model=list[MessageGet])
async def get_messages_by_user(user_id: int, session: AsyncSession = Depends(get_db)):
    messages = await Message.get_messages_by_user_id(session, user_id)
    return messages


@chat_router.post("/message/create", response_model=MessageGet)
async def create_message(request: Request, message: MessageCreate, session: AsyncSession = Depends(get_db),
                         current_user: UserGetFull = Depends(get_current_user)):
    print(message)
    print(dict(request.headers.items()))
    print(dict(request.query_params.items()))
    print(await request.json())
    print(await request.body())
    message = await Message.create_message(session, message.message, message.chat_id, message.user_id)
    # print(message.user_id, message.chat_id, message.message)
    return message


@chat_router.delete("/delete/{chat_id}", response_model=ChatGet)
async def delete_chat_by_id(chat_id: int, session: AsyncSession = Depends(get_db)):
    chat = await Chat.delete_chat(session, chat_id)
    return chat

