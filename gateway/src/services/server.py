import asyncio
import uvicorn
from fastapi import FastAPI
from loguru import logger

from redis import Redis
from valkey import Valkey

from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.routers import *
from src.services.routers.jwt_router import *


class Server:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.app = FastAPI(
            title="Authorizer",
            description="This is test books_store web app.",
            version="0.0.1"
        )
        self.uvicorn_config = uvicorn.Config(
            app=self.app,
            host=EnvTools.load_env_var("AUTHORIZER_HOST"),
            port=int(EnvTools.load_env_var("AUTHORIZER_PORT")),
            reload=True,
            log_level="info"
        )

    
    async def run_server(self):
        server = uvicorn.Server(self.uvicorn_config)
        await self._register_routes()
        
        await server.serve()


    async def _register_routes(self):
        '''
        register all of endpoints.
        '''
        @self.app.get("/")
        def home():
            return {"message": f"Hello! This is {self.config.get("project", "name")} service!"}

        # self.app.include_router(get_user_router(self.data_base))
        # self.app.include_router(get_author_router(self.data_base))
        # self.app.include_router(get_delivery_group_router(self.data_base))
            
