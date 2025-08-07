from redis import Redis
from valkey import Valkey

from src.core.utils import EnvTools

import uuid
from datetime import datetime, timezone
from jose import JWTError, jwt


class Valkey:
    def __init__(self) -> None:
        self.access_token_expire_minutes = EnvTools.load_env_var("ACCESS_TOKEN_EXPIRE_MINUTES")

        self.valkey = Valkey(
            host="valkey-alchemy",
            port=6379,
            decode_responses=True
        )


    def create_session(self, user_id: int) -> str:
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        self.valkey.hset(session_key, mapping={
            "user_id": user_id,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        self.valkey.expire(session_key, self.access_token_expire_minutes * 60)
        
        return session_id