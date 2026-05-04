from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

class Base(DeclarativeBase):
    ...

engine = create_async_engine(settings.DATABASE_URL,
                             connect_args={'statement_cache_size': 0})

Session = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with Session() as session:
        yield session
