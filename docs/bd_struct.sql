--
-- PostgreSQL database dump
-- Sistema de Ventas (SisVentas) - Estructura limpia para TP
--
-- Dumped from database version 18.4
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';
SET default_table_access_method = heap;


-- ============================================================
--  TABLAS MAESTRAS (catálogos y configuración)
-- ============================================================

CREATE TABLE public.taxes (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    rate numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.taxes OWNER TO sail;


CREATE TABLE public.brands (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.brands OWNER TO sail;


CREATE TABLE public.categories (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.categories OWNER TO sail;


CREATE TABLE public.payment_methods (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    surcharge_percentage numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.payment_methods OWNER TO sail;


-- ============================================================
--  SUCURSALES Y USUARIOS
-- ============================================================

CREATE TABLE public.branches (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address character varying(255),
    phone character varying(255),
    is_active boolean DEFAULT true NOT NULL,
    activation_code character varying(20),
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.branches OWNER TO sail;


CREATE TABLE public.users (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    email_verified_at timestamp(0) without time zone,
    password character varying(255) NOT NULL,
    branch_id uuid,
    pos_pin character varying(255),
    remember_token character varying(100),
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.users OWNER TO sail;


-- ============================================================
--  PRODUCTOS E INVENTARIO
-- ============================================================

CREATE TABLE public.products (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    sku character varying(255) NOT NULL,
    barcode character varying(255),
    sale_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    cost_price numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    image_url character varying(255),
    price_includes_tax boolean DEFAULT false NOT NULL,
    min_stock numeric(12,3) DEFAULT '0'::numeric NOT NULL,
    max_stock numeric(12,3) DEFAULT '0'::numeric NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    category_id uuid,
    brand_id uuid,
    tax_id uuid NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.products OWNER TO sail;


CREATE TABLE public.branch_product (
    branch_id uuid NOT NULL,
    product_id uuid NOT NULL,
    stock numeric(12,3) DEFAULT '0'::numeric NOT NULL,
    alert_stock numeric(12,3) DEFAULT '5'::numeric NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);

ALTER TABLE public.branch_product OWNER TO sail;


CREATE TABLE public.inventory_movements (
    id uuid NOT NULL,
    product_id uuid NOT NULL,
    branch_id uuid NOT NULL,
    user_id uuid,
    type character varying(255) NOT NULL,
    quantity integer NOT NULL,
    reason character varying(255) NOT NULL,
    reference_id uuid,
    notes text,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);

ALTER TABLE public.inventory_movements OWNER TO sail;


CREATE TABLE public.suppliers (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    tax_id character varying(255),
    email character varying(255),
    phone character varying(255),
    address text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.suppliers OWNER TO sail;


-- ============================================================
--  CLIENTES
-- ============================================================

CREATE TABLE public.clients (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    document_type character varying(255),
    document_number character varying(255),
    email character varying(255),
    phone character varying(255),
    address text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    deleted_at timestamp(0) without time zone
);

ALTER TABLE public.clients OWNER TO sail;


-- ============================================================
--  VENTAS Y CAJA
-- ============================================================

CREATE TABLE public.cash_register_sessions (
    id uuid NOT NULL,
    branch_id uuid NOT NULL,
    user_id uuid NOT NULL,
    opening_amount numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    closing_amount numeric(12,2),
    status character varying(255) DEFAULT 'open'::character varying NOT NULL,
    notes text,
    opened_at timestamp(0) without time zone NOT NULL,
    closed_at timestamp(0) without time zone,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone,
    CONSTRAINT cash_register_sessions_status_check CHECK (((status)::text = ANY ((ARRAY['open'::character varying, 'closed'::character varying])::text[])))
);

ALTER TABLE public.cash_register_sessions OWNER TO sail;


CREATE TABLE public.sales (
    id uuid NOT NULL,
    branch_id uuid,
    user_id uuid,
    client_id uuid,
    session_id uuid,
    payment_method_id uuid,
    total_amount numeric(12,2) NOT NULL,
    synced_at timestamp(0) without time zone,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);

ALTER TABLE public.sales OWNER TO sail;


CREATE TABLE public.sale_details (
    id uuid NOT NULL,
    sale_id uuid NOT NULL,
    product_id uuid NOT NULL,
    quantity numeric(12,3) NOT NULL,
    unit_price numeric(12,2) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);

ALTER TABLE public.sale_details OWNER TO sail;


-- ============================================================
--  COMPRAS A PROVEEDORES
-- ============================================================

CREATE TABLE public.purchases (
    id uuid NOT NULL,
    branch_id uuid NOT NULL,
    user_id uuid NOT NULL,
    supplier_id uuid NOT NULL,
    total_amount numeric(12,2) NOT NULL,
    status character varying(255) DEFAULT 'completed'::character varying NOT NULL,
    notes text,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);

ALTER TABLE public.purchases OWNER TO sail;


CREATE TABLE public.purchase_details (
    id uuid NOT NULL,
    purchase_id uuid NOT NULL,
    product_id uuid NOT NULL,
    quantity numeric(12,3) NOT NULL,
    unit_cost numeric(12,2) NOT NULL,
    created_at timestamp(0) without time zone,
    updated_at timestamp(0) without time zone
);

ALTER TABLE public.purchase_details OWNER TO sail;


-- ============================================================
--  CLAVES PRIMARIAS
-- ============================================================

ALTER TABLE ONLY public.taxes                ADD CONSTRAINT taxes_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.brands               ADD CONSTRAINT brands_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.categories           ADD CONSTRAINT categories_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.payment_methods      ADD CONSTRAINT payment_methods_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.branches             ADD CONSTRAINT branches_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.users                ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.products             ADD CONSTRAINT products_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.inventory_movements  ADD CONSTRAINT inventory_movements_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.suppliers            ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.clients              ADD CONSTRAINT clients_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.cash_register_sessions ADD CONSTRAINT cash_register_sessions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.sales                ADD CONSTRAINT sales_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.sale_details         ADD CONSTRAINT sale_details_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.purchases            ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.purchase_details     ADD CONSTRAINT purchase_details_pkey PRIMARY KEY (id);


-- ============================================================
--  RESTRICCIONES DE UNICIDAD
-- ============================================================

ALTER TABLE ONLY public.branches        ADD CONSTRAINT branches_activation_code_unique UNIQUE (activation_code);
ALTER TABLE ONLY public.brands          ADD CONSTRAINT brands_slug_unique UNIQUE (slug);
ALTER TABLE ONLY public.clients         ADD CONSTRAINT clients_document_number_unique UNIQUE (document_number);
ALTER TABLE ONLY public.clients         ADD CONSTRAINT clients_email_unique UNIQUE (email);
ALTER TABLE ONLY public.payment_methods ADD CONSTRAINT payment_methods_name_unique UNIQUE (name);
ALTER TABLE ONLY public.products        ADD CONSTRAINT products_sku_unique UNIQUE (sku);
ALTER TABLE ONLY public.suppliers       ADD CONSTRAINT suppliers_email_unique UNIQUE (email);
ALTER TABLE ONLY public.suppliers       ADD CONSTRAINT suppliers_tax_id_unique UNIQUE (tax_id);
ALTER TABLE ONLY public.users           ADD CONSTRAINT users_email_unique UNIQUE (email);
ALTER TABLE ONLY public.branch_product  ADD CONSTRAINT branch_product_branch_id_product_id_unique UNIQUE (branch_id, product_id);


-- ============================================================
--  ÍNDICES
--  NOTA: Los índices se agregarán más adelante de forma
--  intencional para documentar la diferencia de rendimiento
--  con EXPLAIN ANALYZE (antes y después).
-- ============================================================


-- ============================================================
--  CLAVES FORÁNEAS
-- ============================================================

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_branch_id_foreign FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_foreign FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_brand_id_foreign FOREIGN KEY (brand_id) REFERENCES public.brands(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_tax_id_foreign FOREIGN KEY (tax_id) REFERENCES public.taxes(id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.branch_product
    ADD CONSTRAINT branch_product_branch_id_foreign FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.branch_product
    ADD CONSTRAINT branch_product_product_id_foreign FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_branch_id_foreign FOREIGN KEY (branch_id) REFERENCES public.branches(id);

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_product_id_foreign FOREIGN KEY (product_id) REFERENCES public.products(id);

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.cash_register_sessions
    ADD CONSTRAINT cash_register_sessions_branch_id_foreign FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.cash_register_sessions
    ADD CONSTRAINT cash_register_sessions_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_branch_id_foreign FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_client_id_foreign FOREIGN KEY (client_id) REFERENCES public.clients(id);

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_payment_method_id_foreign FOREIGN KEY (payment_method_id) REFERENCES public.payment_methods(id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_session_id_foreign FOREIGN KEY (session_id) REFERENCES public.cash_register_sessions(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.sale_details
    ADD CONSTRAINT sale_details_sale_id_foreign FOREIGN KEY (sale_id) REFERENCES public.sales(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.sale_details
    ADD CONSTRAINT sale_details_product_id_foreign FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_branch_id_foreign FOREIGN KEY (branch_id) REFERENCES public.branches(id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_supplier_id_foreign FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE RESTRICT;

ALTER TABLE ONLY public.purchase_details
    ADD CONSTRAINT purchase_details_purchase_id_foreign FOREIGN KEY (purchase_id) REFERENCES public.purchases(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.purchase_details
    ADD CONSTRAINT purchase_details_product_id_foreign FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT;


-- ============================================================
--  FIN DEL DUMP
-- ============================================================
