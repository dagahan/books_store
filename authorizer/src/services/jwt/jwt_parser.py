from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union

from bs_schemas import AccessPayload, RefreshPayload
from fastapi import HTTPException, status
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import EnvTools, StringTools
from src.services.auth.sessions_manager import SessionsManager


class JwtParser:
    def __init__(self):
        self.config = ConfigLoader()
        self.sessions_manager = SessionsManager()
        self.private_key = self._read_key("private_key")
        self.public_key = EnvTools.load_env_var("public_key")
        self.access_token_expire_minutes = int(EnvTools.load_env_var("ACCESS_TOKEN_EXPIRE_MINUTES"))
        self.refresh_token_expire_days = int(EnvTools.load_env_var("REFRESH_TOKEN_EXPIRE_DAYS"))
        self.algorithm = "RS256"


    def _read_key(self, key_type: str) -> str:
        path = self.config.get("jwt", key_type)
        try:
            match key_type:
                case "private_key":
                    with open(path, "rb") as key_file:
                        return key_file.read()
                case "public_key":
                    with open(path, "rb") as key_file:
                        return key_file.read()
            
        except Exception as ex:
            logger.critical(f"Error during reading process of {key_type}: {ex}")
            raise Exception


    def validate_token(self, token: str) -> Union[AccessPayload, RefreshPayload]:
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        
        except JWTError as ex:
            logger.error(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Universal token decoding (for access and refresh).
        Returns payload (dict) on success, throws HttpException (401) on error.
        """
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload  # dict

        except ExpiredSignatureError as ex:
            logger.debug(f"Token expired: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

        except JWTError as ex:
            logger.debug(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        except Exception as ex:
            logger.exception(f"Unexpected error while decoding token: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


    def generate_refresh_token(self, user_id: str, session_id: str):
        expires_at = int((
            datetime.now(timezone.utc)
            + timedelta(days=self.refresh_token_expire_days)
        ).timestamp())

        test_dsh: dict = self.sessions_manager.get_test_dsh()
        dsh: str = StringTools.hash_string(
            f"{test_dsh.get("user_agent")}{test_dsh.get("client_id")}{test_dsh.get("local_system_time_zone")}{test_dsh.get("platform")}"
        )

        jwt_payload = RefreshPayload(
            sub=user_id,
            sid=session_id,
            exp=expires_at,
            dsh=dsh,
            ish=StringTools.hash_string(self.sessions_manager.get_test_client_ip()),
        )

        return jwt.encode(jwt_payload.model_dump(), self.private_key, algorithm=self.algorithm)
        
    
    def generate_access_token(self, user_id: str, session_id: str):
        expires_at = int((datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)).timestamp())
        jwt_payload = AccessPayload(
            sub=user_id,
            sid=session_id,
            exp=expires_at,
        )

        return jwt.encode(jwt_payload.model_dump(), self.private_key, algorithm=self.algorithm)
        
 

