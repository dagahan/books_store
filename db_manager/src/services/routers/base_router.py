from typing import Any, Optional
from uuid import UUID as PythonUUID

from fastapi import HTTPException
from models import *
from schemas import *
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.db.database import DataBase


class BaseRouter:
    def __init__(self, db: DataBase):
        self.db = db
    

    async def is_attribute_unique(
        self,
        session: AsyncSession,
        attribute: Any,
        value: Any,
        exclude_id: Optional[PythonUUID | str] = None,
    ) -> bool:
        model = attribute.class_
        if not hasattr(model, '__tablename__'):
            raise ValueError("Attribute must be a SQLAlchemy column property")
        
        query = (
            select
            (
                model
            )
            .where(attribute == value)
        )
        
        if exclude_id is not None:
            query = query.where(model.id != exclude_id)
        
        result = await session.execute(query)
        return len(result.scalars().all()) == 0
    

    def http_ex_attribute_is_not_unique(self, attribute: Any, entity_name: str = "Entity") -> HTTPException:
        return HTTPException(
            status_code=400,
            detail=f"{entity_name} with this {getattr(attribute, 'key', str(attribute))} already exists"
        )
    
