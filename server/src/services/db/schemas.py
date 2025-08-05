from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaymentMethodDTO(str, Enum):
    cash = 'cash'
    card = 'card'


class DeliveryStatusDTO(str, Enum):
    on_delivery = 'on_delivery'
    wait_for_delivery = 'wait_for_delivery'
    done = 'done'
    failed = 'failed'


class DeliveryGroupStatusDTO(str, Enum):
    on_delivery = 'on_delivery'
    wait_for_delivery = 'wait_for_delivery'
    done = 'done'
    failed = 'failed'


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class TimestampMixin(BaseDTO):
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class UserDTO(TimestampMixin):
    id: UUID = Field(...)
    first_name: str = Field(..., min_length=3, max_length=32)
    last_name: str = Field(..., min_length=3, max_length=32)
    middle_name: str = Field(..., min_length=3, max_length=32)
    email: Optional[str] = Field(default=None, max_length=64)
    phone: str = Field(..., min_length=11, max_length=16)

    @field_validator('first_name', 'last_name', 'middle_name', mode='before')
    def capitalize_name(cls, v: str) -> str:
        return v.strip().capitalize()


class UserCreateDTO(BaseDTO):
    first_name: str = Field(..., min_length=3, max_length=32)
    last_name: str = Field(..., min_length=3, max_length=32)
    middle_name: str = Field(..., min_length=3, max_length=32)
    email: Optional[str] = Field(default=None, max_length=64)
    phone: str = Field(..., min_length=11, max_length=16)

    @field_validator('first_name', 'last_name', 'middle_name', mode='before')
    def capitalize_name(cls, v: str) -> str:
        return v.strip().capitalize()


class UserUpdateDTO(BaseDTO):
    first_name: str = Field(default=None, min_length=3, max_length=32)
    last_name: str = Field(default=None, min_length=3, max_length=32)
    middle_name: str = Field(default=None, min_length=3, max_length=32)
    email: Optional[str] = Field(default=None, max_length=64)
    phone: str = Field(default=None, min_length=11, max_length=16)

    @field_validator('first_name', 'last_name', 'middle_name', mode='before')
    def capitalize_name(cls, v: str) -> str:
        return v.strip().capitalize()


class AuthorDTO(TimestampMixin):
    id: UUID = Field(...)
    name: str = Field(...)


class SellerDTO(TimestampMixin):
    id: UUID = Field(...)
    name: str = Field(...)
    user: UserDTO = Field(...)


class ProductTypeDTO(TimestampMixin):
    id: UUID = Field(...)
    name: str = Field(..., min_length=3, max_length=128)
    available: bool = Field(default=True)
    cost: float = Field(..., ge=0)
    sale: Optional[float] = Field(default=None, ge=0, le=1)
    date_publication: datetime = Field(...)
    seller: SellerDTO = Field(...)
    author: AuthorDTO = Field(default=None)
    
    @field_validator('cost', mode='before')
    def convert_decimal(cls, v):
        return float(v)


class ProductDTO(TimestampMixin):
    id: UUID = Field(...)
    product_type: ProductTypeDTO = Field(...)
    warehouse_id: UUID = Field(...)


class PurchaseItemDTO(TimestampMixin):
    product_type: ProductTypeDTO = Field(...)
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)

    @field_validator('unit_cost', mode='before')
    def convert_unit_cost(cls, v):
        return float(v)


class DeliveryDTO(TimestampMixin):
    id: UUID = Field(...)
    product: ProductDTO = Field(...)
    status: DeliveryStatusDTO = Field(...)


class DeliveryGroupDTO(TimestampMixin):
    id: UUID = Field(...)
    status: DeliveryGroupStatusDTO = Field(...)
    target_warehouse_id: UUID = Field(...)
    target_user: UserDTO = Field(...)


class PurchaseDTO(TimestampMixin):
    id: UUID = Field(...)
    timestamp: datetime = Field(...)
    payment_method: PaymentMethodDTO = Field(...)
    delivery_group: DeliveryGroupDTO = Field(default=None)
    buyer: UserDTO = Field(...)
    seller: UserDTO = Field(...)
    items: List[PurchaseItemDTO] = Field(...)
