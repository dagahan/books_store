from .base_router import *


def get_user_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)


    @router.post("/register", status_code=201)
    async def register(user_data: UserCreateDTO,
        session = Depends(db.get_session)
    ) -> RegisterResponse:
        
        if user_data.email and not await base_router.is_attribute_unique(session, User.email, user_data.email):
            raise base_router.http_ex_attribute_is_not_unique(User.email, "User")
        
        if user_data.phone and not await base_router.is_attribute_unique(session, User.phone, user_data.phone):
            raise base_router.http_ex_attribute_is_not_unique(User.phone, "User")

        try:
            hashed_password = Password.hash_password(user_data.password.get_secret_value())

            user = User(
            hashed_password=hashed_password,
            first_name=user_data.first_name.capitalize(),
            last_name=user_data.last_name.capitalize(),
            middle_name=user_data.middle_name.capitalize(),
            email=user_data.email,
            phone=user_data.phone,
            role=user_data.role,
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
            token_type="bearer"
        )
        

    @router.post("/login", status_code=200)
    async def login(user_data: UserCreateDTO,
        session = Depends(db.get_session)
    ) -> RegisterResponse:
        
        if user_data.email and not await base_router.is_attribute_unique(session, User.email, user_data.email):
            raise base_router.http_ex_attribute_is_not_unique(User.email, "User")
        
        if user_data.phone and not await base_router.is_attribute_unique(session, User.phone, user_data.phone):
            raise base_router.http_ex_attribute_is_not_unique(User.phone, "User")

        try:
            hashed_password = Password.hash_password(user_data.password.get_secret_value())

            user = User(
            hashed_password=hashed_password,
            first_name=user_data.first_name.capitalize(),
            last_name=user_data.last_name.capitalize(),
            middle_name=user_data.middle_name.capitalize(),
            email=user_data.email,
            phone=user_data.phone,
            role=user_data.role,
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
            token_type="bearer"
        )

    

    return router


