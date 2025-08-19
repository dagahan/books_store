from ..base_router import *


def get_token_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/tokens", tags=["tokens"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    auth_service = AuthService(db)

    
    @router.get("/access", status_code=200, response_model=ResponseAccess)
    async def access(data: RequestAccess,
        session = Depends(db.get_session)
    ) -> ResponseAccess:
        try:
            logger.debug(f"Test msg from user with access token: {data.access_token}")

        except Exception as ex:
            logger.error(f"Couldn't add an object. {ex}")
            return HTTPException(status_code=500, detail="Cannot test an access token because of internal error..")

        return ResponseAccess(
            valid = await auth_service.validate_access_token(data.access_token)
        )

    
    @router.post("/refresh", status_code=201, response_model=ResponseRefresh)
    async def refresh(data: RequestRefresh,
        session = Depends(db.get_session)
    ) -> ResponseRefresh:
        try:
            payload = jwt_parser.validate_token(data.refresh_token)

            session_id: str = payload.get("sid")
            user_id: str = payload.get("sub")

            if not sessions_manager.is_session_exists(session_id):
                return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session is expired.")

            logger.debug(f"New access token generated with refresh token for user: {user_id}")

        except Exception as ex:
            logger.error(f"Couldn't add an object. {ex}")
            raise HTTPException(status_code=500, detail="Cannot refresh access token because of internal error.")

        return ResponseRefresh(
            access_token = await auth_service.get_access_token_by_refresh_token(data.refresh_token),
            refresh_token = jwt_parser.generate_refresh_token(
                user_id,
                session_id,
                data.refresh_token,
                make_old_refresh_token_used=True
            ),
        )
        

    return router


