from .base_schema import *


class SellerDTO(TimestampMixin):
    id: UUID = Field(...)
    name: str = Field(..., min_length=1, max_length=128)
    user_id: UUID = Field(...)


class SellerCreateDTO(BaseDTO):
    name: str = Field(..., min_length=1, max_length=128)
    user_id: UUID = Field(...)


class SellerUpdateDTO(BaseDTO):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
