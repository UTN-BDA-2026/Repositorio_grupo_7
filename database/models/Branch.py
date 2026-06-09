from database.db import Base
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

# CREATE TABLE public.branches (
#     id uuid NOT NULL,
#     name character varying(255) NOT NULL,
#     address character varying(255),
#     phone character varying(255),
#     is_active boolean DEFAULT true NOT NULL,
#     activation_code character varying(20),
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone,
#     deleted_at timestamp(0) without time zone
# );

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    activation_code = Column(String(20), nullable=True, unique=True)    
    
    is_active = Column(Boolean, nullable=False, default=True)    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)