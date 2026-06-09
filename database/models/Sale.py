# CREATE TABLE public.sales (
#     id uuid NOT NULL,
#     branch_id uuid,
#     user_id uuid,
#     client_id uuid,
#     session_id uuid,
#     payment_method_id uuid,
#     total_amount numeric(12,2) NOT NULL,
#     synced_at timestamp(0) without time zone,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone
# );


import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("cash_register_sessions.id", ondelete="SET NULL"), nullable=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id", ondelete="RESTRICT"), nullable=True)
    
    total_amount = Column(Numeric(12, 2), nullable=False)
    synced_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    branch = relationship("Branch")
    user = relationship("User")
    client = relationship("Client")
    session = relationship("CashRegisterSession")
    payment_method = relationship("PaymentMethod")