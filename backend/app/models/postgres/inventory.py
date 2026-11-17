import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.postgres import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    on_hand = Column(Integer, default=0, nullable=False)
    reserved = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        CheckConstraint('on_hand >= 0', name='chk_inventory_on_hand_positive'),
        CheckConstraint('reserved >= 0', name='chk_inventory_reserved_positive'),
        CheckConstraint('on_hand >= reserved', name='chk_inventory_on_hand_gte_reserved'),
        UniqueConstraint('variant_id', 'warehouse_id', 'seller_id', name='uq_inventory_variant_warehouse_seller'),
    )

class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # ACTIVE, COMMITTED, RELEASED, EXPIRED
    expires_at = Column(DateTime(timezone=True), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    reason = Column(String, nullable=False) # RESERVE, COMMIT, RELEASE, MANUAL_ADJUST
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
