from datetime import datetime
from typing import TypeVar, TYPE_CHECKING, Type

from sqlalchemy import Integer, Table, Column, ForeignKey, String, select, delete, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped

from app.chat.associations import association_table
from app.core.db import Base
# if TYPE_CHECKING:
from app.users.models import User
from app.users.schemas import UserGetName

C = TypeVar('C', bound='Chat')
M = TypeVar('M', bound='Message')


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    users: Mapped[list['User']] = relationship('User', secondary=association_table, back_populates="chats", lazy='selectin')
    messages: Mapped[list['Message']] = relationship("Message", back_populates="chat", lazy='selectin')

    @classmethod
    async def create_chat(cls: Type[C], session: AsyncSession, user_id: int) -> C:
        user = await User.get_by_id(session, user_id)
        if user.chats:
            return user.chats[0]
        superuser = await User.get_superuser(session)
        users = [user, superuser]
        # print(users)
        chat = cls()
        # chat.messages = []
        chat.users.extend(users)
        # print(chat)
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat

    @classmethod
    async def get_chats(cls: Type[C], session: AsyncSession, limit: int = 100, offset: int = 0) -> list[C]:
        chats = select(cls).limit(limit).offset(offset)
        result = await session.execute(chats)
        return result.scalars().all()

    @classmethod
    async def get_chat(cls: Type[C], session: AsyncSession, chat_id: int) -> C | None:
        chat = select(cls).where(cls.id == chat_id)
        result = await session.execute(chat)
        res = result.scalars().first()

        return res

    @classmethod
    async def get_chat_by_user(cls: Type[C], session: AsyncSession, user_id: int) -> list[C]:
        chat = select(cls).join(cls.users).where(User.id == user_id)
        result = await session.execute(chat)
        res = result.scalars().all()
        return res

    @classmethod
    async def delete_chat(cls: Type[C], session: AsyncSession, chat_id: int) -> C:
        query = delete(cls).where(cls.id == chat_id)
        data = await session.execute(query)
        await session.commit()
        return data.scalars().first()


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped['User'] = relationship('User', back_populates="messages", lazy="selectin")
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id', ondelete="CASCADE"))
    chat: Mapped['Chat'] = relationship('Chat', back_populates="messages", lazy="selectin")

    def __repr__(self):
        return f"CHAT {self.id} users: {self.user}"

    @classmethod
    async def create_message(cls: Type[M], session: AsyncSession, message: str, chat_id: int, user_id: int) -> M:
        chat = await Chat.get_chat(session, chat_id)
        if not chat:
            chat = await Chat.create_chat(session, user_id)
        message = cls(
            message=message,
            chat_id=chat.id,
            user_id=user_id
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    @classmethod
    async def get_messages_by_chat_id(cls: Type[M], session: AsyncSession, chat_id: int) -> list[M]:
        messages = select(cls).where(cls.chat_id == chat_id)
        result = await session.execute(messages)
        return result.scalars().all()

    @classmethod
    async def get_messages_by_user_id(cls: Type[M], session: AsyncSession, user_id: int) -> list[M]:
        messages = select(cls).where(cls.user_id == user_id)
        result = await session.execute(messages)
        return result.scalars().all()
