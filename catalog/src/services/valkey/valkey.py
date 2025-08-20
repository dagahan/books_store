
from valkey import Valkey

from src.core.config import ConfigLoader
from src.core.utils import EnvTools


class ValkeyService:
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.valkey = Valkey(
            host=EnvTools.get_service_ip("valkey"),
            port=int(EnvTools.get_service_port("valkey")),
            decode_responses=True
        )

