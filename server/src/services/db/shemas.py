from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum
from uuid import UUID, uuid4


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
    created_at: datetime
    updated_at: datetime


class UserDTO(TimestampMixin):
    id: UUID
    first_name: str
    last_name: str
    middle_name: str
    email: Optional[str] = None
    phone: str


class UserCreateDTO(BaseDTO):
    first_name: str
    last_name: str
    middle_name: str
    email: Optional[str] = None
    phone: str


class UserUpdateDTO(BaseDTO):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class AuthorDTO(TimestampMixin):
    id: UUID
    name: str


class SellerDTO(TimestampMixin):
    id: UUID
    name: str
    user: UserDTO


class ProductTypeDTO(TimestampMixin):
    id: UUID
    name: Optional[str]
    available: bool
    cost: float = Field(..., ge=0)
    sale: Optional[float] = Field(None, ge=0, le=1)
    date_publication: datetime
    seller: SellerDTO
    author: AuthorDTO

    @field_validator('cost', mode='before')
    def convert_decimal(cls, v):
        return float(v)


class ProductDTO(TimestampMixin):
    id: UUID
    product_type: ProductTypeDTO
    warehouse_id: UUID


class PurchaseItemDTO(TimestampMixin):
    product_type: ProductTypeDTO
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)

    @field_validator('unit_cost', mode='before')
    def convert_unit_cost(cls, v):
        return float(v)


class DeliveryDTO(TimestampMixin):
    id: UUID
    product: ProductDTO
    status: DeliveryStatusDTO


class DeliveryGroupDTO(TimestampMixin):
    id: UUID
    status: DeliveryGroupStatusDTO
    target_warehouse_id: UUID
    target_user: UserDTO


class PurchaseDTO(TimestampMixin):
    id: UUID
    timestamp: datetime
    payment_method: PaymentMethodDTO
    delivery_group: DeliveryGroupDTO
    buyer: UserDTO
    seller: UserDTO
    items: List[PurchaseItemDTO]
