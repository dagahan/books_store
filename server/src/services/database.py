from loguru import logger
from sqlalchemy import create_engine

from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class DataBase:
    def __init__(self,) -> None:
        self.config = ConfigLoader()
        self.engine = None
        self.db_host = EnvTools.load_env_var("POSTGRES_HOST")
        self.db_port = EnvTools.load_env_var("POSTGRES_PORT")
        self.db_user = EnvTools.load_env_var("POSTGRES_USER")
        self.db_pwd = EnvTools.load_env_var("POSTGRES_PASSWORD")
        self.db_name = EnvTools.load_env_var("POSTGRES_DB")
        self.engine_config = f"postgresql+psycopg://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"


    def init_alchemy_engine(self,) -> None:
        logger.info(f"Starting service..")
        self.engine = create_engine(self.engine_config)