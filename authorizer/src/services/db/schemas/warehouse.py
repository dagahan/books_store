from .base_schema import *


class WarehouseDTO(TimestampMixin):
    id: UUID = Field(...)
    available: bool = Field(...)
    location: str = Field(..., max_length=256)


class WarehouseCreateDTO(BaseDTO):
    available: bool = Field(default=True)
    location: str = Field(..., min_length=1, max_length=256)


class WarehouseUpdateDTO(BaseDTO):
    available: Optional[bool] = Field(default=None)
    location: Optional[str] = Field(default=None, min_length=1, max_length=256)
