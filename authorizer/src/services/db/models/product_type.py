from src.services.db.models.base_model import *


class ProductType(Base):
    __tablename__ = "product_types"
    
    id: Mapped[UUIDpk]
    name: Mapped[str] = mapped_column(String(128), nullable=True)
    seller_id: Mapped[UUID] = mapped_column(ForeignKey('sellers.id'), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cost: Mapped[money]
    sale: Mapped[float] = mapped_column(Float, nullable=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey('authors.id'), nullable=False)
    date_publication: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    seller: Mapped["Seller"] = relationship("Seller", back_populates='product_types')
    author: Mapped["Author"] = relationship("Author", back_populates='product_types')
    products: Mapped[list["Product"]] = relationship("Product", back_populates='product_type')
    purchase_items: Mapped[list["PurchaseItem"]] = relationship("PurchaseItem", back_populates='product_type')
