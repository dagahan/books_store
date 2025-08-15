from valkey import Valkey
import uuid
from datetime import datetime, timezone
from src.core.utils import EnvTools, StringTools, TimeTools, ValidatingTools
from bs_schemas import Session
from typing import Dict, Optional, Any
from loguru import logger
from types import SimpleNamespace
from collections.abc import Mapping


class SessionsManager:
    def __init__(self) -> None:
        self.session_max_life_days = int(EnvTools.load_env_var("SESSIONS_MAX_LIFE_DAYS"))
        self.session_inactive_days = int(EnvTools.load_env_var("SESSIONS_INACTIVE_DAYS"))

        self.valkey_service = Valkey(
            host=EnvTools.get_service_ip("valkey"),
            port=int(EnvTools.get_service_port("valkey")),
            decode_responses=True
        )


    def _days_to_seconds(self, days: int) -> int:
        return days * 24 * 60 * 60


    def _clamped_ttl_seconds(self, now_ts: int, mtl_ts: int) -> int:
        """
        Returns TTL = min(inactive_window, mtl - now), not < 0.
        """
        remaining = max(0, mtl_ts - now_ts)
        return min(remaining, self._days_to_seconds(self.session_inactive_days))


    def create_session(self, user_id: uuid.UUID, *,
        user_agent: str, client_id: str,
        local_system_time_zone: str, platform: str, ip: str,
    ) -> Dict[str, str]:

        sid = uuid.uuid4()
        key = f"Session:{sid}"

        now_time_stamp = TimeTools.now_time_stamp()
        mtl_time_stamp = now_time_stamp + self._days_to_seconds(self.session_max_life_days)

        dsh: str = StringTools.hash_string(
            f"{user_agent}{client_id}{local_system_time_zone}{platform}"
        )

        ish: str = StringTools.hash_string(ip)

        model = Session(
            sub=str(user_id),
            iat=now_time_stamp,
            mtl=mtl_time_stamp,
            dsh=dsh,
            ish=ish,
        )

        self.valkey_service.hset(key, mapping={k: str(v) for k, v in model.model_dump().items()})

        ttl = self._clamped_ttl_seconds(now_time_stamp, mtl_time_stamp)
        if ttl > 0:
            self.valkey_service.expire(key, ttl)
        else:
            self.valkey_service.delete(key)

        logger.debug(f"Created new session: {str(sid)} for user: {user_id}")

        return {
            "session_id": str(sid),
            "iat": str(now_time_stamp),
            "mtl": str(mtl_time_stamp),
        }


    def touch_session(self, session_id: str) -> bool:
        sess = self.get_session(session_id)

        if not sess:
            return False

        now_ts = TimeTools.now_time_stamp()
        ttl = self._clamped_ttl_seconds(now_ts, sess.mtl)

        if ttl <= 0:
            self.valkey_service.delete(f"Session:{session_id}")
            return False

        self.valkey_service.expire(f"Session:{session_id}", ttl)
        logger.debug(f"Touched session: {session_id}")
        return True


    def delete_session(self, session_id: str) -> None:
        session_key = f"Session:{session_id}"
        self.valkey_service.delete(session_key)


    def is_session_exists(self, session_id: str) -> bool:
         return self.get_session(session_id) is not None


    def get_session(self, session_id: str) -> Optional[Session]:
        session_key = f"Session:{session_id}"
        data = self.valkey_service.hgetall(session_key)
        if not data:
            return None
        try:
            dto_session = self.validate_session(data)
            if isinstance(dto_session, list):
                return dto_session[0] if dto_session else None
            return dto_session
            
        except Exception as ex:
            logger.warning(f"Session {session_id} failed validation: {ex}")
            return None


    def validate_session(self, raw: Any) -> Optional[Session]:
        if raw is None:
            return None
        obj = SimpleNamespace(**raw) if isinstance(raw, Mapping) else raw
        dto = ValidatingTools.validate_models_by_schema(obj, Session)
        return dto if not isinstance(dto, list) else (dto[0] if dto else None)


    def get_test_dsh(self) -> Dict[str, str]:
        return {
            "user_agent": "bla_bla",
            "client_id": "bla_bla",
            "local_system_time_zone": "bla_bla",
            "platform": "bla_bla",
        }


    def get_test_client_ip(self) -> str:
       return "192.168.0.1"
        

        