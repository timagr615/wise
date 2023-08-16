from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, constr

# from app.users.models import User
if TYPE_CHECKING:
    from app.users.schemas import UserGet, UserGetName


class FileBase(BaseModel):
    name: str


class FileUpload(FileBase):
    path: str
    size: int
    message_id: int

    class Config:
        orm_mode = True


class FileDB(FileUpload):
    id: int

    class Config:
        orm_mode = True


class ChatBase(BaseModel):
    id: int
    # users: list[User] = []


class ChatCreate(ChatBase):
    user_id: int


class MessageBase(BaseModel):
    id: int | None
    message: str | None


class MessageCreate(MessageBase):
    user_id: int
    chat_id: int


class MessageGet(MessageBase):
    user_id: int
    chat_id: int
    created_at: datetime
    files: list[FileDB] = []

    class Config:
        orm_mode = True


class ChatGet(ChatBase):

    messages: list[MessageGet] = []
    # users: list['UserGetName'] = []

    class Config:
        orm_mode = True


class UserGetName1(BaseModel):
    username: constr(min_length=2, max_length=50)
    id: int
    role: str | None

    class Config:
        orm_mode = True


class MessageLast(MessageBase):
    created_at: datetime
    username: str


class ChatGetAdmin(ChatBase):
    user: UserGetName1
    last_message: MessageLast

    class Config:
        orm_mode = True
# ChatGet.update_forward_refs()
