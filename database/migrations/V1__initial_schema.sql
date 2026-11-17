-- ============================================================================
-- MIGRATION V1: INITIAL SCHEMA
-- File   : database/migrations/V1__initial_schema.sql
-- Date   : 2026-09-01
-- Author : SmartCommerce AI Team
-- Purpose: Baseline PostgreSQL schema — creates all core tables, enums,
--          extensions, and primary indexes from scratch.
--          This migration establishes the foundation of the system.
-- ============================================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation functions
CREATE EXTENSION IF NOT EXISTS "vector";         -- pgvector for AI embeddings
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Trigram similarity for fuzzy text search

-- ============================================================================
-- ENUM TYPES (ensures only valid status strings are stored)
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('CUSTOMER', 'SELLER', 'ADMIN');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_status AS ENUM (
        'PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'
    );
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE movement_type AS ENUM (
        'ORDER_RESERVATION', 'ORDER_FULFILLED', 'RESTOCK', 'RETURN_RESTOCK', 'MANUAL_ADJUST'
    );
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM (
        'PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'
    );
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE shipment_status AS ENUM (
        'PREPARING', 'DISPATCHED', 'IN_TRANSIT', 'DELIVERED', 'RETURNED'
    );
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- ============================================================================
-- TABLE 1: users
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(150) NOT NULL DEFAULT '',
    role            user_role   NOT NULL DEFAULT 'CUSTOMER',
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_users_email     ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role      ON users(role);

-- ============================================================================
-- TABLE 2: categories  (self-referential hierarchy)
-- ============================================================================
CREATE TABLE IF NOT EXISTS categories (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(120) UNIQUE NOT NULL,
    parent_id   UUID        REFERENCES categories(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_categories_slug   ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);

-- ============================================================================
-- TABLE 3: products
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    id                  UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku                 VARCHAR(64)     UNIQUE NOT NULL,
    title               VARCHAR(255)    NOT NULL,
    slug                VARCHAR(280)    UNIQUE NOT NULL,
    category_id         UUID            NOT NULL REFERENCES categories(id),
    brand               VARCHAR(100)    NOT NULL DEFAULT '',
    base_price          NUMERIC(12,2)   NOT NULL CHECK (base_price >= 0),
    compare_at_price    NUMERIC(12,2)   CHECK (compare_at_price IS NULL OR compare_at_price >= base_price),
    has_360_view        BOOLEAN         NOT NULL DEFAULT FALSE,
    has_video           BOOLEAN         NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    rating_avg          NUMERIC(3,2)    NOT NULL DEFAULT 0.00 CHECK (rating_avg BETWEEN 0.00 AND 5.00),
    review_count        INTEGER         NOT NULL DEFAULT 0 CHECK (review_count >= 0),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_products_category  ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_slug      ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_sku       ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_active    ON products(is_active, created_at DESC) WHERE is_active = TRUE;

-- ============================================================================
-- TABLE 4: product_variants  (size, color, storage options, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_variants (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id      UUID        NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku             VARCHAR(80) UNIQUE NOT NULL,
    title           VARCHAR(150) NOT NULL,
    price_override  NUMERIC(12,2),
    attributes      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_variants_product ON product_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_attributes ON product_variants USING GIN (attributes);

-- ============================================================================
-- TABLE 5: product_embeddings  (pgvector — 384-dim all-MiniLM-L6-v2)
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_embeddings (
    product_id  UUID        PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    embedding   vector(384) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_product_embeddings_hnsw
    ON product_embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================================
-- TABLE 6: inventory  (stock balances with strict integrity)
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory (
    id              UUID    PRIMARY KEY DEFAULT uuid_generate_v4(),
    variant_id      UUID    UNIQUE NOT NULL REFERENCES product_variants(id) ON DELETE CASCADE,
    on_hand         INTEGER NOT NULL DEFAULT 0,
    reserved        INTEGER NOT NULL DEFAULT 0,
    safety_stock    INTEGER NOT NULL DEFAULT 2,
    CONSTRAINT chk_stock_validity   CHECK (on_hand >= reserved),
    CONSTRAINT chk_positive_counts  CHECK (on_hand >= 0 AND reserved >= 0)
);

-- ============================================================================
-- TABLE 7: inventory_movements  (audit ledger)
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory_movements (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    variant_id      UUID            NOT NULL REFERENCES product_variants(id),
    change_qty      INTEGER         NOT NULL,
    movement_type   movement_type   NOT NULL,
    reference_id    VARCHAR(100),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_variant ON inventory_movements(variant_id, created_at DESC);

-- ============================================================================
-- TABLE 8: orders
-- ============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id               UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID          NOT NULL REFERENCES users(id),
    status           order_status  NOT NULL DEFAULT 'PENDING',
    total_amount     NUMERIC(12,2) NOT NULL CHECK (total_amount > 0),
    shipping_address JSONB         NOT NULL DEFAULT '{}'::jsonb,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_orders_user    ON orders(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status  ON orders(status, created_at DESC);

-- ============================================================================
-- TABLE 9: order_items
-- ============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id          UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id    UUID            NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    variant_id  UUID            NOT NULL REFERENCES product_variants(id),
    unit_price  NUMERIC(12,2)  NOT NULL CHECK (unit_price >= 0),
    quantity    INTEGER         NOT NULL CHECK (quantity > 0)
);
CREATE INDEX IF NOT EXISTS idx_order_items_order   ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_variant ON order_items(variant_id);

-- ============================================================================
-- TABLE 10: order_status_history  (state machine audit)
-- ============================================================================
CREATE TABLE IF NOT EXISTS order_status_history (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id    UUID        NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    old_status  TEXT,
    new_status  TEXT        NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by  TEXT        NOT NULL DEFAULT 'SYSTEM'
);
CREATE INDEX IF NOT EXISTS idx_order_status_history_order ON order_status_history(order_id);

-- ============================================================================
-- TABLE 11: user_search_history  (personalization & recommendations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_search_history (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID        REFERENCES users(id) ON DELETE CASCADE,
    session_id          VARCHAR(100) NOT NULL,
    raw_query           TEXT        NOT NULL,
    extracted_category  VARCHAR(100),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_search_history_user ON user_search_history(user_id, created_at DESC);

-- ============================================================================
-- TABLE 12: notifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title               VARCHAR(200) NOT NULL,
    message             TEXT        NOT NULL,
    notification_type   VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    is_read             BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- ============================================================================
-- TABLE 13: payments
-- ============================================================================
CREATE TABLE IF NOT EXISTS payments (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id        UUID            NOT NULL REFERENCES orders(id),
    amount          NUMERIC(12,2)   NOT NULL,
    status          payment_status  NOT NULL DEFAULT 'PENDING',
    provider        VARCHAR(50)     NOT NULL DEFAULT 'mock',
    transaction_id  VARCHAR(200),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABLE 14: shipments
-- ============================================================================
CREATE TABLE IF NOT EXISTS shipments (
    id                  UUID                PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id            UUID                NOT NULL REFERENCES orders(id),
    status              shipment_status     NOT NULL DEFAULT 'PREPARING',
    tracking_number     VARCHAR(100),
    carrier             VARCHAR(100),
    estimated_delivery  TIMESTAMPTZ,
    shipped_at          TIMESTAMPTZ,
    delivered_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_shipments_order ON shipments(order_id);

-- ============================================================================
-- SCHEMA VERSION TRACKING TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     VARCHAR(50) PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT
);

INSERT INTO schema_migrations (version, description)
VALUES ('V1', 'Initial schema: all core tables, enums, extensions, indexes')
ON CONFLICT (version) DO NOTHING;
