from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/zcw_blog"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/zcw_blog"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # CORS
    cors_origins: str = '["http://localhost:3000"]'

    # LLM
    llm_api_key: str = ""
    llm_api_base: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-3.5-turbo"

    # Embedding
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dim: int = 512

    # Logging
    log_level: str = "DEBUG"

    # Rate limit
    rate_limit_per_minute: int = 60

    @property
    def cors_origin_list(self) -> List[str]:
        import json

        return json.loads(self.cors_origins)


settings = Settings()
