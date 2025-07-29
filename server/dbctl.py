import argparse
import asyncio
import sys
from typing import List, Optional

from loguru import logger

from src.services.db.database import *
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
        subparsers.add_parser("update_users", help="Selects all users in database.")

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
                
                

            except Exception as e:
                await session.rollback()
                logger.error(f"Error inserting test data: {e}")
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

            except Exception as e:
                await session.rollback()
                logger.error(f"Error inserting test data: {e}")
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
                    return None
                
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
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating user {user_id}: {e}")
                raise
        

if __name__ == "__main__":
    asyncio.run(DbCtl().run())
