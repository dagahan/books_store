from typing import TYPE_CHECKING

from ..base_router import *

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def get_catalog_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/catalog", tags=["catalog"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    bearer_scheme = HTTPBearer()
    auth_service = AuthService(db)
    s3_service = S3Client()
    media_processor = MediaProcessor()


    
    @router.get("/categories", response_model=CategoriesResponse)
    async def list_product_types(
        data: CategoriesRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: "AsyncSession" = Depends(db.get_session),
    ) -> CategoriesResponse:
        payload: Dict[str, Any] = await base_router.get_payload_or_401(credentials)

        query = select(
                ProductType
            )

        if data.categories:
            query = query.where(ProductType.category.in_(data.categories))

        result = await session.execute(query.order_by(ProductType.name))
        product_types = result.scalars().all()

        return CategoriesResponse(
            product_types=ValidatingTools.validate_models_by_schema(product_types, ProductTypeDTO)
        )



    return router

