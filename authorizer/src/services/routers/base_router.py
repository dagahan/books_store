from typing import Any, Iterable, List, Optional, Union, Dict, Tuple
from uuid import UUID as PythonUUID
import uuid

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
from src.services.auth.auth_service import AuthService
from bs_schemas import *
from bs_models import *
from src.services.auth.sessions_manager import *
from src.services.auth.auth_service import *
from src.services.jwt import *


class BaseRouter:
    def __init__(self, db: DataBase):
        self.db = db
        self.jwt_parser = JwtParser()


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


    async def get_payload_or_401(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        if credentials is None or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing.")
        return self.jwt_parser.decode_token(credentials.credentials)


    async def require_admin(self,
        credentials: HTTPAuthorizationCredentials,
        session: AsyncSession,
    ) -> Tuple[uuid.UUID, Optional[str]]:
        payload: Dict[str, Any] = await self.get_payload_or_401(credentials)
        sub: Optional[str] = payload.get("sub")
        sid: Optional[str] = payload.get("sid")
        if not sub:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token missing subject (sub).")

        async with self.db.session_ctx() as session:
            result = await session.execute(
                            select(User)
                            .where(User.id == sub)
                            .options(noload("*"))
                        )
            admin_id: User = result.scalar_one_or_none()
            if not admin_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin not found"
                )

            if admin_id.role == UserRole.user or admin_id.role == UserRole.moderator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )

        try:
            return uuid.UUID(sub), sid
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid admin UUID in token.")



