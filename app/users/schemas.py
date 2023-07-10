from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, constr

# if TYPE_CHECKING:
from app.chat.schemas import ChatGet, MessageGet


class UserBase(BaseModel):

    username: constr(min_length=2, max_length=50)


class UserCreate(UserBase):
    password: str


class UserGet(UserBase):
    id: int
    #chats: list[ChatGet] = []
    messages: list[MessageGet] = []

    class Config:
        orm_mode = True


class UserGetName(UserBase):

    id: int
    role: str | None

    class Config:
        orm_mode = True


class UserGetFull(UserBase):
    id: int
    role: str | None
    created_at: datetime | None
    # chats: list[ChatGet] = []

    class Config:
        orm_mode = True
