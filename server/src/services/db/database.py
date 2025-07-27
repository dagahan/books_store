from loguru import logger
from sqlalchemy import (
    engine,
    text,
    inspect,
    insert,
)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

import colorama

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.db.models import Base


class DataBase:
    def __init__(self,) -> None:
        self.config = ConfigLoader()
        self.engine = None
        self.db_host = EnvTools.load_env_var("POSTGRES_HOST")
        self.db_port = EnvTools.load_env_var("POSTGRES_PORT")
        self.db_user = EnvTools.load_env_var("POSTGRES_USER")
        self.db_pwd = EnvTools.load_env_var("POSTGRES_PASSWORD")
        self.db_name = EnvTools.load_env_var("POSTGRES_DB")
        self.engine_config = f"postgresql+asyncpg://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"



    async def init_alchemy_engine(self,) -> None:
        logger.info(f"Starting service..")
        self.engine = create_async_engine(
            url=self.engine_config,
            echo=self.config.get("db", "echo"),
            poolclass=NullPool,  # Отключаем пул соединений для asyncpg
            future=True,  # Используем новый стиль SQLAlchemy 2.0
            connect_args={
                "timeout": 10,  # Таймаут подключения (секунды)
                "command_timeout": 30,  # Таймаут выполнения запросов
                "server_settings": {
                    "application_name": "myapp_ctl"
                }
            }
        )

        if await self.test_connection(self.engine):
            logger.info(f"{colorama.Fore.GREEN}Connection with data base has been established!")
        else:
            raise Exception(f"{colorama.Fore.RED}Cannot establish connection with data base.")
        

    async def test_connection(self, engine: engine,) -> bool: 
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    
    async def create_tables(self,) -> None:
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
        async with self.engine.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()
        logger.success("All tables created successfully")


    async def drop_all_tables(self,) -> None:
        async with self.engine.connect() as conn:
            result = await conn.execute(text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            
            for table in tables:
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            await conn.execute(text(
                "DROP TYPE IF EXISTS payment_method_enum, deliveries_status_enum, delivery_groups_status_enum CASCADE"))
            await conn.commit()