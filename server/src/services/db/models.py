import enum
import datetime
from uuid import uuid4

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Annotated


UUIDpk = Annotated[UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=func.now(), nullable=False)]
updated_at = Annotated[datetime.datetime, mapped_column
                       (
                            server_default=func.now(),
                            onupdate=func.now(),
                            nullable=False
                        )]
money = Annotated[Numeric, mapped_column(Numeric(10, 2), nullable=False)]


class Base(DeclarativeBase):
    # this is base class for all of declaratively using models of tables.
    # e.g. we use this for create or drop all of tables in db.
    pass


class PaymentMethodEnum(str, enum.Enum):
    cash = 'cash'
    card = 'card'


class DeliveryStatusEnum(str, enum.Enum):
    on_delivery = 'on_delivery'
    wait_for_delivery = 'wait_for_delivery'
    done = 'done'
    failed = 'failed'


class DeliveryGroupStatusEnum(str, enum.Enum):
    on_delivery = 'on_delivery'
    wait_for_delivery = 'wait_for_delivery'
    done = 'done'
    failed = 'failed'


class ProductType(Base):
    __tablename__ = "product_types"
    
    id: Mapped[UUIDpk]
    name: Mapped[str] = mapped_column(String(128), nullable=True)
    seller_id: Mapped[UUID] = mapped_column(ForeignKey('sellers.id'), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cost: Mapped[money]
    sale: Mapped[float] = mapped_column(Float, nullable=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('authors.id'), nullable=False)
    date_publication: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    seller: Mapped["Seller"] = relationship("Seller", back_populates='product_types')
    author: Mapped["Author"] = relationship("Author", back_populates='product_types')
    products: Mapped[list["Product"]] = relationship("Product", back_populates='product_type')
    purchase_items: Mapped[list["PurchaseItem"]] = relationship("PurchaseItem", back_populates='product_type')


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


class Delivery(Base):
    __tablename__ = "deliveries"
    
    id: Mapped[UUIDpk]
    product_id: Mapped[UUID] = mapped_column(ForeignKey('products.id'), nullable=False)
    status: Mapped[DeliveryStatusEnum] = mapped_column(Enum(DeliveryStatusEnum), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product: Mapped["Product"] = relationship("Product", back_populates='deliveries')


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


class Author(Base):
    __tablename__ = "authors"
    
    id: Mapped[UUIDpk]
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product_types: Mapped[list["ProductType"]] = relationship("ProductType", back_populates='author')


class Seller(Base):
    __tablename__ = "sellers"
    
    id: Mapped[UUIDpk]
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product_types: Mapped[list["ProductType"]] = relationship("ProductType", back_populates='seller')
    user: Mapped["User"] = relationship("User", back_populates='seller')


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUIDpk]
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=True)
    phone: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    delivery_groups: Mapped[list["DeliveryGroup"]] = relationship("DeliveryGroup", back_populates='target_user')
    purchases_as_buyer: Mapped[list["Purchase"]] = relationship("Purchase", foreign_keys="[Purchase.buyer_id]", back_populates='buyer')
    purchases_as_seller: Mapped[list["Purchase"]] = relationship("Purchase", foreign_keys="[Purchase.seller_id]", back_populates='seller')
    seller: Mapped["Seller"] = relationship("Seller", back_populates='user', uselist=False)


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id: Mapped[UUIDpk]
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    location: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates='warehouse')
    delivery_groups: Mapped[list["DeliveryGroup"]] = relationship("DeliveryGroup", back_populates='target_warehouse')
