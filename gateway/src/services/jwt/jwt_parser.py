import colorama
from loguru import logger
import jwt
import bcrypt
from typing import Any

from src.core.utils import EnvTools
from src.core.config import ConfigLoader
from typing import Any, Optional, Dict
from datetime import datetime, timedelta, timezone

import uuid
import logging
from fastapi import FastAPI, Request, HTTPException, Depends, status
from cryptography.hazmat.primitives import serialization
from jose import JWTError, jwt
from pydantic import BaseModel
from valkey import Valkey


class JwtParser:
    def __init__(self):
        self.config = ConfigLoader()
        self.private_key = self._read_key("private_key")
        self.public_key = self._read_key("public_key")
        self.access_token_expire_minutes = EnvTools.load_env_var("ACCESS_TOKEN_EXPIRE_MINUTES")
        self.refresh_token_expire_days = EnvTools.load_env_var("REFRESH_TOKEN_EXPIRE_DAYS")
        self.algorithm = "RS256"


    def _read_key(self, key_type: str) -> str:
        path = self.config.get("jwt", key_type)
        try:
            match key_type:
                case "private_key":
                    with open(path, "r") as key_file:
                        return serialization.load_pem_private_key(key_file.read(), password=None)
                case "public_key":
                    with open(path, "r") as key_file:
                        return serialization.load_pem_public_key(key_file.read())
            
        except Exception as ex:
            logger.critical(f"Error during reading process of {key_type}: {ex}")
            raise Exception


    def validate_token(self, token: str):
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        
        except JWTError as ex:
            logging.error(f"JWT validation error: {ex}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        

    def generate_refresh_token(self, user_id: int, session_id: str):
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        jwt_payload = {
            "sub": user_id,
            "sid": session_id,
            "exp": expires_at,
            "refresh": True
        }

        return jwt.encode(jwt_payload, self.private_key, algorithm=self.algorithm)
        
    
    def generate_acess_token(self, user_id: int, session_id: str):
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        jwt_payload = {
            "sub": user_id,
            "sid": session_id,
            "exp": expires_at
        }

        return jwt.encode(jwt_payload, self.private_key, algorithm=self.algorithm)
        
 

