import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

from src.core.utils import EnvTools
from src.services.db.database import DataBase


class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True


class Server:
    def __init__(self) -> None:
        self.data_base = DataBase()
        self.app = FastAPI(
            title="Simple Web Service",
            description="Пример веб-приложения на FastAPI",
            version="1.0.0"
        )
        self.fake_db = {
            1: User(id=1, name="Ivan Petrov", email="ivan@example.com"),
            2: User(id=2, name="Maria Ivanova", email="maria@example.com")
        }
        self.uvicorn_config = uvicorn.Config(
            app=self.app,
            host=EnvTools.load_env_var("SERVER_HOST"),
            port=int(EnvTools.load_env_var("SERVER_PORT")),
            reload=True,
            log_level="info"
        )
        self._register_routes()

    
    async def run_server(self):
        server = uvicorn.Server(self.uvicorn_config)
        self.data_base.init_alchemy_engine()
        # self.data_base.drop_all_tables() # dropping all of tables and data.
        self.data_base.create_tables()

        logger.info(self.data_base.engine)

        await server.serve()


    def _register_routes(self):
        '''
        register all of endpoints.
        '''
        @self.app.get("/", tags=["Главная"])
        def home():
            return {"message": "Добро пожаловать в наш сервис!"}


        @self.app.get("/users", tags=["Пользователи"])
        def get_all_users():
            return list(self.fake_db.values())


        @self.app.get("/users/{user_id}", tags=["Пользователи"])
        def get_user(user_id: int):
            if user_id not in self.fake_db:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            return self.fake_db[user_id]


        @self.app.post("/users", tags=["Пользователи"], status_code=201)
        def create_user(user: User):
            if user.id in self.fake_db:
                raise HTTPException(status_code=400, detail="Пользователь с таким ID уже существует")
            
            self.fake_db[user.id] = user
            return {"message": "Пользователь создан", "data": user}


        @self.app.delete("/users/{user_id}", tags=["Пользователи"])
        def delete_user(user_id: int):
            if user_id not in self.fake_db:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            del self.fake_db[user_id]
            return {"message": "Пользователь удален"}


        @self.app.get("/health", tags=["Система"])
        def health_check():
            return {"status": "ok"}