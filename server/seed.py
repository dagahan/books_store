
import asyncio
import random

from faker import Faker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.db.database import DataBase
from src.services.db.models import (
    Author,
    DeliveryGroup,
    DeliveryGroupStatusEnum,
    PaymentMethodEnum,
    Product,
    ProductType,
    Purchase,
    PurchaseItem,
    Seller,
    User,
    Warehouse,
)

# Configuration for the amount of data to generate
NUM_USERS = 100
NUM_AUTHORS = 50
NUM_SELLERS = 30
NUM_WAREHOUSES = 10
NUM_PRODUCT_TYPES_PER_SELLER = 20
NUM_PRODUCTS_PER_PRODUCT_TYPE = 50
NUM_PURCHASES = 200


fake = Faker()

async def create_users(session: AsyncSession, num_users: int) -> list[User]:
    users = []
    for _ in range(num_users):
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            middle_name=fake.first_name(),  # Faker doesn't have a good middle_name generator
            email=fake.unique.email(),
            phone=fake.phone_number()[:16],
        )
        users.append(user)
    session.add_all(users)
    await session.commit()
    logger.info(f"Created {len(users)} users.")
    return users

async def create_authors(session: AsyncSession, num_authors: int) -> list[Author]:
    authors = []
    for _ in range(num_authors):
        author = Author(name=fake.name())
        authors.append(author)
    session.add_all(authors)
    await session.commit()
    logger.info(f"Created {len(authors)} authors.")
    return authors

async def create_warehouses(session: AsyncSession, num_warehouses: int) -> list[Warehouse]:
    warehouses = []
    for _ in range(num_warehouses):
        warehouse = Warehouse(
            available=fake.boolean(chance_of_getting_true=90),
            location=fake.address(),
        )
        warehouses.append(warehouse)
    session.add_all(warehouses)
    await session.commit()
    logger.info(f"Created {len(warehouses)} warehouses.")
    return warehouses

async def create_sellers(session: AsyncSession, users: list[User], num_sellers: int) -> list[Seller]:
    sellers = []
    # Ensure we don't try to create more sellers than available users
    num_sellers = min(num_sellers, len(users))
    seller_users = random.sample(users, num_sellers)
    
    for user in seller_users:
        seller = Seller(
            user_id=user.id,
            name=f"{user.first_name}'s Store",
        )
        sellers.append(seller)
    session.add_all(sellers)
    await session.commit()
    logger.info(f"Created {len(sellers)} sellers.")
    return sellers


async def create_product_types(session: AsyncSession, sellers: list[Seller], authors: list[Author], num_per_seller: int) -> list[ProductType]:
    product_types = []
    for seller in sellers:
        for _ in range(num_per_seller):
            product_type = ProductType(
                seller_id=seller.id,
                available=fake.boolean(chance_of_getting_true=95),
                cost=random.uniform(5.0, 150.0),
                sale=random.choice([None, random.uniform(0.1, 0.5)]),
                author_id=random.choice(authors).id,
                date_publication=fake.date_time_this_decade(),
            )
            product_types.append(product_type)
    session.add_all(product_types)
    await session.commit()
    logger.info(f"Created {len(product_types)} product types.")
    return product_types


async def create_products(session: AsyncSession, product_types: list[ProductType], warehouses: list[Warehouse], num_per_type: int) -> list[Product]:
    products = []
    for pt in product_types:
        for _ in range(num_per_type):
            product = Product(
                product_type_id=pt.id,
                warehouse_id=random.choice(warehouses).id,
            )
            products.append(product)
    session.add_all(products)
    await session.commit()
    logger.info(f"Created {len(products)} products.")
    return products


async def create_purchases_and_deliveries(
    session: AsyncSession,
    users: list[User],
    sellers: list[Seller],
    product_types: list[ProductType],
    warehouses: list[Warehouse],
    num_purchases: int,
):
    purchases = []
    purchase_items = []
    delivery_groups = []

    seller_users = [seller.user for seller in sellers]


    for _ in range(num_purchases):
        buyer = random.choice(users)
        seller_user = random.choice(seller_users)
        
        # Create DeliveryGroup first
        delivery_group = DeliveryGroup(
            target_warehouse_id=random.choice(warehouses).id,
            target_user_id=buyer.id,
            status=random.choice(list(DeliveryGroupStatusEnum)),
        )
        delivery_groups.append(delivery_group)
        
        # Create Purchase
        purchase = Purchase(
            timestamp=fake.date_time_this_year(),
            payment_method=random.choice(list(PaymentMethodEnum)),
            delivery_group=delivery_group,
            buyer_id=buyer.id,
            seller_id=seller_user.id
        )
        purchases.append(purchase)

        # Create PurchaseItems
        num_items = random.randint(1, 5)
        
        # Get product types available from the chosen seller
        available_product_types = [pt for pt in product_types if pt.seller.user_id == seller_user.id]
        if not available_product_types:
            continue

        selected_product_types = random.sample(
            available_product_types,
            min(num_items, len(available_product_types))
        )

        for pt in selected_product_types:
            purchase_item = PurchaseItem(
                purchase=purchase,
                product_type_id=pt.id,
                quantity=random.randint(1, 10),
                unit_cost=pt.cost,
            )
            purchase_items.append(purchase_item)
    
    session.add_all(delivery_groups)
    session.add_all(purchases)
    session.add_all(purchase_items)
    await session.commit()
    logger.info(f"Created {len(purchases)} purchases with {len(purchase_items)} items and {len(delivery_groups)} delivery groups.")


async def main():
    logger.info("Starting database seeding process.")
    
    db = DataBase()
    await db.init_alchemy_engine()

    async with db.async_session() as session:
        # Create base data
        users = await create_users(session, NUM_USERS)
        authors = await create_authors(session, NUM_AUTHORS)
        warehouses = await create_warehouses(session, NUM_WAREHOUSES)
        
        # Create sellers from a subset of users
        sellers = await create_sellers(session, users, NUM_SELLERS)
        
        # Create product types
        product_types = await create_product_types(session, sellers, authors, NUM_PRODUCT_TYPES_PER_SELLER)
        
        # Create individual products (stock)
        products = await create_products(session, product_types, warehouses, NUM_PRODUCTS_PER_PRODUCT_TYPE)
        
        # Create purchases, which also handles delivery groups and purchase items
        await create_purchases_and_deliveries(
            session, users, sellers, product_types, warehouses, NUM_PURCHASES
        )

    await db.engine.dispose()
    logger.success("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())


