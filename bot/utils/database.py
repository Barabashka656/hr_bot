from typing import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker, 
    create_async_engine
)

from bot.data.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
