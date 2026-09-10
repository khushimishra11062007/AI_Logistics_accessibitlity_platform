import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

load_dotenv()


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return database_url


database_url = get_database_url()
sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
async_database_url = (
    database_url
    if "+asyncpg" in database_url
    else database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
)
engine = create_engine(sync_database_url, pool_pre_ping=True)
async_engine = create_async_engine(async_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def init_db() -> None:
    # Import model modules so their metadata is registered before table creation.
    import app.models  # noqa: F401

    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
