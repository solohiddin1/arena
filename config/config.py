from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()



class Settings(BaseSettings):
    PHOTO_PATH: str
    DEFAULT_PHOTO_PATH: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_ENGINE: str
    ALLOWED_HOSTS: list[str]
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_USE_TLS: bool
    DEFAULT_FROM_EMAIL: str
    SERVER_EMAIL: str
    EMAIL_BACKEND: str
    TIME_ZONE: str
    LANGUAGE_CODE: str

    class Config:
        env_file = ".env"
    

settings = Settings()