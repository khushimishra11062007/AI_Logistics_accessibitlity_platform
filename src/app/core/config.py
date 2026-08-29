from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Smart Logistics"
    DATABASE_URL: PostgresDsn
    AWS_REGION: str = "us-east-1"
    AWS_SQS_QUEUE_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
