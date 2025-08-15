from .base_router import *


def get_token_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/tokens", tags=["tokens"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    auth_service = AuthService(db)

    
    @router.get("/access", status_code=200)
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

    
    @router.post("/refresh", status_code=201)
    async def refresh(data: RequestRefresh,
        session = Depends(db.get_session)
    ) -> ResponseRefresh:
        try:
            payload = jwt_parser.validate_token(data.refresh_token)

            test_dsh = sessions_manager.get_test_dsh()
            sessions_manager.create_session(
                payload.get("sub"),
                user_agent=test_dsh.get("user_agent"),
                client_id=test_dsh.get("client_id"),
                local_system_time_zone=test_dsh.get("local_system_time_zone"),
                platform=test_dsh.get("platform"),
                ip=StringTools.hash_string(sessions_manager.get_test_client_ip()),
            )
            logger.debug(f"New access token generated with refresh token for user: {payload.get("sub")}")

        except Exception as ex:
            logger.error(f"Couldn't add an object. {ex}")
            raise HTTPException(status_code=500, detail="Cannot refresh access token because of internal error.")

        return ResponseRefresh(
            access_token = await auth_service.get_access_token_by_refresh_token(data.refresh_token)
        )
        

    return router


