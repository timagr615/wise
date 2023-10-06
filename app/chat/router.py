import os.path
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, Form, status
from fastapi import File as fa_file
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import get_current_user
from app.chat.models import Chat, Message, File
from app.chat.schemas import ChatGet, MessageGet, ChatGetAdmin, MessageLast, MessageCreate
from app.chat.schemas import FileDB, FileUpload
from app.core.db import get_db
from app.users.models import User
from app.users.schemas import UserGetName, UserGetFull
from app.utils.uploads import generate_path, generate_filename

chat_router = APIRouter()
CHUNK_SIZE = 1024*1024


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


@chat_router.get("/message/{message_id}/delete")
async def delete_message_by_id(message_id: int, session: AsyncSession = Depends(get_db)):
    await Message.delete_message_by_id(session, message_id)
    return {"message": message_id, 'deleted': 'success'}


@chat_router.post("/message/create", response_model=MessageGet)
async def create_message(message: MessageCreate,
                         session: AsyncSession = Depends(get_db),
                         current_user: UserGetFull = Depends(get_current_user)):
    message = await Message.create_message(session, message.message, message.chat_id, message.user_id)
    # print(message.user_id, message.chat_id, message.message)
    return message


@chat_router.post("/message_file/create", response_model=MessageGet)
async def create_message_with_file(message: MessageCreate = Depends(),
                                   files: list[UploadFile] | None = None,
                                   session: AsyncSession = Depends(get_db),
                                   current_user: UserGetFull = Depends(get_current_user)):
    # print(message)
    message = await Message.create_message(session, message.message, message.chat_id, message.user_id)
    message_id = message.id
    files_db = []
    if files:
        for file in files:
            path = generate_path()
            if not os.path.exists(path):
                os.makedirs(path, mode=0o666)
            name = generate_filename(file.filename)
            path = os.path.join(path, name)
            try:
                # content = await file.read()
                async with aiofiles.open(path, 'wb') as f:
                    while chunk := await file.read(CHUNK_SIZE):
                        await f.write(chunk)
                f_db = FileUpload(name=name, path=path, size=1, message_id=message_id)
                await File.create_file(session, f_db)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=f'There was an error uploading file: {e}')
            finally:
                await file.close()
            # print(path)
    message = await Message.get_message_by_id(session, message_id)
    # print(message)
    # print(message.user_id, message.chat_id, message.message, message.files)
    return message


@chat_router.delete("/delete/{chat_id}", response_model=ChatGet)
async def delete_chat_by_id(chat_id: int, session: AsyncSession = Depends(get_db)):
    chat = await Chat.delete_chat(session, chat_id)
    return chat


@chat_router.get('/download/{file_id}', response_class=FileResponse)
async def download_file(file_id: int,
                        session: AsyncSession = Depends(get_db),
                        current_user: UserGetFull = Depends(get_current_user)):
    file = await File.get_by_id(session, file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f'File {file_id} not found')
    filename = file.path.split('/')[-1]
    return FileResponse(path=file.path, media_type='application/octet-stream', filename=filename)


@chat_router.get('/files/all', response_model=list[FileDB])
async def get_all_files(offset: int = 0, limit: int = 100, session: AsyncSession = Depends(get_db)):
    files = await File.get_all(session, limit, offset)
    return files


@chat_router.get('/{chat_id}/clear')
async def clear_chat(chat_id: int, session: AsyncSession = Depends(get_db),
                     current_user: UserGetFull = Depends(get_current_user)):
    if current_user.role != "superuser":
        raise HTTPException(status_code=400, detail="Permission denied!")
    await Message.clear_messages_by_chat_id(session, chat_id)
