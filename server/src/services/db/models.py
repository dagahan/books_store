from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Float,
    TIMESTAMP,
    ForeignKey,
    Enum,
    Numeric,
    )

import enum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import uuid4


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
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    seller_id: Mapped[UUID] = mapped_column(ForeignKey('sellers.id'), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    sale: Mapped[float] = mapped_column(Float, nullable=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('authors.id'), nullable=False)
    date_publication: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
    
    seller: Mapped["Seller"] = relationship("Seller", back_populates='product_types')
    author: Mapped["Author"] = relationship("Author", back_populates='product_types')
    products: Mapped[list["Product"]] = relationship("Product", back_populates='product_type')
    purchase_items: Mapped[list["PurchaseItem"]] = relationship("PurchaseItem", back_populates='product_type')


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_type_id: Mapped[UUID] = mapped_column(ForeignKey('product_types.id'), nullable=False)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    
    product_type: Mapped["ProductType"] = relationship("ProductType", back_populates='products')
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates='products')
    deliveries: Mapped[list["Delivery"]] = relationship("Delivery", back_populates='product')


class Purchase(Base):
    __tablename__ = "purchases"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(Enum(PaymentMethodEnum), nullable=False)
    delivery_group_id: Mapped[UUID] = mapped_column(ForeignKey('delivery_groups.id'), nullable=False)
    buyer_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    seller_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    delivery_group: Mapped["DeliveryGroup"] = relationship("DeliveryGroup", back_populates='purchase')
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id], back_populates='purchases_as_buyer')
    seller: Mapped["User"] = relationship("User", foreign_keys=[seller_id], back_populates='purchases_as_seller')
    items: Mapped[list["PurchaseItem"]] = relationship("PurchaseItem", back_populates='purchase')


class PurchaseItem(Base):
    __tablename__ = "purchases_items"
    
    purchase_id: Mapped[UUID] = mapped_column(ForeignKey('purchases.id'), primary_key=True)
    product_type_id: Mapped[UUID] = mapped_column(ForeignKey('product_types.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    purchase: Mapped["Purchase"] = relationship("Purchase", back_populates='items')
    product_type: Mapped["ProductType"] = relationship("ProductType", back_populates='purchase_items')


class Delivery(Base):
    __tablename__ = "deliveries"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey('products.id'), nullable=False)
    status: Mapped[DeliveryStatusEnum] = mapped_column(Enum(DeliveryStatusEnum), nullable=False)
    
    product: Mapped["Product"] = relationship("Product", back_populates='deliveries')


class DeliveryGroup(Base):
    __tablename__ = "delivery_groups"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    target_warehouse_id: Mapped[UUID] = mapped_column(ForeignKey('warehouses.id'), nullable=False)
    target_user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    status: Mapped[DeliveryGroupStatusEnum] = mapped_column(Enum(DeliveryGroupStatusEnum), nullable=False)
    
    target_warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates='delivery_groups')
    target_user: Mapped["User"] = relationship("User", back_populates='delivery_groups')
    purchase: Mapped["Purchase"] = relationship("Purchase", back_populates='delivery_group', uselist=False) # uselist=false mean one to one relate. not one to many


class Author(Base):
    __tablename__ = "authors"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    
    product_types: Mapped[list["ProductType"]] = relationship("ProductType", back_populates='author')


class Seller(Base):
    __tablename__ = "sellers"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True, nullable=False), ForeignKey('users.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    
    product_types: Mapped[list["ProductType"]] = relationship("ProductType", back_populates='seller')
    user: Mapped["User"] = relationship("User", back_populates='seller')


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(64), nullable=True)
    phone: Mapped[str] = mapped_column(String(16), nullable=False)
    
    delivery_groups: Mapped[list["DeliveryGroup"]] = relationship("DeliveryGroup", back_populates='target_user')
    purchases_as_buyer: Mapped[list["Purchase"]] = relationship("Purchase", foreign_keys="[Purchase.buyer_id]", back_populates='buyer')
    purchases_as_seller: Mapped[list["Purchase"]] = relationship("Purchase", foreign_keys="[Purchase.seller_id]", back_populates='seller')
    seller: Mapped["Seller"] = relationship("Seller", back_populates='user', uselist=False)


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    location: Mapped[str] = mapped_column(String(256), nullable=False)
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates='warehouse')
    delivery_groups: Mapped[list["DeliveryGroup"]] = relationship("DeliveryGroup", back_populates='target_warehouse')
