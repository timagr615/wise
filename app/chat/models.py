from datetime import datetime
from typing import TypeVar, TYPE_CHECKING, Type, Annotated, Self

from sqlalchemy import Integer, Table, Column, ForeignKey, String, select, delete, DateTime, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped

from app.chat.associations import association_table
from app.chat.schemas import FileUpload
from app.core.db import Base
# if TYPE_CHECKING:
from app.users.models import User
from app.users.schemas import UserGetName

C = TypeVar('C', bound='Chat')
M = TypeVar('M', bound='Message')
F = TypeVar('F', bound='File')


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    users: Mapped[list['User']] = relationship('User', secondary=association_table, back_populates="chats", lazy='selectin')
    messages: Mapped[list['Message']] = relationship("Message", back_populates="chat", lazy='selectin')

    @classmethod
    async def create_chat(cls: Type[Self], session: AsyncSession, user_id: int) -> Self:
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
    files: Mapped[list['File']] = relationship('File', back_populates='message', lazy='selectin')

    def __repr__(self):
        return f"CHAT {self.id}, {self.message}"

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

    # @classmethod
    # async def update_message_files(cls: Type[M], session: AsyncSession, message_id: str, files: ):

    @classmethod
    async def get_message_by_id(cls: Type[M], session: AsyncSession, message_id: int) -> M:
        message = select(cls).where(cls.id == message_id)
        result = await session.execute(message)
        return result.scalars().first()

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

    @classmethod
    async def delete_message_by_id(cls: Type[M], session: AsyncSession, message_id: int) -> bool:
        msg = delete(cls).where(cls.id == message_id)
        await session.execute(msg)
        await session.commit()
        return True

    @classmethod
    async def delete_all_messages(cls: Type[M], session: AsyncSession, messages_id: list[int]) -> bool:
        msg = delete(cls).where(cls.id.in_(messages_id))
        await session.execute(msg)
        await session.commit()
        return True

    @classmethod
    async def clear_messages_by_chat_id(cls: Type[M], session: AsyncSession, chat_id: int) -> None:
        try:
            messages = await cls.get_messages_by_chat_id(session, chat_id)
            mes = []
            for i in range(len(messages)):
                if i != 0:
                    mes.append(messages[i].id)
            await cls.delete_all_messages(session, mes)
        except Exception as e:
            print(e)


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, default=datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f"))
    path: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    message_id: Mapped[int] = mapped_column(ForeignKey('messages.id', ondelete="CASCADE"))
    message: Mapped['Message'] = relationship('Message', back_populates='files', lazy='selectin')

    def __repr__(self):
        print(f'File from message: {self.message_id}. Name: {self.name}, Path: {self.path}, Size: {self.size}')

    @classmethod
    async def create_file(cls: Type[F], session: AsyncSession, data: FileUpload) -> F:
        file = cls(**data.dict())
        session.add(file)
        await session.commit()
        await session.refresh(file)
        return file

    @classmethod
    async def get_all(cls: Type[F], session: AsyncSession, limit: int = 100, offset: int = 0) -> list[F]:
        data = await session.execute(select(cls).offset(offset).limit(limit))
        return data.scalars().all()

    @classmethod
    async def get_by_id(cls: Type[F], session: AsyncSession, file_id: int) -> F:
        query = select(cls).where(cls.id == file_id)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def get_by_path(cls: Type[F], session: AsyncSession, path: str) -> F:
        query = select(cls).where(cls.path == path)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def get_by_message_id(cls: Type[F], session: AsyncSession, message_id: int) -> F:
        query = select(cls).where(cls.message_id == message_id)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def get_message_file(cls: Type[F], session: AsyncSession, message_id: int, file_id: int) -> F:
        query = select(cls).where(cls.message_id == message_id).where(cls.id == file_id)
        data = await session.execute(query)
        return data.scalars().first()

    @classmethod
    async def delete_by_id(cls: Type[F], session: AsyncSession, file_id: int) -> F:
        query = delete(cls).where(cls.id == file_id).returning(cls.path)
        data = await session.execute(query)
        await session.commit()
        return data.scalars().first()

    @classmethod
    async def update_file_size(cls: Type[F], session: AsyncSession, size: int, path: str) -> F:
        data_d = {'size': size}
        file = await cls.get_by_path(session, path)
        query = update(cls).where(cls.id == file.id).values(**data_d).execution_options(synchronize_session="fetch")
        data = await session.execute(query)
        await session.commit()
        return data.scalars().first()
