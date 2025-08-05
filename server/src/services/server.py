import uvicorn
import asyncio

from loguru import logger
from pydantic import BaseModel

from typing import Any

from src.core.utils import EnvTools
from src.core.config import ConfigLoader
from src.services.db.database import DataBase

from src.services.db.models import *
from src.services.db.shemas import *

from fastapi import (
    FastAPI,
    HTTPException,
    status,
    Response,
)

from sqlalchemy import (
    cast,
    and_,
    select,
    func,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
    joinedload,
    class_mapper,
    noload,
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

    
    async def is_attribute_unique(
            self,
            session: AsyncSession,
            attribute: Any,
            value: Any,
            exclude_id: Optional[UUID | str] = None,
            ) -> bool:
            model = attribute.class_
            if not hasattr(model, '__tablename__'):
                raise ValueError("Attribute must be a SQLAlchemy column property")
            
            query = (
                select(
                    model
                )
                .where(attribute == value)
            )

            
            if exclude_id is not None:
                query = query.where(model.id != exclude_id)

            result = await session.execute(query)
            return len(result.scalars().all()) == 0
    

    def http_ex_attribute_is_not_unique(self, attribute: Any) -> HTTPException:
        return HTTPException(
                            status_code=400,
                            detail=f"User with this {getattr(attribute, "key", str(attribute))} already exists"
                        )


    async def _register_routes(self):
        '''
        register all of endpoints.
        '''
        @self.app.get("/", tags=["users"])
        def home():
            return {"message": f"Hello! This is {self.config.get("project", "name")} service!"}


        @self.app.get("/users", tags=["users"], status_code=status.HTTP_200_OK)
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

                return [UserDTO.model_validate(row, from_attributes=True) for row in row_items]


        @self.app.get("/users/{user_id}", tags=["users"], status_code=status.HTTP_200_OK)
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
                
                return UserDTO.model_validate(user, from_attributes=True)
            

        @self.app.post("/users", tags=["users"], status_code=status.HTTP_200_OK)
        async def create_user(user_data: UserCreateDTO):
            async with self.data_base.async_session() as session:
                if user_data.email:
                    if not await self.is_attribute_unique(session, User.email, user_data.email):
                        raise self.http_ex_attribute_is_not_unique(User.email)
                
                if user_data.phone:
                    if not await self.is_attribute_unique(session, User.phone, user_data.phone):
                        raise self.http_ex_attribute_is_not_unique(User.phone)
                    
                new_user = User(
                    first_name=user_data.first_name.capitalize(),
                    last_name=user_data.last_name.capitalize(),
                    middle_name=user_data.middle_name.capitalize(),
                    email=user_data.email,
                    phone=user_data.phone
                )

                session.add(new_user)
                await session.commit()
                logger.info(f"Created new user with ID: {new_user.id}")
                return {"message": {"UUID": f"{new_user.id}"}}
            
        
        @self.app.patch("/users/{user_id}", tags=["users"], status_code=status.HTTP_200_OK)
        async def update_user(user_id: UUID, update_data: UserUpdateDTO):
            async with self.data_base.async_session() as session:
                result = await session.execute(
                    select(
                        User
                    )
                    .where(User.id == user_id)
                    .options(noload("*"))
                )
                user = result.scalar_one_or_none()

                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                update_dict = update_data.model_dump(exclude_unset=True)
                for key, value in update_dict.items():
                    setattr(user, key, value)

                if 'email' in update_dict and update_dict['email']:
                    print(update_dict['email'])
                    if not await self.is_attribute_unique(session, User.email, update_dict["email"], exclude_id=user_id):
                        raise self.http_ex_attribute_is_not_unique(User.email)
                    
                if 'phone' in update_dict and update_dict['phone']:
                    print(update_dict['phone'])
                    if not await self.is_attribute_unique(session, User.phone, update_dict["phone"], exclude_id=user_id):
                        raise self.http_ex_attribute_is_not_unique(User.phone)
                    
                await session.commit()
                
                logger.info(f"Updated user with ID: {user_id}")
                return Response(status_code=status.HTTP_200_OK)
                

        @self.app.delete("/users/{user_id}", tags=["users"], status_code=status.HTTP_200_OK)
        async def delete_user(user_id: UUID):
            async with self.data_base.async_session() as session:
                result = await session.execute(
                    select(
                        User
                    )
                    .where(User.id == user_id)
                )
                user = result.scalar_one_or_none()

                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                
                await session.delete(user)
                await session.commit()

                logger.info(f"Deleted user with ID: {user_id}")
                return Response(status_code=status.HTTP_200_OK)
            