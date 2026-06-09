# CREATE TABLE public.clients (
#     id uuid NOT NULL,
#     name character varying(255) NOT NULL,
#     document_type character varying(255),
#     document_number character varying(255),
#     email character varying(255),
#     phone character varying(255),
#     address text,
#     is_active boolean DEFAULT true NOT NULL,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone,
#     deleted_at timestamp(0) without time zone
# );

import uuid
from sqlalchemy import  Column, String, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class Client(Base):
    __tablename__="clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    document_type = Column(String(255), nullable=True)
    document_number = Column(String(255), nullable=True, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    phone = Column(String(255), nullable=True)
    address = Column(Text)
    
    is_active = Column(Boolean, nullable=False, default=True)   
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)