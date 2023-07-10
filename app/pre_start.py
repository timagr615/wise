import asyncio
import os
import time
from app.users.models import User
from app.chat.models import Chat
from app.core.db import get_db, sessionmanager
from app.core.config import settings


async def pre_start():
    time.sleep(7)
    sessionmanager.init(settings.database_url)
    async with sessionmanager.session() as session:
        await User.create_superuser(session)


if __name__ == '__main__':
    asyncio.run(pre_start())