import colorama
from loguru import logger

from src.core.utils import EnvTools
from src.core.config import ConfigLoader
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta, timezone

import uuid
from fastapi import FastAPI, Request, HTTPException, Depends, status
from jose import JWTError, jwt
from pydantic import BaseModel
from valkey import Valkey
from bs_schemas import AccessPayload, RefreshPayload
from jose.exceptions import ExpiredSignatureError


class JwtParser:
    def __init__(self):
        self.config = ConfigLoader()
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


    def validate_token(self, token: str) -> Union[AccessPayload, RefreshPayload]:
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        
        except JWTError as ex:
            logger.error(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

