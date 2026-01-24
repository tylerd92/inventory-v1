from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str | None = None

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()
