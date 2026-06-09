from database.db import Base
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# CREATE TABLE public.brands (
#     id uuid NOT NULL,
#     name character varying(255) NOT NULL,
#     slug character varying(255) NOT NULL,
#     description text,
#     is_active boolean DEFAULT true NOT NULL,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone,
#     deleted_at timestamp(0) without time zone
# );

class Brand(Base):
    __tablename__= "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

