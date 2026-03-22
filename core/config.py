from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    app_name: str = "To-Do API"
    debug: bool = True
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./todo.db"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value


settings = Settings()
