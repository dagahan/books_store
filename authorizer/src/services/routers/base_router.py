from typing import Any, Iterable, List, Optional, Union, Dict
from uuid import UUID as PythonUUID

from loguru import logger
import colorama

from fastapi import APIRouter, HTTPException, Response, status, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.utils import ValidatingTools
from src.core.config import ConfigLoader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.db.database import DataBase
from src.services.jwt.jwt_parser import JwtParser
from bs_schemas import *
from bs_models import *
from src.services.auth.sessions_manager import *
from src.services.auth.auth_service import *
from src.services.jwt import *


class BaseRouter:
    def __init__(self, db: DataBase):
        self.db = db


    async def find_user_by_any_credential(self, session: AsyncSession, user_data: Any) -> User:
        if user_data.user_name:
            query = select(
                User
            ).where(User.user_name == user_data.user_name)

        elif user_data.email:
            query = select(
                User
            ).where(User.email == user_data.email)

        elif user_data.phone:
            query = select(
                User
            ).where(User.phone == user_data.phone)

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Login (user_name, email or phone) is required")

        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        dto = ValidatingTools.validate_models_by_schema(user, UserDTO)
        if dto is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="User record failed schema validation")

        return user


    async def is_attribute_unique(
        self,
        session: AsyncSession,
        attribute: Any,
        value: Any,
        exclude_id: Optional[PythonUUID | str] = None,
    ) -> bool:
        model = attribute.class_
        if not hasattr(model, '__tablename__'):
            raise ValueError("Attribute must be a SQLAlchemy column property")
        
        query = (
            select
            (
                model
            )
            .where(attribute == value)
        )
        
        if exclude_id is not None:
            query = query.where(model.id != exclude_id)
        
        result = await session.execute(query)
        return len(result.scalars().all()) == 0
    

    def http_ex_attribute_is_not_unique(self, attribute: Any, entity_name: str = "Entity") -> HTTPException:
        return HTTPException(
            status_code=400,
            detail=f"{entity_name} with this {getattr(attribute, 'key', str(attribute))} already exists"
        )

