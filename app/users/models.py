from typing import Type, TypeVar, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.associations import association_table
from app.core.config import settings
from app.core.db import Base
from app.users.hashing import verify_password, get_hashed_password
from app.users.schemas import UserCreate
if TYPE_CHECKING:
    from app.chat.models import Chat, Message

T = TypeVar('T', bound='User')



'''A = TypeVar('A', bound='Admin')


class Admin(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Admin {self.username} {self.password}'

    def check_password(self, password: str) -> bool:
        return verify_password(self.password, password)

    @classmethod
    async def verify_username(cls: Type[A], session: AsyncSession, username: str) -> A | None:
        query = select(cls).where(cls.username == username)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def admin_registration(cls: Type[A], session: AsyncSession, admin: AdminCreate) -> A:
        admin.password = get_hashed_password(admin.password)
        new_instance = cls(**admin.dict())
        session.add(new_instance)
        await session.commit()
        await session.refresh(new_instance)
        return new_instance

    @classmethod
    async def get_by_id(cls: Type[A], session: AsyncSession, id: int) -> A | None:
        admin = select(cls).where(cls.id == id)
        result = await session.execute(admin)
        return result.scalars().first()

    @classmethod
    async def get_all(cls: Type[A], session: AsyncSession, limit: int = 100, offset: int = 0) -> list[A]:
        query = select(cls).offset(offset).limit(limit)
        admins = await session.execute(query)
        return admins.scalars().all()

    @classmethod
    async def create_superuser(cls: Type[A], session: AsyncSession) -> None:
        already_exist = await cls.verify_username(session, settings.admin_username)
        if already_exist:
            return
        admin = cls(
            username=settings.admin_username,
            password=get_hashed_password(settings.admin_password),
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)'''


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), default='guest')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chats: Mapped[list['Chat']] = relationship("Chat", secondary=association_table, back_populates="users", lazy="selectin")
    messages: Mapped[list['Message']] = relationship("Message", back_populates="user", lazy='selectin')

    def __repr__(self):
        return f"USER: {self.username} {self.password} {self.role}"

    def check_password(self, password: str) -> bool:
        return verify_password(self.password, password)

    @classmethod
    async def verify_username(cls: Type[T], session: AsyncSession, username: str) -> T | None:
        query = select(cls).where(cls.username == username)
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def user_registration(cls: Type[T], session: AsyncSession, user: UserCreate) -> T:
        user.password = get_hashed_password(user.password)
        new_instance = cls(**user.dict())
        session.add(new_instance)
        await session.commit()
        await session.refresh(new_instance)
        return new_instance

    @classmethod
    async def get_superuser(cls: Type[T], session: AsyncSession) -> T:
        user = select(cls).where(cls.role == "superuser")
        result = await session.execute(user)
        return result.scalars().first()

    @classmethod
    async def get_by_id(cls: Type[T], session: AsyncSession, id: int) -> T | None:
        user = select(cls).where(cls.id == id)
        result = await session.execute(user)
        return result.scalars().first()

    @classmethod
    async def get_all(cls: Type[T], session: AsyncSession, limit: int = 100, offset: int = 0) -> list[T]:
        query = select(cls).offset(offset).limit(limit)
        users = await session.execute(query)
        return users.scalars().all()

    @classmethod
    async def create_superuser(cls: Type[T], session: AsyncSession) -> None:
        already_exist = await cls.verify_username(session, settings.admin_username)
        if already_exist:
            return
        user = cls(
            username=settings.admin_username,
            password=get_hashed_password(settings.admin_password),
            role='superuser',
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)



