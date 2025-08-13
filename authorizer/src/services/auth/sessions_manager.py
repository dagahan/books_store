from src.core.utils import EnvTools
from valkey import Valkey
import uuid
from datetime import datetime, timezone


class SessionsManager:
    def __init__(self) -> None:
        self.access_token_expire_minutes = int(EnvTools.load_env_var("ACCESS_TOKEN_EXPIRE_MINUTES"))
        self.valkey_service = Valkey(
            host=EnvTools.get_service_ip("valkey"),
            port=EnvTools.get_service_port("valkey"),
            decode_responses=True
        )


    def create_session(self, user_id: uuid.UUID) -> str:
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        self.valkey_service.hset(session_key, mapping={
            "user_id": str(user_id),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        self.valkey_service.expire(session_key, self.access_token_expire_minutes * 60)
        
        return session_id


    def delete_session(self, session_id: str) -> None:
        session_key = f"session:{session_id}"
        self.valkey_service.delete(session_key)


    def is_session_exists(self, session_id: str) -> bool:
        session_key = f"session:{session_id}"
        return self.valkey_service.exists(session_key) == 1


    def get_session_data(self, session_id: str) -> dict:
        session_key = f"session:{session_id}"
        return self.valkey_service.hgetall(session_key) or {}

        