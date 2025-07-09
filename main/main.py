import sys

import colorama
from loguru import logger

from src.core.config import ConfigLoader
from src.core.logging import InterceptHandler, LogSetup
from src.services.books import Books


class Service:
    def __init__(self):
        self.config = ConfigLoader()
        self.intercept_handler = InterceptHandler()
        self.logger_setup = LogSetup()
        self.books = Books()
        self.service_name = self.config.get("project", "name")


    def run_service(self):
        self.logger_setup.configure()
        self.books.setup_service()


if __name__ == "__main__":
    try:
        Service().run_service()
    except KeyboardInterrupt:
        logger.info(f"{colorama.Fore.CYAN}Service stopped by user")
    except Exception as error:
        logger.critical(f"{colorama.Fore.RED}Service crashed: {error}")
        sys.exit(1)
