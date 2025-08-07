from src.services.db.models.base_model import *


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUIDpk]
    hashed_password: Mapped[str] = mapped_column(Password, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=True)
    phone: Mapped[str] = mapped_column(String(16), nullable=False)
    role: Mapped[str] = mapped_column(UserRole, default=UserRole.user, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    delivery_groups: Mapped[list["DeliveryGroup"]] = relationship("DeliveryGroup", back_populates='target_user')
    purchases_as_buyer: Mapped[list["Purchase"]] = relationship("Purchase", foreign_keys="[Purchase.buyer_id]", back_populates='buyer')
    purchases_as_seller: Mapped[list["Purchase"]] = relationship("Purchase", foreign_keys="[Purchase.seller_id]", back_populates='seller')
    seller: Mapped["Seller"] = relationship("Seller", back_populates='user', uselist=False)


    def verify_password(self, plain_password: str) -> bool:
        return Password.verify(plain_password, self.hashed_password)
    
