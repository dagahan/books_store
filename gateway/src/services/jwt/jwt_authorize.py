import uuid
import logging
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from redis import Redis
from valkey import Valkey


class JWTBearer(HTTPBearer):
    def __init__(self, ):
        pass


    def call(self, request: Request) -> TokenPayload:
      
        payload = validate_token(credentials.credentials)
        
        session_key = f"session:{payload.sid}"
        session_data = valkey.hgetall(session_key)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session expired"
            )
        
        if session_data.get("status") == "banned":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account suspended"
            )
        
        return payload