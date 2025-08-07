from src.services.db.models.base_model import *


class Seller(Base):
    __tablename__ = "sellers"
    
    id: Mapped[UUIDpk]
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product_types: Mapped[list["ProductType"]] = relationship("ProductType", back_populates='seller')
    user: Mapped["User"] = relationship("User", back_populates='seller')
    