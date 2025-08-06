from .base_router import *


def get_user_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    base_router = BaseRouter(db)


    @router.get("/", status_code=status.HTTP_200_OK)
    async def get_all_users(
        session = Depends(db.get_session)
    ) -> Union[UserDTO | List[UserDTO]]:
        
        try:
            result = await session.execute(
                select(User)
            )
            users = result.scalars().all()

        except Exception as ex:
            logger.warning(f"Couldn't select an object. {ex}")
            raise HTTPException(status_code=404, detail=f"There are no users")

        if not users:
            raise HTTPException(status_code=404, detail="There are no users")
        
        return base_router.validate_models_by_schema(users, UserDTO)


    @router.get("/{user_id}", status_code=status.HTTP_200_OK)
    async def get_user_by_id(
        user_id: PythonUUID,
        session = Depends(db.get_session)
    ) -> UserDTO:
        
        try:
            result = await session.execute(
                select(User)
                .where(User.id == user_id)
            )
            user = result.scalars().first()

        except Exception as ex:
            logger.warning(f"Couldn't select an object. {ex}")
            raise HTTPException(status_code=404, detail=f"User not found")        

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return base_router.validate_models_by_schema(user, UserDTO)


    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create_user(
        user_data: UserCreateDTO,
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


    @router.patch("/{user_id}", status_code=status.HTTP_200_OK)
    async def update_user(
        user_id: PythonUUID,
        update_data: UserUpdateDTO,
        session = Depends(db.get_session)
    ):
        try:
            result = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(noload("*"))
            )
            user = result.scalars().first()

        except Exception as ex:
            logger.warning(f"Couldn't select an object. {ex}")
            raise HTTPException(status_code=404, detail=f"User not found")

        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data = update_data.model_dump(exclude_unset=True)
        if 'email' in data and not await base_router.is_attribute_unique(session, User.email, data['email'], exclude_id=user_id):
            raise base_router.http_ex_attribute_is_not_unique(User.email, "User")
        
        if 'phone' in data and not await base_router.is_attribute_unique(session, User.phone, data['phone'], exclude_id=user_id):
            raise base_router.http_ex_attribute_is_not_unique(User.phone, "User")

        for field, value in data.items():
            setattr(user, field, value)
        await session.commit()

        return Response(status_code=status.HTTP_200_OK)


    @router.delete("/{user_id}", status_code=status.HTTP_200_OK)
    async def delete_user(
        user_id: PythonUUID,
        session = Depends(db.get_session)
    ):
        try:
            result = await session.execute(
                select(User)
                .where(User.id == user_id)
            )
            user = result.scalars().first()

        except Exception as ex:
            logger.warning(f"Couldn't select an object. {ex}")
            raise HTTPException(status_code=404, detail=f"User not found")

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await session.delete(user)
        await session.commit()
        return Response(status_code=status.HTTP_200_OK)


    return router