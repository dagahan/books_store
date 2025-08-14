from typing import Any, Iterable, List, Optional, Union
from uuid import UUID as PythonUUID

from loguru import logger
from pydantic import ValidationError
import colorama
import httpx

from fastapi import APIRouter, HTTPException, Response, status, Depends, Request

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from urllib.parse import urlparse
from src.services.auth.sessions_manager import SessionsManager

from src.services.db.database import DataBase
from bs_schemas import *
from bs_models import *
from src.core.config import ConfigLoader
from src.core.utils import EnvTools
from src.services.jwt.jwt_parser import JwtParser
from src.services.auth.auth_service import AuthService


class BaseRouter:
    def __init__(self, db: DataBase):
        self.db = db
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=30.0))
        self.HOP_BY_HOP = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        }
        # lately this might work with service_map from k8s.
        self.SERVICE_MAP = {
            "users":  f"http://{EnvTools.get_service_ip("authorizer")}:{EnvTools.get_service_port("authorizer")}",
            "tokens": f"http://{EnvTools.get_service_ip("authorizer")}:{EnvTools.get_service_port("authorizer")}",
        }
        self.PUBLIC_ENDPOINTS = {
            ("POST", ("users", "register")),
            ("POST", ("users", "login")),
            ("GET", ("tokens", "access")),
            ("POST", ("tokens", "refresh")),
        }


    def path_segments(self, path: str) -> List[str]:
        return [seg for seg in path.strip("/").split("/") if seg]


    def is_public_endpoint(self, method: str, full_path: str) -> bool:
        segs = self.path_segments(full_path)
        if not segs:
            return False
        for m, tail in self.PUBLIC_ENDPOINTS:
            if m is not None and m.upper() != method.upper():
                continue
            if len(segs) >= len(tail) and segs[-len(tail):] == list(tail):
                return True
        return False


    def map_path_to_service_address(self, path: str) -> Optional[dict]:
        path = path.lstrip("/")
        prefix = path.split("/", 1)[0] if path else ""
        return self.SERVICE_MAP.get(prefix)

    
    def get_bearer_token(self, request: Request) -> Optional[str]:
        auth = request.headers.get("authorization")
        if not auth:
            return None
        scheme, _, token = auth.partition(" ")
        return token if scheme.lower() == "bearer" else None


    def _normalize(self, name: str) -> str:
        return name.lower().strip()


    def filter_request_headers(self, incoming_headers: dict, upstream_host: str, client_ip: Optional[str]) -> dict:
        """
        Удаляем hop-by-hop, заголовки, указанные в Connection,
        удаляем Host, добавляем/дописываем X-Forwarded-For.
        """
        headers = dict(incoming_headers)

        conn_val = None
        for k in list(headers.keys()):
            if self._normalize(k) == "connection":
                conn_val = headers.pop(k, None)
                break

        conn_tokens = set()
        if conn_val:
            for tok in conn_val.split(","):
                tok = tok.strip().lower()
                if tok:
                    conn_tokens.add(tok)

        for key in list(headers.keys()):
            n = self._normalize(key)
            if n in self.HOP_BY_HOP or n in conn_tokens:
                headers.pop(key, None)

        headers.pop("host", None)
        headers.pop("Host", None)

        if client_ip:
            existing_xff = incoming_headers.get("x-forwarded-for") or incoming_headers.get("X-Forwarded-For")
            headers["X-Forwarded-For"] = f"{existing_xff}, {client_ip}" if existing_xff else client_ip

        return headers


    def filter_response_headers(self, incoming_headers: dict) -> dict:
        return {k: v for k, v in incoming_headers.items() if self._normalize(k) not in self.HOP_BY_HOP}


    def validate_models_by_schema(self, models: Any, schema: Any) -> Any:
        if not isinstance(models, Iterable):
            models = [models]

        valid_models = []
        for model in models:
            try:
                dto = schema.model_validate(model, from_attributes=True)
                valid_models.append(dto)
                
            except ValidationError as ex:
                model_id = getattr(model, "id", None)
                logger.warning(f"{colorama.Fore.YELLOW}Skipping invalid instance of {schema.__name__} (id={model_id}): {ex.errors()}")

        if len(valid_models) == 1:
            return valid_models[0]
        return valid_models
