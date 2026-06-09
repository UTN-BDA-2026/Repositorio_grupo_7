# CREATE TABLE public.sale_details (
#     id uuid NOT NULL,
#     sale_id uuid NOT NULL,
#     product_id uuid NOT NULL,
#     quantity numeric(12,3) NOT NULL,
#     unit_price numeric(12,2) NOT NULL,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone
# );

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class SaleDetail(Base):
    __tablename__ = "sale_details"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    sale = relationship("Sale")
    product = relationship("Product")
    
    