from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/artist_events"

    # OpenAI
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # Tavily (Web Search)
    tavily_api_key: str = ""

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Search Cache
    search_cache_ttl_hours: int = 24

    # App
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
