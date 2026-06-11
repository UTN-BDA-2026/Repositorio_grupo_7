# CREATE TABLE public.purchases (
#     id uuid NOT NULL,
#     branch_id uuid NOT NULL,
#     user_id uuid NOT NULL,
#     supplier_id uuid NOT NULL,
#     total_amount numeric(12,2) NOT NULL,
#     status character varying(255) DEFAULT 'completed'::character varying NOT NULL,
#     notes text,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone
# );

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class Purchase(Base):
    __tablename__= "purchases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(255), nullable=False, default = "completed")
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    branch = relationship("Branch")
    user = relationship("User")
    supplier = relationship("Supplier")