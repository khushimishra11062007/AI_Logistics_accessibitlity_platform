from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Smart Logistics"
    DATABASE_URL: PostgresDsn

    AWS_REGION: str = "us-east-1"
    AWS_SQS_QUEUE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()