import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
# pyrefly: ignore [missing-import]
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(280), unique=True, index=True, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    brand = Column(String(100), nullable=False, default="Generic")
    base_price = Column(Numeric(12, 2), nullable=False)
    compare_at_price = Column(Numeric(12, 2), nullable=True)
    has_360_view = Column(Boolean, default=True, nullable=False)
    has_video = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    rating_avg = Column(Numeric(3, 2), default=0.00, nullable=False)
    review_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    embedding_rel = relationship("ProductEmbedding", uselist=False, back_populates="product", cascade="all, delete-orphan")

    @property
    def name(self) -> str:
        """Alias title to name for backward compatibility with frontend"""
        return self.title

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = Column(String(80), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    price_override = Column(Numeric(12, 2), nullable=True)
    attributes = Column(JSONB, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)

    product = relationship("Product", back_populates="variants")
    inventory = relationship("Inventory", uselist=False, back_populates="variant", cascade="all, delete-orphan")
    inventory_movements = relationship("InventoryMovement", back_populates="variant", cascade="all, delete-orphan")

class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(Vector(384), nullable=False)

    product = relationship("Product", back_populates="embedding_rel")
