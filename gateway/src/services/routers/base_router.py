from typing import Any, Iterable, List, Optional, Union
from uuid import UUID as PythonUUID

from loguru import logger
import colorama
import httpx

from fastapi import APIRouter, HTTPException, Response, status, Depends, Request

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from urllib.parse import urlparse
from src.services.auth.sessions_manager import SessionsManager

from src.services.db.database import DataBase
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bs_schemas import *
from bs_models import *
from src.core.config import ConfigLoader
from src.core.utils import EnvTools, ValidatingTools
from src.services.jwt.jwt_parser import JwtParser
from src.services.auth.auth_service import AuthService
from src.services.cors.cors import CorsTools


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
            "catalog": f"http://{EnvTools.get_service_ip("catalog")}:{EnvTools.get_service_port("catalog")}",
        }
        self.PUBLIC_ENDPOINTS = {
            ("POST", ("users", "register")),
            ("POST", ("users", "login")),
            ("GET", ("tokens", "access")),
            ("POST", ("tokens", "refresh")),
            ("GET", ("catalog", "product_types_by_categories")),
            ("GET", ("catalog", "categories")),
        }
        self.ALLOWED_ORIGINS = {
            "http://127.0.0.1:5500",
            "http://localhost:5500",
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

    
    def _normalize(self, name: str) -> str:
        return name.lower().strip()


    def filter_request_headers(self, incoming_headers: dict, upstream_host: str, client_ip: Optional[str]) -> dict:
        """
        Removing the hop-by-hop headers specified in the Connection,
        deleting the Host, adding/adding X-Forwarded-For.
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

