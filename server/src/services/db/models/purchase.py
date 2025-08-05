from src.services.db.models.base_model import *


class Purchase(Base):
    __tablename__ = "purchases"
    
    id: Mapped[UUIDpk]
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(Enum(PaymentMethodEnum), nullable=False)
    delivery_group_id: Mapped[UUID] = mapped_column(ForeignKey('delivery_groups.id'), nullable=False)
    buyer_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    seller_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    delivery_group: Mapped["DeliveryGroup"] = relationship("DeliveryGroup", back_populates='purchase')
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id], back_populates='purchases_as_buyer')
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id], back_populates='purchases_as_seller')
    items: Mapped[list["PurchaseItem"]] = relationship("PurchaseItem", back_populates='purchase')
