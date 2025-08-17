from .base_router import *


def get_user_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    bearer_scheme = HTTPBearer()
    auth_service = AuthService(db)


    @router.post("/register", status_code=201, response_model=RegisterResponse)
    async def register(
        data: UserCreateDTO,
        session = Depends(db.get_session)
    ) -> RegisterResponse:
        
        if data.email and not await base_router.is_attribute_unique(session, User.email, data.email):
            raise base_router.http_ex_attribute_is_not_unique(User.email, "User")
        
        if data.phone and not await base_router.is_attribute_unique(session, User.phone, data.phone):
            raise base_router.http_ex_attribute_is_not_unique(User.phone, "User")

        if data.user_name and not await base_router.is_attribute_unique(session, User.user_name, data.user_name):
            raise base_router.http_ex_attribute_is_not_unique(User.user_name, "User")

        try:
            user = User(
                user_name=data.user_name,
                hashed_password=data.password.get_secret_value(),
                first_name=data.first_name.capitalize(),
                last_name=data.last_name.capitalize(),
                middle_name=data.middle_name.capitalize(),
                email=data.email,
                phone=data.phone,
                role=data.role,
                is_seller=data.is_seller,
            )

            session.add(user)
            await session.flush()
            await session.refresh(user)

            user_id: str = str(user.id) # converting to string because JSON can't serialize UUID :/

            test_dsh: Dict[str, str] = sessions_manager.get_test_dsh()
            session_id: str = sessions_manager.create_session(
                user_id,
                user_agent=test_dsh.get("user_agent"),
                client_id=test_dsh.get("client_id"),
                local_system_time_zone=test_dsh.get("local_system_time_zone"),
                platform=test_dsh.get("platform"),
                ip=StringTools.hash_string(sessions_manager.get_test_client_ip()),
            ).get("session_id")

            refresh_token: str = jwt_parser.generate_refresh_token(user_id, session_id)

            access_token: str = jwt_parser.generate_access_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token=refresh_token,
                make_refresh_token_used=False,
            )

            await session.commit()

        except Exception as ex:
            logger.error(f"Couldn't add an object. {ex}")
            raise HTTPException(status_code=500, detail="Cannot register a new user because of internal error.")
        
        logger.debug(f"Registered user with UUID {user.id}")

        return RegisterResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        

    @router.post("/login", status_code=201, response_model=LoginResponse)
    async def login(
        data: LoginRequest,
        session = Depends(db.get_session)
        ) -> LoginResponse:

        try:
            user: User = await base_router.find_user_by_any_credential(session, data)

            if not user.verify_password(data.password.get_secret_value()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive.")

            user_id: str = str(user.id)
            
            test_dsh: Dict[str, str] = sessions_manager.get_test_dsh()
            session_id: str = sessions_manager.create_session(
                user_id,
                user_agent=test_dsh.get("user_agent"),
                client_id=test_dsh.get("client_id"),
                local_system_time_zone=test_dsh.get("local_system_time_zone"),
                platform=test_dsh.get("platform"),
                ip=StringTools.hash_string(sessions_manager.get_test_client_ip()),
            ).get("session_id")

            refresh_token = jwt_parser.generate_refresh_token(user_id, session_id)

            access_token = jwt_parser.generate_access_token(
                user_id=user_id,
                session_id=session_id,
                refresh_token=refresh_token,
                make_refresh_token_used=False,
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Login error: {ex}")
            raise HTTPException(status_code=500, detail="Internal server error.")

        logger.debug(f"User {user.id} logged in (session {session_id})")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


    @router.post("/logout", status_code=200, response_model=LogoutResponse)
    async def logout(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session = Depends(db.get_session),) -> LogoutResponse:
        """
        Logout: Accepts the access_token, extracts the sid from the token, and deletes the corresponding session.
        """
        try:
            if credentials is None or not credentials.credentials:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing.")
            
            payload: Dict[str, Any] = base_router.get_payload_or_401(credentials)

            sid = payload.get("sid")
            if not sid:
                logger.debug(f"Access token missing session id (sid) claim: {payload}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token missing session id (sid).")

            try:
                sessions_manager.delete_session(sid)
                if sessions_manager.is_session_exists(sid):
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cannot delete session.")

            except Exception as ex:
                logger.exception(f"Error while deleting session {sid} {ex}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

            return LogoutResponse(
                succsess=True,
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.exception(f"Logout error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


    @router.post("/ban", status_code=200, response_model=BanResponse)
    async def ban_user(
        data: BanRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session = Depends(db.get_session),
        ) -> BanResponse:
        """
        The user's ban. Requires valid access from the administrator.
        """
        try:
            role = await base_router.check_user_role(credentials, session)
            if role not in (UserRole.admin, UserRole.god):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin rights required.")
                
            try:
                ban_user_id: uuid.UUID = data.ban_user_id if isinstance(data.ban_user_id, uuid.UUID) else uuid.UUID(str(data.ban_user_id))
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ban_user_id.")

            await auth_service.ban_user(user_id=ban_user_id)
            sessions_manager.delete_all_sessions_for_user(ban_user_id)
            return BanResponse(
                succsess=True
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.exception(f"Ban user error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


    @router.post("/unban", status_code=200, response_model=UnbanResponse)
    async def unban_user(
        data: UnbanRequest,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session = Depends(db.get_session),
        ) -> UnbanResponse:
        """
        The user's unban. Requires valid access from the administrator.
        """
        try:
            role = await base_router.check_user_role(credentials, session)
            if role not in (UserRole.admin, UserRole.god):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin rights required.")

            try:
                unban_user_id: uuid.UUID = data.unban_user_id if isinstance(data.unban_user_id, uuid.UUID) else uuid.UUID(str(data.unban_user_id))
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ban_user_id.")

            await auth_service.unban_user(user_id=unban_user_id)
            return UnbanResponse(
                succsess=True
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.exception(f"Unban user error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


    return router

