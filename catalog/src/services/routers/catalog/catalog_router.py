from __future__ import annotations
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from src.core.utils import ValidatingTools
from src.services.routers.base_router import BaseRouter
from src.services.jwt.jwt_parser import JwtParser
from src.services.auth.sessions_manager import SessionsManager
from src.services.auth.auth_service import AuthService
from src.services.media_process.media_processor import MediaProcessor
from src.services.s3.s3 import S3Client

from bs_models import ProductType  # type: ignore[import-untyped]
from bs_schemas import (  # type: ignore[import-untyped]
    ProductTypesByCategoriesRequest,
    ProductTypesByCategoriesResponse,
    CategoriesResponse,
    ProductTypeDTO,
    ProductTypeCategory,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.services.db.database import DataBase


def get_catalog_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/catalog", tags=["catalog"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    bearer_scheme = HTTPBearer()
    auth_service = AuthService(db)
    s3_service = S3Client()
    media_processor = MediaProcessor()

    
    @router.get("/product_types_by_categories", response_model=ProductTypesByCategoriesResponse)
    async def product_types_by_categories(
        data: ProductTypesByCategoriesRequest,
        # credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> CategoriesResponse:
        # payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)

        query = select(
                ProductType
            )

        if data.categories:
            query = query.where(ProductType.category.in_(data.categories))

        result = await session.execute(query.order_by(ProductType.name))
        product_types = result.scalars().all()

        return ProductTypesByCategoriesResponse(
            product_types=ValidatingTools.validate_models_by_schema(product_types, ProductTypeDTO)
        )


    @router.get("/categories", response_model=CategoriesResponse)
    async def categories(
        # credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> CategoriesResponse:
        # payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)
        return CategoriesResponse(
            categories=list(ProductTypeCategory)
        ) 



    return router

