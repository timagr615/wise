from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Wise+ chat"
    admin_username: str
    admin_password: str

    database_url: str
    file_storage_path: str
    secret_key: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
