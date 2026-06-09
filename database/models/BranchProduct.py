# CREATE TABLE public.branch_product (
#     branch_id uuid NOT NULL,
#     product_id uuid NOT NULL,
#     stock numeric(12,3) DEFAULT '0'::numeric NOT NULL,
#     alert_stock numeric(12,3) DEFAULT '5'::numeric NOT NULL,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone
# );

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class BranchProduct(Base):
    __tablename__="branch_product"
    
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    stock = Column(Numeric(12, 3), nullable= False, default=0)
    alert_stock = Column(Numeric(12, 3), nullable=False, default=5)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    branch = relationship("Branch")
    product = relationship("Product")
    