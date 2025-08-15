import datetime
import random
from decimal import Decimal
from typing import List

from bs_models import *
from bs_schemas import *
from loguru import logger

from src.services.db.database import DataBase

data_base = DataBase()

def get_random_date():
        return datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365*5))


def get_random_date():
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=random.randint(0, 365 * 5))


def get_random_first_name():
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

def get_random_last_name():
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

def get_random_middle_name():
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

def get_random_author_name():
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

def get_random_product_name():
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

def get_random_location():
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

def get_random_string( length=10):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(length))


def get_random_phone():
    return f"79{random.randint(100000000, 99999999999999)}"


async def seed_data() -> None:
    async with data_base.async_session() as session:
        try:
            # ---------- USERS ----------
            users: List[User] = []
            n_users = random.randint(200, 400)  # безопасный объём
            logger.info(f"Seeding {n_users} users...")
            for _ in range(n_users):
                first = get_random_first_name()
                last = get_random_last_name()
                middle = get_random_middle_name()
                email = f"{get_random_string(10)}@example.com"
                phone = get_random_phone()

                user = User(
                    user_name=get_random_string(9),
                    hashed_password="Password123!",
                    first_name=first,
                    last_name=last,
                    middle_name=middle,
                    email=email,
                    phone=phone,
                    role=UserRole.user,  # по умолчанию обычный пользователь
                    is_active=True,
                    is_seller=False,
                )
                users.append(user)

            session.add_all(users)
            await session.flush()
            await session.commit()
            logger.info(f"{len(users)} users created.")

            # ---------- AUTHORS ----------
            authors: List[Author] = []
            n_authors = random.randint(30, 80)
            logger.info(f"Seeding {n_authors} authors...")
            for _ in range(n_authors):
                authors.append(Author(name=get_random_author_name()))
            session.add_all(authors)
            await session.flush()
            await session.commit()
            logger.info(f"{len(authors)} authors created.")

            # ---------- SELLERS (некоторым пользователям даём роль продавца) ----------
            sellers: List[Seller] = []
            n_sellers = max(20, int(len(users) / 30))  # примерно 1 продавец на 30 юзеров
            logger.info(f"Seeding {n_sellers} sellers...")
            # выбираем уникальные индексы пользователей
            seller_users = random.sample(users, n_sellers)
            for u in seller_users:
                u.role = UserRole.seller  # обновляем роль в объекте (он в сессии)
                seller = Seller(user_id=u.id, name=f"{u.first_name}'s shop")
                sellers.append(seller)

            session.add_all(sellers)
            await session.flush()
            await session.commit()
            logger.info(f"{len(sellers)} sellers created.")

            # ---------- WAREHOUSES ----------
            warehouses: List[Warehouse] = []
            n_warehouses = 40
            logger.info(f"Seeding {n_warehouses} warehouses...")
            for _ in range(n_warehouses):
                warehouses.append(Warehouse(available=True, location=get_random_location()))
            session.add_all(warehouses)
            await session.flush()
            await session.commit()
            logger.info(f"{len(warehouses)} warehouses created.")

            # ---------- PRODUCT TYPES ----------
            product_types: List[ProductType] = []
            n_product_types = random.randint(100, 200)
            logger.info(f"Seeding {n_product_types} product types...")
            for _ in range(n_product_types):
                seller_choice = random.choice(sellers)
                author_choice = random.choice(authors)
                pt = ProductType(
                    seller_id=seller_choice.id,
                    available=True,
                    name=get_random_product_name(),
                    cost=Decimal(f"{random.uniform(10, 500):.2f}"),
                    sale=random.uniform(0.0, 0.5),
                    author_id=author_choice.id,
                    date_publication=get_random_date(),
                )
                product_types.append(pt)

            session.add_all(product_types)
            await session.flush()
            await session.commit()
            logger.info(f"{len(product_types)} product types created.")

            # ---------- PRODUCTS ----------
            products: List[Product] = []
            logger.info("Seeding products (several per product type)...")
            for pt in product_types:
                # разумное число экземпляров на тип
                for _ in range(random.randint(1, 7)):
                    prod = Product(product_type_id=pt.id, warehouse_id=random.choice(warehouses).id)
                    products.append(prod)

            session.add_all(products)
            await session.flush()
            await session.commit()
            logger.info(f"{len(products)} products created.")

            # ---------- PURCHASES, ITEMS, DELIVERIES ----------
            purchases: List[Purchase] = []
            n_purchases = random.randint(8, 120)
            logger.info(f"Seeding {n_purchases} purchases with items and deliveries...")
            for _ in range(n_purchases):
                buyer = random.choice(users)
                seller = random.choice(sellers)

                delivery_group = DeliveryGroup(
                    target_warehouse_id=random.choice(warehouses).id,
                    target_user_id=buyer.id,
                    status=random.choice(list(DeliveryGroupStatusEnum)),
                )
                session.add(delivery_group)
                await session.flush()

                purchase = Purchase(
                    timestamp=get_random_date(),
                    payment_method=random.choice(list(PaymentMethodEnum)),
                    delivery_group_id=delivery_group.id,
                    buyer_id=buyer.id,
                    seller_id=seller.user_id,
                )
                session.add(purchase)
                await session.flush()

                # уникальные типы товаров в заказе
                chosen_types = random.sample(product_types, k=min(8, len(product_types)))
                for pt in chosen_types[: random.randint(1, 6)]:
                    item = PurchaseItem(
                        purchase_id=purchase.id,
                        product_type_id=pt.id,
                        quantity=random.randint(1, 8),
                        unit_cost=pt.cost,
                    )
                    session.add(item)

                # deliveries: привязываем к реальным product.id если есть
                for _ in range(random.randint(0, 3)):
                    if products:
                        delivery = Delivery(
                            product_id=random.choice(products).id,
                            status=random.choice(list(DeliveryStatusEnum)),
                        )
                        session.add(delivery)

                purchases.append(purchase)

            await session.commit()
            logger.info(f"{len(purchases)} purchases created with items and deliveries.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding data: {e}")
            import traceback
            logger.debug(traceback.format_exc())
