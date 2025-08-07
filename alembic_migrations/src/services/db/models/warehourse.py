from src.services.db.models.base_model import *


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id: Mapped[UUIDpk]
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    location: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates='warehouse')
    delivery_groups: Mapped[list["DeliveryGroup"]] = relationship("DeliveryGroup", back_populates='target_warehouse')
