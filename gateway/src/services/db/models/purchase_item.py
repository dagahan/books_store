from src.services.db.models.base_model import *


class PurchaseItem(Base):
    __tablename__ = "purchases_items"
    
    purchase_id: Mapped[UUID] = mapped_column(ForeignKey('purchases.id'), primary_key=True)
    product_type_id: Mapped[UUID] = mapped_column(ForeignKey('product_types.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[money]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    purchase: Mapped["Purchase"] = relationship("Purchase", back_populates='items')
    product_type: Mapped["ProductType"] = relationship("ProductType", back_populates='purchase_items')
