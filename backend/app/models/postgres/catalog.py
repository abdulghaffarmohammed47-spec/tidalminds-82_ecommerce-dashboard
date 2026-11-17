import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.postgres import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

class Brand(Base):
    __tablename__ = "brands"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False)
    description = Column(String, nullable=True)
    attributes = Column(JSONB, default={}, server_default='{}', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('ix_products_attributes', attributes, postgresql_using='gin'),
    )
    
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    attributes = Column(JSONB, default={}, server_default='{}', nullable=False)
    
    __table_args__ = (
        Index('ix_product_variants_attributes', attributes, postgresql_using='gin'),
    )
    
    product = relationship("Product", back_populates="variants")

class Seller(Base):
    __tablename__ = "sellers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class SellerOffer(Base):
    __tablename__ = "seller_offers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    price = Column(Integer, nullable=False) # minor units (paise)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('seller_id', 'variant_id', name='uq_seller_variant_offer'),
    )
