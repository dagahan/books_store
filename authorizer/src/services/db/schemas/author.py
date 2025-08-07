from .base_schema import *


class AuthorDTO(TimestampMixin):
    id: UUID = Field(...)
    name: str = Field(...)


class AuthorCreateDTO(BaseDTO):
    name: str = Field(..., min_length=1, max_length=128)


class AuthorUpdateDTO(BaseDTO):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
