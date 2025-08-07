from src.services.db.models.base_model import *


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[UUIDpk]
    product_type_id: Mapped[UUID] = mapped_column(ForeignKey('product_types.id'), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product_type: Mapped["ProductType"] = relationship("ProductType", back_populates='products')
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates='products')
    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates='product')
