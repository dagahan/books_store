import uuid
from loguru import logger
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from valkey import Valkey
from jose import JWTError, jwt

from src.services.jwt import JwtParser
from src.services.db.database import DataBase
from src.services.db.models import User, UserRole
from src.services.auth.sessions_manager import SessionsManager
from src.core.utils import EnvTools

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload


class AuthService:
    def __init__(self, db: DataBase):
        self.db = db
        self.jwt_parser = JwtParser()
        self.sessions_manager = SessionsManager()
        self.access_token_expire_minutes = self.jwt_parser.access_token_expire_minutes
        self.refresh_token_expire_days = self.jwt_parser.refresh_token_expire_days


    async def authenticate_user(self, identifier: str, password: str) -> User:
        async with self.db.get_session() as session:
            result = await session.execute(
                select(User)
                .where(
                    (User.email == identifier) | (User.phone == identifier)
                )
            )
            user = result.scalars().first()
            
            if not user or not User.verify_password(password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account deactivated"
                )
                
            return user


    async def logout(self, session_id: str):
        self.sessions_manager.delete_session(session_id)
        return {"message": "Session terminated"}


    async def get_access_token_by_refresh_token(self, refresh_token: str) -> dict:
        try:
            payload = self.jwt_parser.validate_token(refresh_token)
            
            if not payload.get("refresh"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
                
            session_id = payload.get("sid")
            user_id = payload.get("sub")
            
            if not session_id or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
                
            if not self.sessions_manager.session_exists(session_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session expired"
                )
                
            self.sessions_manager.refresh_session(session_id)
            
            access_token = self.jwt_parser.generate_access_token(
                user_id=user_id, 
                session_id=session_id
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except JWTError as e:
            logger.error(f"Refresh token error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )


    async def set_is_active_user(self, user_id: uuid.UUID, admin_id: uuid.UUID, option: bool):
        async with self.db.get_session() as session:
            try:
                result = await session.execute(
                                select(User)
                                .where(User.id == admin_id)
                                .options(noload("*"))
                            )
                admin_id = result.scalar_one_or_none()
                if not admin_id:
                    return HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Admin not found"
                    )

                if admin_id.role != UserRole.admin:
                    return HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin privileges required"
                    )
                    
                result = await session.execute(
                                select(User)
                                .where(User.id == user_id)
                                .options(noload("*"))
                            )
                user = result.scalar_one_or_none()
                
                if not user:
                    return HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )

                if not option:                    
                    self.sessions_manager.delete_session(user.id)
                setattr(user, User.is_active, option)
                    
                await session.commit()
                
                return {"message": f"User with UUID: {user_id} banned"}
            
            except Exception as ex:
                logger.error(f"Couldn't ban user during the exception: {ex}")
                return HTTPException(status_code=500, detail="Couldn't ban user during the server error.")
        


    async def ban_user(self, user_id: uuid.UUID, admin_id: uuid.UUID):
        '''
        just synonim to set set_is_active_user(False).
        '''
        await self.set_is_active_user(user_id, admin_id, False)


    async def unban_user(self, user_id: uuid.UUID, admin_id: uuid.UUID):
        '''
        just synonim to set set_is_active_user(True).
        '''
        await self.set_is_active_user(user_id, admin_id, True)

