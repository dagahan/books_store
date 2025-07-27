from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    MetaData,
    BigInteger,
    Boolean,
    Float,
    TIMESTAMP,
    ForeignKey,
    Enum,
    Numeric,
    )

from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class DataBaseTables:
    def __init__(self):
        self.metadata_object = MetaData()

        self.products_types_table = Table(
            "product_types",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("seller", UUID, ForeignKey('sellers.id'), nullable=False),
            Column("avaliable", Boolean, nullable=False),
            Column("cost", Numeric(10, 2), nullable=False),
            Column("sale", Float),
            Column("author", UUID, ForeignKey('authors.id'), nullable=False),
            Column("date_publication", TIMESTAMP, nullable=False),
        )

        self.products_table = Table(
            "products",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("product_type_id", UUID, ForeignKey('product_types.id'), nullable=False),
            Column("warehouses", UUID, ForeignKey('warehouses.id'), nullable=False),
        )

        self.purchases_table = Table(
            "purchases",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("timestamp", TIMESTAMP, nullable=False),
            Column("payment_method", Enum('cash', 'card', name='payment_method_enum'), nullable=False),
            Column("delivery_group_id", UUID, ForeignKey('delivery_groups.id'), nullable=False),
            Column("buyer", UUID, ForeignKey('users.id'), nullable=False),
            Column("seller", UUID, ForeignKey('users.id'), nullable=False),
        )

        self.purchases_items_table = Table(
            "purchases_items",
            self.metadata_object,
            Column("purchase_id", ForeignKey('purchases.id'), primary_key=True),
            Column("product_type_id", ForeignKey('product_types.id'), primary_key=True),
            Column("quantity", Integer, nullable=False),
            Column("unit_cost", Numeric(10, 2)),
        )

        self.deliveries_table = Table(
            "deliveries",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("product_id", UUID, ForeignKey('products.id')),
            Column("status", Enum('on_delivery', 'wait_for_delivery', 'done', 'failed', name='deliveries_status_enum'), nullable=False),
        )

        self.delivery_groups_table = Table(
            "delivery_groups",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("target_warehouse", UUID, ForeignKey('warehouses.id')),
            Column("target_user", UUID, ForeignKey('users.id')),
            Column("status", Enum('on_delivery', 'wait_for_delivery', 'done', 'failed', name='delivery_groups_status_enum'), nullable=False),
        )

        self.authors_table = Table(
            "authors",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("name", String(128), nullable=False),
        )

        self.sellers_table = Table(
            "sellers",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("name", String(128), nullable=False),
        )

        self.users_table = Table(
            "users",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("first_name", String(32), nullable=False),
            Column("last_name", String(32), nullable=False),
            Column("middle_name", String(32), nullable=False),
            Column("email", String(32), nullable=True),
            Column("phone", String(11), nullable=False),
        )

        self.warehouses_table = Table(
            "warehouses",
            self.metadata_object,
            Column("id", UUID, primary_key=True, default=uuid4),
            Column("avaliable", Boolean, nullable=False),
            Column("location", String(256), nullable=False),
        )

        

