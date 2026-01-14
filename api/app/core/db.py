from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

#CREATE ASYNC ENGINE AND SESSION
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with SessionLocal() as session:
        yield session



#CREATE SYNC ENGINE AND SESSION
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=settings.DEBUG,

)


SessionSync = sessionmaker(bind=sync_engine)
