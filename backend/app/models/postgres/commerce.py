import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.postgres import Base

class Cart(Base):
    __tablename__ = "carts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    seller_offer_id = Column(UUID(as_uuid=True), ForeignKey("seller_offers.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String, nullable=False)
    total_amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    seller_orders = relationship("SellerOrder", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")

class SellerOrder(Base):
    __tablename__ = "seller_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String, nullable=False)
    subtotal = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="seller_orders")
    items = relationship("OrderItem", back_populates="seller_order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_order_id = Column(UUID(as_uuid=True), ForeignKey("seller_orders.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False)
    snapshot_price = Column(Integer, nullable=False)
    snapshot_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    seller_order = relationship("SellerOrder", back_populates="items")

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    order = relationship("Order", back_populates="status_history")

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    usage_limit = Column(Integer, nullable=False)
    per_user_limit = Column(Integer, nullable=False)
    discount_type = Column(String, nullable=False, default="PERCENTAGE")
    discount_value = Column(Integer, nullable=False, default=0)
    min_order_amount = Column(Integer, nullable=False, default=0)
    max_discount_amount = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('coupon_id', 'user_id', name='uq_coupon_user'),
    )
