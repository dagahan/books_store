import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.core.utils import EnvTools
from src.core.config import ConfigLoader
from src.services.db.database import DataBase

from src.services.db.models import *
from src.services.db.shemas import *

from sqlalchemy import (
    cast,
    and_,
    select,
    func,
)

from sqlalchemy.orm import (
    selectinload,
    joinedload,
)


class Server:
    def __init__(self) -> None:
        self.data_base = DataBase()
        self.config = ConfigLoader()
        self.app = FastAPI(
            title="Books_Store",
            description="This is test books_store web app.",
            version="0.0.1"
        )
        self.uvicorn_config = uvicorn.Config(
            app=self.app,
            host=EnvTools.load_env_var("SERVER_HOST"),
            port=int(EnvTools.load_env_var("SERVER_PORT")),
            reload=True,
            log_level="info"
        )
        asyncio.run(self._register_routes())

    
    async def run_server(self):
        server = uvicorn.Server(self.uvicorn_config)
        await self.data_base.init_alchemy_engine()
        # await self.data_base.drop_all_tables() # dropping all of tables and data.
        # await self.data_base.create_tables()

        logger.info(self.data_base.engine)

        await server.serve()


    async def _register_routes(self):
        '''
        register all of endpoints.
        '''
        @self.app.get("/", tags=["users"])
        def home():
            return {"message": f"Hello! This is {self.config.get("project", "name")} service!"}


        @self.app.get("/users", tags=["users"])
        async def get_all_users() -> List[UserDTO]:
            '''
            returns all of users with their data.
            '''
            async with self.data_base.async_session() as session:
                query = (
                    select (
                        User
                    )
                )
                    
                result = await session.execute(query)
                row_items = result.scalars().all()

                if not row_items:
                    raise HTTPException(status_code=404, detail=f"There is no users")

                items_dto = [UserDTO.model_validate(row, from_attributes=True) for row in row_items]
                return items_dto


        @self.app.get("/users/{user_id}", tags=["users"])
        async def get_user_by_id(user_id: UUID) -> UserDTO:
            async with self.data_base.async_session() as session:
                query = (
                    select (
                        User
                    )
                    .where(User.id == user_id)
                )

                result = await session.execute(query)
                user = result.scalars().first()

                if not user:
                    logger.warning(f"User with ID {user_id} not found.")
                    raise HTTPException(status_code=404, detail=f"User not found")
                
                user_dto = UserDTO.model_validate(user, from_attributes=True)
                return user_dto