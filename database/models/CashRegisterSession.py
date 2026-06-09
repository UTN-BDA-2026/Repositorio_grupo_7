# CREATE TABLE public.cash_register_sessions (
#     id uuid NOT NULL,
#     branch_id uuid NOT NULL,
#     user_id uuid NOT NULL,
#     opening_amount numeric(12,2) DEFAULT '0'::numeric NOT NULL,
#     closing_amount numeric(12,2),
#     status character varying(255) DEFAULT 'open'::character varying NOT NULL,
#     notes text,
#     opened_at timestamp(0) without time zone NOT NULL,
#     closed_at timestamp(0) without time zone,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone,
#     CONSTRAINT cash_register_sessions_status_check CHECK (((status)::text = ANY ((ARRAY['open'::character varying, 'closed'::character varying])::text[])))
# );

import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class CashRegisterSession(Base):
    __tablename__ = "cash_register_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    opening_amount = Column(Numeric(12, 2), nullable=False, default=0)
    closing_amount = Column(Numeric(12, 2), nullable=True)
    
    status = Column(String(255), nullable=False, default="open")
    notes = Column(Text, nullable=True)
    
    opened_at = Column(DateTime, nullable=False, default=func.now())
    closed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('open', 'closed')", name="cash_register_sessions_status_check"),
    )

    branch = relationship("Branch")
    user = relationship("User")     