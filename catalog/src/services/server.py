import uvicorn
from fastapi import FastAPI
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.db.database import DataBase
from src.services.routers.catalog.catalog_router import *


class Server:
    def __init__(self) -> None:
        self.data_base = DataBase()
        self.config = ConfigLoader()
        self.app = FastAPI(
            title="Authorizer",
            description="This is test books_store web app.",
            version="0.0.1"
        )
        self.uvicorn_config = uvicorn.Config(
            app=self.app,
            host=EnvTools.get_service_ip(self.config.get("project", "name")),
            port=int(EnvTools.get_service_port(self.config.get("project", "name"))),
            reload=True,
            log_level="info"
        )

    
    async def run_server(self) -> None:
        server = uvicorn.Server(self.uvicorn_config)
        await self.data_base.init_alchemy_engine()
        await self._register_routes()

        logger.info(self.data_base.engine)
        
        await server.serve()


    async def _register_routes(self) -> None:
        '''
        register all of endpoints.
        '''
        self.app.include_router(get_catalog_router(self.data_base))
            
