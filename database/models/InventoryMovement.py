# CREATE TABLE public.inventory_movements (
#     id uuid NOT NULL,
#     product_id uuid NOT NULL,
#     branch_id uuid NOT NULL,
#     user_id uuid,
#     type character varying(255) NOT NULL,
#     quantity integer NOT NULL,
#     reason character varying(255) NOT NULL,
#     reference_id uuid,
#     notes text,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone
# );

import uuid

from sqlalchemy import UUID, Column, DateTime, Integer, String, Text, func, ForeignKey

from database.db import Base

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    type = Column("type", String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    