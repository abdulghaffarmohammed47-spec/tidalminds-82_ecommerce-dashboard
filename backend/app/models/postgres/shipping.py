import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base

class ShipmentEvent(Base):
    __tablename__ = "shipment_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_order_id = Column(UUID(as_uuid=True), ForeignKey("seller_orders.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_order_id = Column(UUID(as_uuid=True), ForeignKey("seller_orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    provider = Column(String, nullable=False, default="MOCK")
    tracking_number = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="LABEL_CREATED")
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class Return(Base):
    __tablename__ = "returns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_order_id = Column(UUID(as_uuid=True), ForeignKey("seller_orders.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String, nullable=False)
    reason = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("seller_order_id", name="uq_return_seller_order"),
    )

class ReturnItem(Base):
    __tablename__ = "return_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("returns.id", ondelete="CASCADE"), nullable=False)
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
