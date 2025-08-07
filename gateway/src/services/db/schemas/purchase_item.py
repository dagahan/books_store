from .base_schema import *


class PurchaseItemDTO(TimestampMixin):
    purchase_id: UUID = Field(...)
    product_type_id: UUID = Field(...)
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)

    @field_validator('unit_cost', mode='before')
    def convert_unit_cost(cls, v):
        return float(v)


class PurchaseItemCreateDTO(BaseDTO):
    purchase_id: UUID = Field(...)
    product_type_id: UUID = Field(...)
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)
    
    @field_validator('unit_cost', mode='before')
    def convert_unit_cost(cls, v):
        return float(v)


class PurchaseItemUpdateDTO(BaseDTO):
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_cost: Optional[float] = Field(default=None, ge=0)
    
    @field_validator('unit_cost', mode='before')
    def convert_unit_cost(cls, v):
        if v is not None:
            return float(v)
        return v
