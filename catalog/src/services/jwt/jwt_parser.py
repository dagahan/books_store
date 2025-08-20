from datetime import UTC, datetime, timedelta
from typing import Any

from bs_schemas import AccessPayload, RefreshPayload
from fastapi import HTTPException, status
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from loguru import logger

from src.core.config import ConfigLoader
from src.core.utils import EnvTools, StringTools, TimeTools
from src.services.auth.sessions_manager import SessionsManager


class JwtParser:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.sessions_manager = SessionsManager()
        self.private_key = None
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


    def validate_token(self, token: str) -> AccessPayload | RefreshPayload:
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        
        except JWTError as ex:
            logger.error(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


    def decode_token(self, token: str) -> dict[str, Any]:
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


    def generate_refresh_token(
        self,
        user_id: str,
        session_id: str,
        refresh_token: str = None,
        make_old_refresh_token_used: bool = True
    ) -> str:
        expires_at = int((
            datetime.now(UTC)
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

        if make_old_refresh_token_used:
            self.make_refresh_token_invalid(refresh_token)

        return jwt.encode(jwt_payload.model_dump(), self.private_key, algorithm=self.algorithm)


    def make_refresh_token_invalid(self, refresh_token: str) -> None:
        """
        Marks refresh as used (one-time).
        Creates the Invalid_refresh key:{hash_session_id}:{refresh_hash} from TTL to exp.
        """
        try:
            claims: dict[str, Any] = jwt.get_unverified_claims(refresh_token)  # type: ignore[attr-defined]
            exp_time_stamp = int(claims.get("exp")) if claims and "exp" in claims else None
        except Exception:
            exp_time_stamp = None

        ttl: int = max(1, (exp_time_stamp - TimeTools.now_time_stamp())) if exp_time_stamp is not None else 1

        key: str = f"Invalid_refresh:{refresh_token}"
        self.sessions_manager.valkey_service.valkey.set(key, "1", ex=ttl)


    def is_refresh_token_in_invalid_list(self, refresh_token: str) -> bool:
        key: str = f"Invalid_refresh:{refresh_token}"
        return self.sessions_manager.valkey_service.valkey.exists(key) == 1
        
    
    def generate_access_token(
        self,
        user_id: str,
        session_id: str,
        refresh_token: str,
        make_old_refresh_token_used: bool = True
    ) -> str:
        if refresh_token is not None and self.is_refresh_token_in_invalid_list(refresh_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token already used")

        expires_at = int((datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)).timestamp())
        jwt_payload = AccessPayload(
            sub=user_id,
            sid=session_id,
            exp=expires_at,
        )

        if make_old_refresh_token_used:
            self.make_refresh_token_invalid(refresh_token)

        return jwt.encode(jwt_payload.model_dump(), self.private_key, algorithm=self.algorithm)
        
 

