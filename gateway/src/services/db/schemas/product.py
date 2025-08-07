from .base_schema import *


class ProductDTO(TimestampMixin):
    id: UUID = Field(...)
    product_type_id: UUID = Field(...)
    warehouse_id: UUID = Field(...)


class ProductCreateDTO(BaseDTO):
    product_type_id: UUID = Field(...)
    warehouse_id: UUID = Field(...)


class ProductUpdateDTO(BaseDTO):
    product_type_id: Optional[UUID] = Field(default=None)
    warehouse_id: Optional[UUID] = Field(default=None)
