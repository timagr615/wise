from datetime import datetime, timedelta

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import TokenData
from app.core.config import settings
from app.core.db import get_db
from app.users.models import User
from app.users.schemas import UserGetFull

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def verify_token(session: AsyncSession, token: str, credentials_exception) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(f'token {token}')
        username: str = payload.get("sub")
        # print(username)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        # print(token_data)
        user = await User.verify_username(session, username=token_data.username)
        # print(f'user {user.chats[0].users}')
        if not user:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
    except JWTError:
        raise credentials_exception


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(session: AsyncSession = Depends(get_db), data: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credenrtials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return await verify_token(session, data, credentials_exception)

