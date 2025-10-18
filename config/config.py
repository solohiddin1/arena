from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()



class Settings(BaseSettings):
    PHOTO_PATH: str
    DEFAULT_PHOTO_PATH: str

    class Config:
        env_file = ".env"
    

settings = Settings()