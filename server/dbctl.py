import sys
from loguru import logger
import argparse
from typing import Optional, List
from src.services.db.database import *
from src.services.db.models import *


class DbCtl:
    def __init__(self) -> None:
        self.parser = self._setup_parser()
        self.data_base = DataBase()
        self.data_base.init_alchemy_engine()
        self.models = DataBaseTables()


    def _setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Using Alchemy via command prompts.",
        )
        subparsers = parser.add_subparsers(dest="command", help="Avaliable commands")
        subparsers.add_parser("insert_test", help="Inserts test data into tables.")

        return parser


    def run(self, args: Optional[List[str]] = None) -> None:
        parsed = self.parser.parse_args(args)

        if not parsed.command:
            self.parser.print_help()
            sys.exit(1)

        getattr(self, f"handle_{parsed.command}")(parsed)


    def handle_insert_test(self, args) -> None:
        print(f"test data is inserting...")

        users_table = self.models.users_table
        
        stmt = insert(users_table).values(
            {
            "first_name": "nikita",
            "last_name": "usov",
            "middle_name": "maksimovich",
            "email": "nikitka223@gmail.com",
            "phone": "79124100333"
        }
        )
        
        with self.data_base.engine.connect() as conn:
            try:
                conn.execute(stmt)
                conn.commit()
                print("User successfully inserted!")
            except Exception as e:
                conn.rollback()
                print(f"Error inserting user: {e}")
        

if __name__ == "__main__":
    DbCtl().run()
