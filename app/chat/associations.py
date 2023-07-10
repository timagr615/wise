from sqlalchemy import Table, Column, Integer, ForeignKey

from app.core.db import Base

association_table = Table(
    "association_table",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)