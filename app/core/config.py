from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./inventory.db"  # Default SQLite database
    openai_api_key: str | None = None

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

# Create settings instance lazily to allow for test environment overrides
_settings = None

def get_settings():
    """Get settings instance, allowing for runtime environment variable changes."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Lazy property for backward compatibility
class SettingsProxy:
    def __getattr__(self, name):
        return getattr(get_settings(), name)

settings = SettingsProxy()
