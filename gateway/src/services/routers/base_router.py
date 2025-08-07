from typing import Any, Iterable, List, Optional, Union
from uuid import UUID as PythonUUID

from loguru import logger
from pydantic import ValidationError
import colorama

from fastapi import APIRouter, HTTPException, Response, status, Depends

from src.services.db.schemas import *

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from src.services.db.database import DataBase
from src.services.db.schemas import *
from src.services.db.models import *


class BaseRouter:
    def __init__(self):
        pass
    

    def validate_models_by_schema(self, models: Any, schema: Any) -> Any:
        if not isinstance(models, Iterable):
            models = [models]

        valid_models = []
        for model in models:
            try:
                dto = schema.model_validate(model, from_attributes=True)
                valid_models.append(dto)
                
            except ValidationError as ex:
                model_id = getattr(model, "id", None)
                logger.warning(f"{colorama.Fore.YELLOW}Skipping invalid instance of {schema.__name__} (id={model_id}): {ex.errors()}")

        if len(valid_models) == 1:
            return valid_models[0]
        return valid_models
