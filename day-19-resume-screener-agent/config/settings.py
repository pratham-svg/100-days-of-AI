from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "openai/gpt-4o"

    QDRANT_URL: str           # your Qdrant cloud URL
    QDRANT_API_KEY: str       # your Qdrant cloud API key
    QDRANT_COLLECTION: str = "resumes"

    EMBEDDING_MODEL: str = "text-embedding-ada-002"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
