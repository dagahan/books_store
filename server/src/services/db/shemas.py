from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from models import *


class UserAddDTO(Base):
    first_name: str
    middle_name: str
    email: Optional[str]
    phone: str


