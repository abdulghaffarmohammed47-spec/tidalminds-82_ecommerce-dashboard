-- ============================================================================
-- SMARTCOMMERCE AI: INDEXES & CONSTRAINTS
-- File: database/queries/04_indexes_and_constraints.sql
-- Purpose: Defines all performance indexes and additional database-level
--          constraints beyond the primary schema. Indexes are critical
--          for query performance especially on large datasets.
-- ============================================================================

-- ============================================================================
-- SECTION 1: B-TREE INDEXES (Default — optimal for equality and range queries)
-- ============================================================================

-- Users: Fast lookup by email (login path — most frequent query)
CREATE INDEX IF NOT EXISTS idx_users_email
    ON users(email);

-- Users: Filter by is_active for admin user management
CREATE INDEX IF NOT EXISTS idx_users_active
    ON users(is_active)
    WHERE is_active = TRUE;  -- Partial index: only indexes active users

-- Categories: Slug lookup (URL-based routing)
CREATE INDEX IF NOT EXISTS idx_categories_slug
    ON categories(slug);

-- Categories: Parent hierarchy traversal
CREATE INDEX IF NOT EXISTS idx_categories_parent
    ON categories(parent_id)
    WHERE parent_id IS NOT NULL;

-- Products: Category filter (most common browse query)
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products(category_id);

-- Products: Slug-based product page lookup (URL routing)
CREATE INDEX IF NOT EXISTS idx_products_slug
    ON products(slug);

-- Products: Active products only — most queries filter this
CREATE INDEX IF NOT EXISTS idx_products_active
    ON products(is_active, created_at DESC)
    WHERE is_active = TRUE;

-- Products: Rating sort for bestsellers
CREATE INDEX IF NOT EXISTS idx_products_rating
    ON products(rating_avg DESC, review_count DESC)
    WHERE is_active = TRUE;

-- Products: SKU lookup (admin catalog management)
CREATE INDEX IF NOT EXISTS idx_products_sku
    ON products(sku);

-- Product Variants: Product → Variants lookup
CREATE INDEX IF NOT EXISTS idx_variants_product
    ON product_variants(product_id);

-- Product Variants: Active variants only
CREATE INDEX IF NOT EXISTS idx_variants_active
    ON product_variants(product_id, is_active)
    WHERE is_active = TRUE;

-- Inventory: Variant → Inventory (most critical join)
CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_variant_unique
    ON inventory(variant_id);

-- Inventory: Low stock alert queries (safety_stock comparison)
CREATE INDEX IF NOT EXISTS idx_inventory_low_stock
    ON inventory(variant_id, on_hand, reserved, safety_stock);

-- Orders: User order history (customer portal)
CREATE INDEX IF NOT EXISTS idx_orders_user_recency
    ON orders(user_id, created_at DESC);

-- Orders: Status-based order management (admin)
CREATE INDEX IF NOT EXISTS idx_orders_status
    ON orders(status, created_at DESC);

-- Order Items: Order detail lookup
CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON order_items(order_id);

-- Order Items: Variant co-occurrence (Frequently Bought Together)
CREATE INDEX IF NOT EXISTS idx_order_items_variant
    ON order_items(variant_id);

-- Inventory Movements: Audit trail per variant
CREATE INDEX IF NOT EXISTS idx_inventory_movements_variant_date
    ON inventory_movements(variant_id, created_at DESC);

-- User Search History: Personalization query (user + recency)
CREATE INDEX IF NOT EXISTS idx_user_search_history_user_recency
    ON user_search_history(user_id, created_at DESC);

-- ============================================================================
-- SECTION 2: HNSW VECTOR INDEX (pgvector — semantic search)
-- HNSW = Hierarchical Navigable Small World graph
-- Optimal for approximate nearest-neighbor search on high-dimensional vectors.
-- m=16: max connections per layer; ef_construction=64: build-time search width
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_product_embeddings_hnsw
    ON product_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

COMMENT ON INDEX idx_product_embeddings_hnsw IS
'HNSW approximate nearest-neighbor index on 384-dim product embeddings.
 Enables pgvector cosine distance queries in ~2-5ms vs ~500ms full scan.
 vector_cosine_ops: optimized for normalized unit vectors (all-MiniLM-L6-v2 output).';

-- ============================================================================
-- SECTION 3: GIN INDEXES (Full-text search and JSONB)
-- GIN = Generalized Inverted Index — optimal for multi-value containment queries
-- ============================================================================

-- Full-text search on product titles and brand
-- Creates a searchable tsvector from title + brand columns
CREATE INDEX IF NOT EXISTS idx_products_fulltext
    ON products
    USING GIN (
        to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(brand, ''))
    );

COMMENT ON INDEX idx_products_fulltext IS
'GIN full-text search index on product title + brand.
 Enables fast tsvector queries: WHERE to_tsvector(title) @@ to_tsquery(query)';

-- JSONB index on shipping_address for fast address querying
CREATE INDEX IF NOT EXISTS idx_orders_shipping_address
    ON orders
    USING GIN (shipping_address);

-- JSONB index on product variant attributes (size, color, etc.)
CREATE INDEX IF NOT EXISTS idx_variants_attributes
    ON product_variants
    USING GIN (attributes);

COMMENT ON INDEX idx_variants_attributes IS
'GIN index on product variant JSONB attributes.
 Enables fast queries like: WHERE attributes @> ''{"color": "red"}''';

-- ============================================================================
-- SECTION 4: COMPOSITE INDEXES (Covering indexes for multi-column queries)
-- ============================================================================

-- Composite: orders by user + status (customer order history with filter)
CREATE INDEX IF NOT EXISTS idx_orders_user_status
    ON orders(user_id, status, created_at DESC);

-- Composite: inventory movements for audit report (variant + type + date)
CREATE INDEX IF NOT EXISTS idx_movements_variant_type_date
    ON inventory_movements(variant_id, movement_type, created_at DESC);

-- ============================================================================
-- SECTION 5: ADDITIONAL CHECK CONSTRAINTS
-- (Supplement the schema-level constraints with business rule constraints)
-- ============================================================================

-- Ensure email format (basic validation at DB level)
ALTER TABLE users
    ADD CONSTRAINT chk_users_email_format
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Ensure product base_price is non-negative
ALTER TABLE products
    ADD CONSTRAINT chk_products_price_positive
    CHECK (base_price >= 0);

-- Ensure compare_at_price, when set, is >= base_price
ALTER TABLE products
    ADD CONSTRAINT chk_products_compare_price
    CHECK (compare_at_price IS NULL OR compare_at_price >= base_price);

-- Ensure order total_amount is positive
ALTER TABLE orders
    ADD CONSTRAINT chk_orders_total_positive
    CHECK (total_amount > 0);

-- Ensure rating_avg is within 0.0–5.0
ALTER TABLE products
    ADD CONSTRAINT chk_products_rating_range
    CHECK (rating_avg >= 0.00 AND rating_avg <= 5.00);

-- ============================================================================
-- SECTION 6: INDEX USAGE ANALYSIS QUERY
-- Run this after seeding data to verify indexes are being used.
-- ============================================================================
/*
-- Show all indexes on the key tables with their sizes:
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM
    pg_stat_user_indexes
WHERE
    schemaname = 'public'
ORDER BY
    tablename, indexname;

-- Check which queries use the HNSW vector index:
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.id, p.title, pe.embedding <=> '[0.1, 0.2, ...]'::vector AS distance
FROM products p
JOIN product_embeddings pe ON p.id = pe.product_id
ORDER BY distance
LIMIT 5;
*/
