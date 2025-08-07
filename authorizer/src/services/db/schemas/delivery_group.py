from .base_schema import *


class DeliveryGroupDTO(TimestampMixin):
    id: UUID = Field(...)
    target_warehouse_id: UUID = Field(...)
    target_user_id: UUID = Field(...)
    status: DeliveryGroupStatusDTO = Field(...)


class DeliveryGroupCreateDTO(BaseDTO):
    target_warehouse_id: UUID = Field(...)
    target_user_id: UUID = Field(...)
    status: DeliveryGroupStatusDTO = Field(...)


class DeliveryGroupUpdateDTO(BaseDTO):
    target_warehouse_id: Optional[UUID] = Field(default=None)
    target_user_id: Optional[UUID] = Field(default=None)
    status: Optional[DeliveryGroupStatusDTO] = Field(default=None)
