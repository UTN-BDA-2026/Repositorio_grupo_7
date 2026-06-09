import uuid
from database.db import Base
from sqlalchemy import Column, String, Boolean, Numeric, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func



# id uuid NOT NULL,
#     name character varying(255) NOT NULL,
#     rate numeric(5,2) DEFAULT '0'::numeric NOT NULL,
#     is_default boolean DEFAULT false NOT NULL,
#     is_active boolean DEFAULT true NOT NULL,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone,
#     deleted_at timestamp(0) without time zone

class Tax(Base):
    __tablename__ = "taxes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  
    rate = Column(Numeric(5, 2), nullable=False,  default=0)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

