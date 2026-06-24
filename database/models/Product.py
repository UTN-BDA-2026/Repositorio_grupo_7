
# CREATE TABLE public.products (
#     id uuid NOT NULL,
#     name character varying(255) NOT NULL,
#     description text,
#     sku character varying(255) NOT NULL,
#     barcode character varying(255),
#     sale_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
#     cost_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
#     image_url character varying(255),
#     price_includes_tax boolean DEFAULT false NOT NULL,
#     min_stock numeric(12,3) DEFAULT '0'::numeric NOT NULL,
#     max_stock numeric(12,3) DEFAULT '0'::numeric NOT NULL,
#     is_active boolean DEFAULT true NOT NULL,
#     category_id uuid,
#     brand_id uuid,
#     tax_id uuid NOT NULL,
#     created_at timestamp(0) without time zone,
#     updated_at timestamp(0) without time zone,
#     deleted_at timestamp(0) without time zone
# );

import uuid

from sqlalchemy.orm import relationship
from database.db import Base
from sqlalchemy import Column, String, Numeric, Boolean, func, ForeignKey, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID


class Product(Base):
    __tablename__ = "products"

    # SPEC-01 — Índices estratégicos:
    #  - barcode: el escaneo de código de barra es la operación más frecuente del
    #    POS y `barcode` NO es UNIQUE (no tiene índice por defecto).
    #  - name (varchar_pattern_ops): habilita usar el índice en LIKE 'prefijo%'
    #    para el autocompletado de búsqueda de productos en la UI.
    __table_args__ = (
        Index("ix_products_barcode", "barcode"),
        Index("ix_products_name_pattern", "name",
              postgresql_ops={"name": "varchar_pattern_ops"}),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(255), nullable=False, unique=True)
    barcode = Column(String(255), nullable=True)
    sale_price = Column(Numeric(12, 2), nullable=False, default=0)
    cost_price = Column(Numeric(12, 2), nullable=False, default=0)
    image_url = Column(String(255))
    price_includes_tax = Column(Boolean, nullable=False, default=False)
    min_stock = Column(Numeric(12, 3), nullable=False, default=0)
    max_stock = Column(Numeric(12, 3), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True)
    tax_id = Column(UUID(as_uuid=True), ForeignKey("taxes.id", ondelete="RESTRICT"), nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    
    category = relationship("Category")
    brand = relationship("Brand")
    tax = relationship("Tax")
    
    
    