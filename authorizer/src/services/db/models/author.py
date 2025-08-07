from src.services.db.models.base_model import *


class Author(Base):
    __tablename__ = "authors"
    
    id: Mapped[UUIDpk]
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    product_types: Mapped[list["ProductType"]] = relationship("ProductType", back_populates='author')
    