import argparse
import asyncio
import datetime
import random
import sys
from decimal import Decimal
from typing import List, Optional

from loguru import logger
from sqlalchemy import (
    and_,
    select,
)

from src.services.db.database import DataBase
from src.services.db.schemas import *
from src.services.db.models import *


class DbCtl:
    def __init__(self) -> None:
        self.parser = self._setup_parser()
        self.data_base = DataBase()


    def _setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Using Alchemy via command prompts.",
        )
        subparsers = parser.add_subparsers(dest="command", help="Avaliable commands")
        subparsers.add_parser("insert_test", help="Inserts test data into tables.")
        subparsers.add_parser("select_users", help="Selects all users in database.")
        subparsers.add_parser("select_deliveries", help="Selects all users in database.")
        subparsers.add_parser("update_users", help="Selects all users in database.")
        subparsers.add_parser("seed_data", help="Seeds database with comprehensive test data for all models.")

        return parser
    

    async def init_db(self):
        await self.data_base.init_alchemy_engine()


    async def run(self, args: Optional[List[str]] = None) -> None:
        parsed = self.parser.parse_args(args)

        if not parsed.command:
            self.parser.print_help()
            sys.exit(1)

        await self.init_db()
        await getattr(self, f"handle_{parsed.command}")(parsed)


    async def handle_insert_test(self, args) -> None:
        async with self.data_base.async_session() as session:
            try:
                new_users = User(
                    first_name="Nikita",
                    last_name="Usov",
                    middle_name="Maksimovich",
                    email="nikitka223@gmail.com",
                    phone="79124100333"
                ), User(
                    first_name="Maxim",
                    last_name="Usov",
                    middle_name="Victorovich",
                    email="mvusov@gmail.com",
                    phone="79124155235"
                ), User(
                    first_name="Jaba",
                    last_name="Usova",
                    middle_name="Victorovna",
                    email="jabau@gmail.com",
                    phone="79124444533"
                ), User(
                    first_name="Yana",
                    last_name="Alshekova",
                    middle_name="Georgeevna",
                    email="georgeevna22@gmail.com",
                    phone="79151238735"
                ), User(
                    first_name="Olga",
                    last_name="Usova",
                    middle_name="Vladimirna",
                    email="vladimirnaolga24@gmail.com",
                    phone="79135785235"
                )
                    
                for user in new_users:
                    session.add(user)
                    logger.success(f"User inserted successfully! ID: {user.id}")
                
                await session.commit()
                
                

            except Exception as ex:
                await session.rollback()
                logger.error(f"Error inserting test data: {ex}")
                import traceback
                logger.debug(traceback.format_exc())


    async def handle_select_deliveries(self, args):
        async with self.data_base.async_session() as session:
            try:
                query = (
                    select (
                        DeliveryGroup.status,
                    )
                    .select_from(DeliveryGroup)
                    .filter(and_(
                            DeliveryGroup.status == DeliveryGroupStatusEnum.on_delivery
                        ))
                )
                
                result = await session.execute(query)
                delivery_groups = result.scalars().all()

                logger.info(f"Founded {len(delivery_groups)} deliveriy groups with status {DeliveryGroupStatusEnum.on_delivery.name}")

                # for i, delivery_group in enumerate(delivery_groups, start=1):
                #     logger.info(f"Index: {i}. | {delivery_group.__dict__}")

            except Exception as ex:
                await session.rollback()
                logger.error(f"Error inserting test data: {ex}")
                import traceback
                logger.debug(traceback.format_exc())


    async def handle_select_users(self, args) -> None:
        async with self.data_base.async_session() as session:
            try:
                query = select(User)
                result = await session.execute(query)
                users = result.scalars().all()
                
                logger.info(f"Found {len(users)} users:")
                for user in users:
                    logger.info(user.__dict__)
                    logger.info(user.id)

            except Exception as ex:
                await session.rollback()
                logger.error(f"Error inserting test data: {ex}")
                import traceback
                logger.debug(traceback.format_exc())

    
    async def handle_update_users(self, args) -> None:
        async with self.data_base.async_session() as session:
            try:
                user_id = "a8cfaeb5-5ecd-4657-b0d7-d3765ea42870"
                update_data = {
                    "first_name": "NewFirstName",
                    "email": "new.email@example.com",
                    "phone": "+79991112233"
                }
                result = await session.execute(select(User).filter(User.id == user_id))
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.error(f"User with ID {user_id} not found")
                    return
                
                valid_fields = {'first_name', 'last_name', 'middle_name', 'email', 'phone'}
                invalid_fields = set(update_data.keys()) - valid_fields
                
                if invalid_fields:
                    raise ValueError(f"Invalid fields for update: {', '.join(invalid_fields)}")
                
                for field, value in update_data.items():
                    if hasattr(user, field):
                        setattr(user, field, value)
                    else:
                        logger.warning(f"Ignoring unknown field: {field}")
                
                session.add(user)
                await session.commit()
                
                logger.success(f"User {user_id} updated successfully")
                
            except Exception as ex:
                await session.rollback()
                logger.error(f"Error updating user {user_id}: {ex}")
                raise
        

    def _get_random_date(self):
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365*5))


    def _get_random_first_name(self):
        return random.choice([
            "Алексей", "Максим", "Мария", "Ольга", "Дмитрий",
            "Анна", "Сергей", "Елена", "Иван", "Наталья",
            "Андрей", "Екатерина", "Михаил", "Татьяна", "Владимир",
            "Светлана", "Александр", "Ирина", "Юрий", "Людмила",
            "Константин", "Виктор", "Ксения", "Павел", "Полина",
            "Григорий", "Вероника", "Борис", "Диана", "Роман",
            "Кирилл", "Жанна", "Василиса", "Рустам", "Дарья",
            "Роберт", "Лилия", "Игорь", "Нина", "Тимофей"
        ])

    def _get_random_last_name(self):
        return random.choice([
            "Иванов", "Петров", "Сидоров", "Федоров", "Васильев",
            "Кузнецов", "Попов", "Морозов", "Волков", "Соколов",
            "Новиков", "Фишер", "Козлов", "Орлов", "Лебедев",
            "Семенов", "Егоров", "Павлов", "Захаров", "Степанов",
            "Никитин", "Макаров", "Алексеев", "Гусев", "Лазарев",
            "Медведев", "Крылов", "Гаврилов", "Дорофеев", "Виноградов",
            "Карпов", "Поляков", "Осипов", "Прохоров", "Фролов",
            "Антонов", "Романов", "Шестаков", "Николаев", "Афанасьев"
        ])

    def _get_random_middle_name(self):
        return random.choice([
            "Алексеевич", "Максимович", "Дмитриевич", "Сергеевич", "Иванович",
            "Андреевич", "Михайлович", "Александрович", "Владимирович", "Петрович",
            "Алексеевна", "Максимовна", "Дмитриевна", "Сергеевна", "Ивановна",
            "Андреевна", "Михайловна", "Александровна", "Владимировна", "Петровна",
            "Николаевич", "Викторович", "Николаевна", "Викторовна", "Григорьевич",
            "Григорьевна", "Юрьевич", "Юрьевна", "Романович", "Романовна",
            "Борисович", "Борисовна", "Тимофеевич", "Тимофеевна", "Константинович",
            "Константиновна", "Рустамович", "Рустамовна", "Дмитриевна", "Дмитриевич"
        ])

    def _get_random_author_name(self):
        return random.choice([
            "Александр Пушкин", "Лев Толстой", "Федор Достоевский", "Антон Чехов",
            "Иван Тургенев", "Николай Гоголь", "Михаил Лермонтов", "Анна Ахматова",
            "Борис Пастернак", "Владимир Маяковский", "Сергей Есенин", "Марина Цветаева",
            "Иосиф Бродский", "Варлам Шаламов", "Александр Солженицын", "Василий Шукшин",
            "Николай Некрасов", "Дмитрий Мережковский", "Иван Бунин", "Михаил Булгаков",
            "Юрий Олеша", "Набоков Владимир", "Александр Грибоедов", "Валентин Распутин",
            "Всеволод Иванов", "Юрий Трифонов", "Константин Паустовский", "Владимир Набоков",
            "Анна Каренина", "Лидия Чуковская", "Валерий Брюсов", "Ольга Берггольц",
            "Осип Мандельштам", "Михаил Пришвин", "Виктор Астафьев", "Валентин Катаев",
            "Константин Симонов", "Михаил Зощенко"
        ])

    def _get_random_product_name(self):
        return random.choice([
            "Смартфон", "Ноутбук", "Планшет", "Наушники", "Клавиатура",
            "Мышь", "Монитор", "Принтер", "Веб-камера", "Колонки",
            "Роман", "Детектив", "Фантастика", "Биография", "Учебник",
            "Куртка", "Джинсы", "Футболка", "Платье", "Обувь",
            "Настольная игра", "Пазл", "Конструктор", "Мяч", "Ракетка",
            "Гитара", "Саксофон", "Микрофон", "Чехол", "Наушники-беспроводные",
            "Кофемашина", "Тостер", "Мороженица", "Плеер", "Телевизор",
            "Фотоаппарат", "Шахматы", "Головоломка", "Планшет-фонарик", "Путеводитель"
        ])

    def _get_random_location(self):
        return random.choice([
            "Москва, ул. Тверская 1", "Санкт-Петербург, Невский пр. 10",
            "Новосибирск, ул. Ленина 25", "Екатеринбург, ул. Малышева 15",
            "Казань, ул. Баумана 30", "Нижний Новгород, ул. Большая Покровская 5",
            "Челябинск, ул. Кирова 20", "Самара, ул. Ленинградская 35",
            "Омск, ул. Маркса 40", "Ростов-на-Дону, пр. Ворошиловский 12",
            "Владивосток, ул. Светланская 2", "Ярославль, ул. Волковская 14",
            "Иркутск, ул. Ленина 10", "Томск, пр. Ленина 50", "Оренбург, ул. Советская 9",
            "Уфа, ул. Ленина 1", "Воронеж, ул. Плехановская 60", "Пермь, ул. Ленина 53",
            "Краснодар, ул. Красная 80", "Волгоград, пр. Ленина 45", "Рязань, ул. Соборная 12",
            "Нижнекамск, ул. Мира 5", "Череповец, ул. Ленина 33", "Кемерово, пр. Советский 22",
            "Тула, ул. Советская 99", "Иваново, ул. Радищева 7", "Липецк, ул. Октябрьская 15",
            "Тамбов, ул. Советская 12", "Саратов, ул. Мичурина 18", "Ульяновск, ул. Ленина 20",
            "Барнаул, пр. Ленина 30", "Калининград, ул. Театральная 1", "Сургут, пр. Мира 40",
            "Новороссийск, ул. Советская 11", "Мурманск, ул. Ленинградская 5", "Севастополь, пр. Нахимова 3"
        ])

    def _get_random_string(self, length=10):
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(length))


    def _get_random_phone(self):
        return f"79{random.randint(100000000, 99999999999999)}"


    async def handle_seed_data(self, args) -> None:
        async with self.data_base.async_session() as session:
            try:
                users = []
                for _ in range(random.randint(1500, 2500)):
                    user = User(
                        first_name=self._get_random_first_name(),
                        last_name=self._get_random_last_name(),
                        middle_name=self._get_random_middle_name(),
                        email=f"{self._get_random_string(10)}@example.com",
                        phone=self._get_random_phone(),
                    )
                    users.append(user)
                session.add_all(users)
                await session.flush()
                logger.info(f"{len(users)} users created.")

                authors = []
                for _ in range(random.randint(20, 500)):
                    author = Author(name=self._get_random_author_name())
                    authors.append(author)
                session.add_all(authors)
                await session.flush()
                logger.info(f"{len(authors)} authors created.")

                sellers = []
                for i in range(random.randint(20, int(len(users) / 10))):
                    seller = Seller(
                        user_id=users[i].id,
                        name=f"{self._get_random_first_name()}\'s shop"
                    )
                    sellers.append(seller)
                session.add_all(sellers)
                await session.flush()
                logger.info(f"{len(sellers)} sellers created.")

                warehouses = []
                for _ in range(140):
                    warehouse = Warehouse(
                        available=True,
                        location=self._get_random_location()
                    )
                    warehouses.append(warehouse)
                session.add_all(warehouses)
                await session.flush()
                logger.info(f"{len(warehouses)} warehouses created.")

                product_types = []
                for _ in range(random.randint(100, 1000)):
                    product_type = ProductType(
                        seller_id=random.choice(sellers).id,
                        available=True,
                        name=self._get_random_product_name(),
                        cost=Decimal(f"{random.uniform(10, 500):.2f}"),
                        sale=random.uniform(0.0, 0.5),
                        author_id=random.choice(authors).id,
                        date_publication=self._get_random_date(),
                    )
                    product_types.append(product_type)
                session.add_all(product_types)
                await session.flush()
                logger.info(f"{len(product_types)} product types created.")

                products = []
                for pt in product_types:
                    for _ in range(random.randint(50, 100)):
                        product = Product(
                            product_type_id=pt.id,
                            warehouse_id=random.choice(warehouses).id
                        )
                        products.append(product)
                session.add_all(products)
                await session.flush()
                logger.info(f"{len(products)} products created.")

                purchases = []
                for i in range(random.randint(50, 150)):
                    buyer = random.choice(users)
                    seller = random.choice(sellers)
                    
                    delivery_group = DeliveryGroup(
                        target_warehouse_id=random.choice(warehouses).id,
                        target_user_id=buyer.id,
                        status=random.choice(list(DeliveryGroupStatusEnum))
                    )
                    session.add(delivery_group)
                    await session.flush()

                    purchase = Purchase(
                        timestamp=self._get_random_date(),
                        payment_method=random.choice(list(PaymentMethodEnum)),
                        delivery_group_id=delivery_group.id,
                        buyer_id=buyer.id,
                        seller_id=seller.user_id
                    )
                    session.add(purchase)
                    await session.flush()
                    purchases.append(purchase)

                    product_types_set = set({})
                    for i in range(10):
                        type = random.choice(product_types)
                        if type not in product_types_set:
                            product_types_set.add(type)
                            purchase_item = PurchaseItem(
                                purchase_id=purchase.id,
                                product_type_id=type.id,
                                quantity=random.randint(1, 10),
                                unit_cost=product_type.cost
                            )
                            session.add(purchase_item)

                    for _ in range(random.randint(1, 3)):
                        if products:
                            delivery = Delivery(
                                product_id=random.choice(products).id,
                                status=random.choice(list(DeliveryStatusEnum))
                            )
                            session.add(delivery)
                
                await session.commit()
                logger.info(f"{len(purchases)} purchases created with items and deliveries.")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error seeding data: {e}")
                import traceback
                logger.debug(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(DbCtl().run())
