from src.services.db.models.base_model import *


class Delivery(Base):
    __tablename__ = "deliveries"
    
    id: Mapped[UUIDpk]
    product_id: Mapped[UUID] = mapped_column(ForeignKey('products.id'), nullable=False)
    status: Mapped[DeliveryStatusEnum] = mapped_column(Enum(DeliveryStatusEnum), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product: Mapped["Product"] = relationship("Product", back_populates='deliveries')
