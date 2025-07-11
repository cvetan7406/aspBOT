import os
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SECRET_KEY: str
    
    OPENAI_API_KEY: str
    
    AZURE_SPEECH_KEY: str
    AZURE_SPEECH_REGION: str
    AZURE_SPEECH_VOICE_NAME: str = "bg-BG-KalinaNeural"
    
    PORCUPINE_ACCESS_KEY: str
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    VECTOR_STORE_PATH: str = "./data/processed/vector_store"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4-turbo"
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    WAKE_PHRASE: str = "Zdravey ASP"
    DEFAULT_RESPONSE: str = "Моля, опитайте се да формулирате въпроса по-точно, за да мога да помогна."
    
    RETRIEVAL_TOP_K: int = 3
    RELEVANCE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()