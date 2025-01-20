from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AOAI_API_BASE: str
    AOAI_API_KEY: str
    AOAI_API_VERSION: str
    AOAI_GPT4O_MINI_MODEL: str
    TTS_MODEL_NAME: str
    WHISPER_MODEL_NAME: str
    BING_SEARCH_API_ENDPOINT: str
    BING_SEARCH_API_KEY: str
    COSMOS_ENDPOINT: str
    COSMOSDB_KEY: str
    COSMOS_DATABASE: str

    class Config:
        env_file = ".env"

settings = Settings()