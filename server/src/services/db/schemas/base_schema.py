from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, SecretStr



class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    seller = "seller"


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
