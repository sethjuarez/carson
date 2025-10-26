from ..models.settings import Settings

# Global settings instance
_settings = Settings()


def get_settings() -> Settings:
    """Get the application settings."""
    return _settings


__all__ = [
    "get_settings",
]
