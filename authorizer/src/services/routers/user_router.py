from .base_router import *


def get_user_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    bearer_scheme = HTTPBearer()


    @router.post("/register", status_code=201)
    async def register(data: UserCreateDTO,
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
            )

            session.add(user)
            await session.flush()
            await session.refresh(user)

            user_id = str(user.id) # converting to string because JSON can't serialize UUID :/

            session_id = sessions_manager.create_session(user_id)
            access_token = jwt_parser.generate_access_token(user_id, session_id)
            refresh_token = jwt_parser.generate_refresh_token(user_id, session_id)

            await session.commit()

        except Exception as ex:
            logger.error(f"Couldn't add an object. {ex}")
            raise HTTPException(status_code=500, detail=f"Cannot register a new user because of internal error.")
        
        logger.debug(f"Registered user with UUID {user.id}")

        return RegisterResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        

    @router.post("/login", status_code=201)
    async def login(data: LoginRequest,
        session = Depends(db.get_session)
        ) -> LoginResponse:

        try:
            user = await base_router.find_user_by_any_credential(session, data)

            if not user.verify_password(data.password.get_secret_value()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

            user_id = str(user.id)
            session_id = sessions_manager.create_session(user_id)
            access_token = jwt_parser.generate_access_token(user_id, session_id)
            refresh_token = jwt_parser.generate_refresh_token(user_id, session_id)

        except HTTPException:
            raise
        except Exception as ex:
            logger.error(f"Login error: {ex}")
            raise HTTPException(status_code=500, detail="Internal server error")

        logger.debug(f"User {user.id} logged in (session {session_id})")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


    @router.post("/logout", status_code=200, response_model=LogoutResponse)
    async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session = Depends(db.get_session),) -> LogoutResponse:
        """
        Logout: Accepts the access_token, extracts the sid from the token, and deletes the corresponding session.
        """
        try:
            if credentials is None or not credentials.credentials:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
            
            access_token = credentials.credentials

            try:
                payload = jwt_parser.decode_token(access_token)
            except Exception as ex:
                logger.debug(f"Invalid access token provided to logout: {ex}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")

            sid = payload.get("sid")
            if not sid:
                logger.debug(f"Access token missing session id (sid) claim: {payload}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token missing session id (sid)")

            try:
                deleted = sessions_manager.delete_session(sid)
            except Exception as ex:
                logger.exception(f"Error while deleting session {sid} {ex}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

            return LogoutResponse(
                succsess=True,
            )

        except HTTPException:
            raise
        except Exception as ex:
            logger.exception(f"Logout error: {ex}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    

    return router



