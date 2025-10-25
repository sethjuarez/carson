from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_prefix="APP_")

    storage_connection: str = Field(
        default="", description="Azure Storage connection string"
    )
    storage_container: str = Field(
        default="", description="Azure Storage container name"
    )
    database_connection: str = Field(
        default="", description="Database connection string"
    )
    client_id: str = Field(default="LOCAL", description="Client ID")


if __name__ == "__main__":
    settings = Settings()
    print(settings.model_dump())
