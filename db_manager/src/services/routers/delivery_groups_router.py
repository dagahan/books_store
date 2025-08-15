from .base_router import *


def get_delivery_group_router(db: DataBase) -> APIRouter:
    router = APIRouter(prefix="/delivery_groups", tags=["Delivery Groups"])
    base_router = BaseRouter(db)


    @router.get("/", status_code=status.HTTP_200_OK)
    async def get_all_delivery_groups(
        session = Depends(db.get_session)
    ) -> Union[List[DeliveryGroupDTO] | DeliveryGroupDTO]:
        
        result = await session.execute(
            select(DeliveryGroup)
        )
        delivery_groups = result.scalars().all()

        if not delivery_groups:
            raise HTTPException(status_code=404, detail="There are no delivery_groups")
        
        return ValidatingTools.validate_models_by_schema(delivery_groups, DeliveryGroupDTO)


    @router.get("/{delivery_group_id}", status_code=status.HTTP_200_OK)
    async def get_delivery_group_by_id(
        delivery_group_id: PythonUUID,
        session = Depends(db.get_session)
    ) -> DeliveryGroupDTO:
        
        result = await session.execute(
            select(DeliveryGroup)
            .where(delivery_group.id == delivery_group_id)
        )
        delivery_group = result.scalars().first()

        if not delivery_group:
            raise HTTPException(status_code=404, detail="delivery_group not found")
        
        return ValidatingTools.validate_models_by_schema(delivery_group, DeliveryGroupDTO)


    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create_delivery_group(
        delivery_group_data: DeliveryGroupCreateDTO,
        session = Depends(db.get_session)
    ):
        
        if delivery_group_data.email and not await base_router.is_attribute_unique(session, delivery_group.email, delivery_group_data.email):
            raise base_router.http_ex_attribute_is_not_unique(delivery_group.email, "delivery_group")
        
        if delivery_group_data.phone and not await base_router.is_attribute_unique(session, delivery_group.phone, delivery_group_data.phone):
            raise base_router.http_ex_attribute_is_not_unique(delivery_group.phone, "delivery_group")

        delivery_group = delivery_group(
            first_name=delivery_group_data.first_name.capitalize(),
            last_name=delivery_group_data.last_name.capitalize(),
            middle_name=delivery_group_data.middle_name.capitalize(),
            email=delivery_group_data.email,
            phone=delivery_group_data.phone,
        )

        session.add(delivery_group)
        await session.commit()

        logger.debug(f"Created delivery_group with UUID {delivery_group.id}")
        return {"message": {"UUID": str(delivery_group.id)}}


    @router.patch("/{delivery_group_id}", status_code=status.HTTP_200_OK)
    async def update_delivery_group(
        delivery_group_id: PythonUUID,
        update_data: DeliveryGroupUpdateDTO,
        session = Depends(db.get_session)
    ):
        
        result = await session.execute(
            select(DeliveryGroup)
            .where(delivery_group.id == delivery_group_id)
            .options(noload("*"))
        )
        
        delivery_group = result.scalar_one_or_none()
        if not delivery_group:
            raise HTTPException(status_code=404, detail="delivery_group not found")

        data = update_data.model_dump(exclude_unset=True)
        if 'email' in data and not await base_router.is_attribute_unique(session, delivery_group.email, data['email'], exclude_id=delivery_group_id):
            raise base_router.http_ex_attribute_is_not_unique(delivery_group.email, "delivery_group")
        
        if 'phone' in data and not await base_router.is_attribute_unique(session, delivery_group.phone, data['phone'], exclude_id=delivery_group_id):
            raise base_router.http_ex_attribute_is_not_unique(delivery_group.phone, "delivery_group")

        for field, value in data.items():
            setattr(delivery_group, field, value)

        await session.commit()
        return Response(status_code=status.HTTP_200_OK)


    @router.delete("/{delivery_group_id}", status_code=status.HTTP_200_OK)
    async def delete_delivery_group(
        delivery_group_id: PythonUUID,
        session = Depends(db.get_session)
    ):
        
        result = await session.execute(
            select(DeliveryGroup)
            .where(delivery_group.id == delivery_group_id)
        )
        
        delivery_group = result.scalars().first()

        if not delivery_group:
            raise HTTPException(status_code=404, detail="delivery_group not found")
        await session.delete(delivery_group)
        await session.commit()
        return Response(status_code=status.HTTP_200_OK)


    return router
