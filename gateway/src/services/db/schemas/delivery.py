from .base_schema import *


class DeliveryDTO(TimestampMixin):
    id: UUID = Field(...)
    product_id: UUID = Field(...)
    status: DeliveryStatusDTO = Field(...)


class DeliveryCreateDTO(BaseDTO):
    product_id: UUID = Field(...)
    status: DeliveryStatusDTO = Field(...)


class DeliveryUpdateDTO(BaseDTO):
    product_id: Optional[UUID] = Field(default=None)
    status: Optional[DeliveryStatusDTO] = Field(default=None)
