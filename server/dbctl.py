import sys
import asyncio
from loguru import logger
import argparse
from typing import Optional, List
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
        logger.debug(f"test data is inserting...")

        async with self.data_base.async_session() as session:
            try:
                new_user = User(
                    first_name="Nikita",
                    last_name="Usov",
                    middle_name="Maksimovich",
                    email="nikitka223@gmail.com",
                    phone="79124100333"
                )
                
                session.add_all([new_user])
                await session.commit()
                
                logger.success(f"User inserted successfully! ID: {new_user.id}")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error inserting test data: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        

if __name__ == "__main__":
    asyncio.run(DbCtl().run())
