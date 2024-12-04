from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 300
    LOG_DIR: str = "logs"
    
    # Weaviate settings
    WEAVIATE_URL: str = "http://localhost:8080"
    COLLECTION_NAME: str = "SupportDocs"
    MAX_CONTEXT_DOCS: int = 3

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings() 