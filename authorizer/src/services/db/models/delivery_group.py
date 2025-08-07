from src.services.db.models.base_model import *


class DeliveryGroup(Base):
    __tablename__ = "delivery_groups"
    
    id: Mapped[UUIDpk]
    target_warehouse_id: Mapped[UUID] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    target_user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    status: Mapped[DeliveryGroupStatusEnum] = mapped_column(Enum(DeliveryGroupStatusEnum), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    target_warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates='delivery_groups')
    target_user: Mapped["User"] = relationship("User", back_populates='delivery_groups')
    purchase: Mapped["Purchase"] = relationship("Purchase", back_populates='delivery_group', uselist=False) # uselist=false mean one to one relate. not one to many
