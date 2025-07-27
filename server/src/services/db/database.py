from loguru import logger
from sqlalchemy import (
    create_engine,
    engine,
    text,
    inspect,
    insert,
)

import colorama

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.db.models import DataBaseTables


class DataBase:
    def __init__(self,) -> None:
        self.config = ConfigLoader()
        self.metadata_object = DataBaseTables().metadata_object
        self.engine = None
        self.db_host = EnvTools.load_env_var("POSTGRES_HOST")
        self.db_port = EnvTools.load_env_var("POSTGRES_PORT")
        self.db_user = EnvTools.load_env_var("POSTGRES_USER")
        self.db_pwd = EnvTools.load_env_var("POSTGRES_PASSWORD")
        self.db_name = EnvTools.load_env_var("POSTGRES_DB")
        self.engine_config = f"postgresql+psycopg://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"



    def init_alchemy_engine(self,) -> None:
        logger.info(f"Starting service..")
        self.engine = create_engine(
            url=self.engine_config,
            echo=self.config.get("db", "echo"),
            pool_size=self.config.get("db", "pool_size"),
            max_overflow=self.config.get("db", "max_overflow"),
        )

        if self.test_connection(self.engine):
            logger.info(f"{colorama.Fore.GREEN}Connection with data base has been established!")
        else:
            raise Exception(f"{colorama.Fore.RED}Cannot establish connection with data base.")
        

    def test_connection(self, engine: engine,) -> bool: 
        with engine.connect() as conn:
            # we are picking collumn and row with indexies 0.
            result = conn.execute(text("SELECT VERSION()")).all()[0][0]
            logger.debug(result)
            return result.startswith("PostgreSQL")

    
    def create_tables(self,) -> None:
        self.metadata_object.create_all(self.engine)


    def drop_all_tables(self,) -> None:
        if self.engine.dialect.name == 'postgresql':
            with self.engine.begin() as conn:
                tables = inspect(conn).get_table_names() # Get all table names in dependency order
                for table in reversed(tables):
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
        else:
            self.metadata_object.drop_all(self.engine)