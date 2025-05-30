from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)

# Сессии
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовая модель
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)