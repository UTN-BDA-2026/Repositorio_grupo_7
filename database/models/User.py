

# CREATE TABLE public.users (
    # id uuid NOT NULL,
    # name character varying(255) NOT NULL,
    # email character varying(255) NOT NULL,
    # email_verified_at timestamp(0) without time zone,
    # password character varying(255) NOT NULL,
    # branch_id uuid,
    # pos_pin character varying(255),
    # remember_token character varying(100),
    # created_at timestamp(0) without time zone,
    # updated_at timestamp(0) without time zone,
    # deleted_at timestamp(0) without time zone
# );

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    email_verified_at = Column(DateTime, nullable=True)
    password = Column(String(255), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    pos_pin = Column(String(255), nullable=True)
    remember_token = Column(String(100))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    branch = relationship("Branch")
    

