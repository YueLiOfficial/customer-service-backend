import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from app.conf.config import settings

engine: AsyncEngine | None = None
session_factory: async_sessionmaker | None = None

def init_db_engine():
    global engine, session_factory

    engine = create_async_engine(
        url=settings.database_url,
        echo=False,
        pool_pre_ping=True
    )

    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )

async def close_db_engine():
    if engine:
        await engine.dispose()

if __name__ == "__main__":
    async def main():
        init_db_engine()

        assert session_factory
        async with session_factory() as session:
            session: AsyncSession

            res = await session.execute(text("SELECT 1"))

            print(res.fetchone())

        await close_db_engine()

    asyncio.run(main())
