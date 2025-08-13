from .base_router import *


def get_user_router() -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    base_router = BaseRouter()


    @app.post("/register", status_code=201)
    async def register(user_data: UserCreateDTO,
        session = Depends(db.get_session)
    ):
        
        if user_data.email and not await base_router.is_attribute_unique(session, User.email, user_data.email):
            raise base_router.http_ex_attribute_is_not_unique(User.email, "User")
        
        if user_data.phone and not await base_router.is_attribute_unique(session, User.phone, user_data.phone):
            raise base_router.http_ex_attribute_is_not_unique(User.phone, "User")

        user = User(
            first_name=user_data.first_name.capitalize(),
            last_name=user_data.last_name.capitalize(),
            middle_name=user_data.middle_name.capitalize(),
            email=user_data.email,
            phone=user_data.phone,
        )
        session.add(user)
        await session.commit()

        logger.debug(f"Created user with UUID {user.id}")
        return {"message": {"UUID": user.id}}
    

    @app.post("/login")
    async def login(credentials: LoginRequest):
        """Аутентификация пользователя"""
        # В реальной системе: проверка в БД
        user = User(id=1, username=credentials.username)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account deactivated"
            )
        
        # Создаем сессию
        session_id = create_session(user.id)
        
        # Генерируем токены
        tokens = create_tokens(user.id, session_id)
        
        return {
            **tokens,
            "session_id": session_id,
            "user_id": user.id
        }

    @app.post("/logout")
    async def logout(payload: TokenPayload = Depends(JWTBearer())):
        """Завершение сессии"""
        session_key = f"session:{payload.sid}"
        valkey.delete(session_key)
        return {"message": "Session terminated"}

    @app.get("/protected")
    async def protected_route(payload: TokenPayload = Depends(JWTBearer())):
        """Защищенный эндпоинт"""
        return {
            "message": f"Hello user {payload.sub}",
            "session_id": payload.sid
        }

    @app.post("/refresh")
    async def refresh_token(request: Request):
        """Обновление access токена"""
        refresh_token = request.headers.get("Authorization", "").split("Bearer ")[-1]
        
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if not payload.get("refresh"):
                raise JWTError("Not a refresh token")
            
            # Проверяем существование сессии
            session_key = f"session:{payload['sid']}"
            if not valkey.exists(session_key):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Session expired"
                )
            
            # Обновляем TTL сессии
            valkey.expire(session_key, ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            
            # Генерируем новые токены (с той же сессией)
            return create_tokens(payload["sub"], payload["sid"])
            
        except JWTError as e:
            logging.error(f"Refresh token error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

    @app.post("/admin/ban/{user_id}")
    async def ban_user(user_id: int):
        """Блокировка пользователя (админ)"""
        # Помечаем все сессии пользователя как забаненные
        for key in valkey.scan_iter("session:*"):
            session_data = valkey.hgetall(key)
            if session_data.get("user_id") == str(user_id):
                valkey.hset(key, "status", "banned")
        
        return {"message": f"User {user_id} banned"}

    @app.get("/health")
    async def health_check():
        """Проверка работоспособности"""
        valkey_status = "up" if valkey.ping() else "down"
        return {
            "api": "running",
            "valkey": valkey_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


    return router


