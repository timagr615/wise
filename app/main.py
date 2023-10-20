from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.api import api_router
from app.core.config import settings
from app.core.db import sessionmanager

origins = [
    'http://localhost',
    'http://localhost:3000',
    'http://wiseapi.online',
    'https://wiseapi.online',
    'http://194.67.93.32',
    'https://194.67.93.32',
    'https://185.46.8.70',
    'http://185.46.8.70',
]

sessionmanager.init(settings.database_url)
app = FastAPI()
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return {'app name': settings.app_name}

