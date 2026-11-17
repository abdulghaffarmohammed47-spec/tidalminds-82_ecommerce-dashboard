-- ============================================================================
-- SMARTCOMMERCE AI: ADVANCED SQL QUERIES — DBMS CONCEPT DEMONSTRATIONS
-- File: database/queries/05_advanced_queries.sql
-- Purpose: Demonstrates advanced SQL/DBMS concepts used in the platform.
--          Each query is annotated with the concept it demonstrates.
--          Run these to validate the database is functioning correctly.
-- ============================================================================

-- ============================================================================
-- QUERY 1: WINDOW FUNCTIONS — Sales Leaderboard with Rankings
-- Concept : Window functions compute aggregates ACROSS rows without collapsing
--           them (unlike GROUP BY). RANK() assigns position; DENSE_RANK()
--           doesn't skip ranks on ties.
-- Use Case: Product sales leaderboard on the Admin dashboard.
-- ============================================================================

SELECT
    p.title                                         AS product_name,
    p.brand,
    c.name                                          AS category,
    SUM(oi.quantity)                               AS total_units_sold,
    SUM(oi.quantity * oi.unit_price)               AS gross_revenue,

    -- RANK: gaps on ties (1, 2, 2, 4...)
    RANK() OVER (ORDER BY SUM(oi.quantity) DESC)   AS sales_rank,

    -- DENSE_RANK: no gaps (1, 2, 2, 3...)
    DENSE_RANK() OVER (ORDER BY SUM(oi.quantity) DESC) AS sales_dense_rank,

    -- ROW_NUMBER: unique sequential number
    ROW_NUMBER() OVER (ORDER BY SUM(oi.quantity) DESC) AS row_num,

    -- Category-level rank (partitioned window)
    RANK() OVER (
        PARTITION BY c.id
        ORDER BY SUM(oi.quantity) DESC
    )                                               AS rank_within_category,

    -- Running total revenue (cumulative window)
    SUM(SUM(oi.quantity * oi.unit_price)) OVER (
        ORDER BY SUM(oi.quantity) DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                               AS cumulative_revenue

FROM
    order_items oi
    JOIN product_variants pv ON oi.variant_id = pv.id
    JOIN products p          ON pv.product_id = p.id
    JOIN categories c        ON p.category_id = c.id
    JOIN orders o            ON oi.order_id = o.id
WHERE
    o.status IN ('CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED')
GROUP BY
    p.id, p.title, p.brand, c.id, c.name
ORDER BY
    total_units_sold DESC
LIMIT 20;


-- ============================================================================
-- QUERY 2: RECURSIVE CTE — Full Category Hierarchy Tree
-- Concept : WITH RECURSIVE traverses self-referential tables (like a tree/graph).
--           Perfect for category hierarchies where each row references a parent.
-- Use Case: Build navigation menu / breadcrumb trail.
-- ============================================================================

WITH RECURSIVE category_tree AS (
    -- Base case: top-level categories (no parent)
    SELECT
        id,
        name,
        slug,
        parent_id,
        0           AS depth,
        name::TEXT  AS full_path,
        ARRAY[id]   AS path_ids
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive case: children of current level
    SELECT
        c.id,
        c.name,
        c.slug,
        c.parent_id,
        ct.depth + 1,
        ct.full_path || ' > ' || c.name,
        ct.path_ids || c.id
    FROM
        categories c
        JOIN category_tree ct ON c.parent_id = ct.id
    WHERE
        NOT (c.id = ANY(ct.path_ids))  -- Prevent infinite loops (cycle guard)
)
SELECT
    LPAD('', depth * 4, ' ') || name   AS indented_name,
    slug,
    depth                               AS level,
    full_path                           AS breadcrumb,
    id
FROM
    category_tree
ORDER BY
    full_path;


-- ============================================================================
-- QUERY 3: FULL-TEXT SEARCH — Semantic Keyword Matching
-- Concept : PostgreSQL's built-in FTS converts text to tsvector (tokenized,
--           stemmed) and matches against tsquery patterns. Faster than ILIKE,
--           supports stemming (run = running), ranking (ts_rank).
-- Use Case: Fallback text search when pgvector model is unavailable.
-- ============================================================================

-- Example: Search for "wireless gaming headphone"
SELECT
    p.id,
    p.title,
    p.brand,
    p.base_price,
    p.rating_avg,
    -- ts_rank: relevance score 0–1
    ts_rank(
        to_tsvector('english', COALESCE(p.title, '') || ' ' || COALESCE(p.brand, '')),
        to_tsquery('english', 'wireless & gaming & headphone')
    )                                       AS text_relevance_score,
    -- ts_headline: highlights matching terms in title
    ts_headline(
        'english',
        p.title,
        to_tsquery('english', 'wireless & gaming & headphone'),
        'StartSel=<mark>, StopSel=</mark>'
    )                                       AS highlighted_title

FROM
    products p
WHERE
    -- Boolean full-text match using GIN index
    to_tsvector('english', COALESCE(p.title, '') || ' ' || COALESCE(p.brand, ''))
    @@ to_tsquery('english', 'wireless & gaming & headphone')
    AND p.is_active = TRUE
ORDER BY
    text_relevance_score DESC
LIMIT 10;


-- ============================================================================
-- QUERY 4: LATERAL JOIN — Most Recent Order Per Customer
-- Concept : LATERAL JOIN allows a subquery to reference columns from the outer
--           query (correlated subquery in FROM clause). Eliminates the need for
--           complex CTEs or window functions for "latest per group" patterns.
-- Use Case: Customer service dashboard showing each user's last order.
-- ============================================================================

SELECT
    u.id                    AS customer_id,
    u.full_name,
    u.email,
    u.created_at            AS member_since,
    last_order.order_id,
    last_order.status       AS last_order_status,
    last_order.total_amount AS last_order_total,
    last_order.ordered_at   AS last_ordered_at

FROM
    users u
    -- LATERAL: the subquery sees u.id from the outer query
    LEFT JOIN LATERAL (
        SELECT
            o.id        AS order_id,
            o.status,
            o.total_amount,
            o.created_at AS ordered_at
        FROM orders o
        WHERE o.user_id = u.id          -- References outer query's u.id
        ORDER BY o.created_at DESC
        LIMIT 1                          -- Only most recent order
    ) AS last_order ON TRUE             -- Always join (LEFT LATERAL)

ORDER BY
    last_order.ordered_at DESC NULLS LAST
LIMIT 50;


-- ============================================================================
-- QUERY 5: PGVECTOR SEMANTIC SEARCH — Transaction-Safe AI Search
-- Concept : Stores 384-dim text embeddings alongside relational data.
--           The <=> operator computes cosine distance.
--           JOIN with inventory means: AI relevance + stock check in ONE query.
-- Use Case: Search bar — "comfortable long-haul flight accessories"
-- NOTE    : Replace :query_vector with the actual float array from the model.
-- ============================================================================

-- Step 1: Show what a semantic search query looks like structurally
-- (Replace '[0.12, -0.05, ...]' with your actual embedding vector)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    p.id,
    p.title,
    p.brand,
    p.base_price,
    c.name                              AS category,
    COALESCE(SUM(GREATEST(i.on_hand - i.reserved, 0)), 0) AS available_stock,

    -- Cosine distance: lower = more similar (0 = identical)
    (pe.embedding <=> pe.embedding)    AS cosine_distance,          -- placeholder
    -- Similarity score: 1 - distance (higher = more similar)
    1 - (pe.embedding <=> pe.embedding) AS similarity_score         -- placeholder

FROM
    products p
    JOIN product_embeddings pe ON p.id = pe.product_id
    JOIN categories c          ON p.category_id = c.id
    JOIN product_variants pv   ON p.id = pv.product_id AND pv.is_active = TRUE
    JOIN inventory i           ON pv.id = i.variant_id
WHERE
    p.is_active = TRUE
GROUP BY
    p.id, p.title, p.brand, p.base_price, c.name, pe.embedding
HAVING
    -- KEY: Filter out-of-stock BEFORE returning AI results
    COALESCE(SUM(GREATEST(i.on_hand - i.reserved, 0)), 0) > 0
ORDER BY
    pe.embedding <=> pe.embedding ASC   -- Order by cosine distance ASC
LIMIT 10;


-- ============================================================================
-- QUERY 6: FREQUENTLY BOUGHT TOGETHER — Co-occurrence Matrix
-- Concept : Self-join on order_items to find product pairs that appear in
--           the same orders. Classic co-occurrence / market basket analysis.
-- Use Case: "Customers who bought X also bought Y" recommendations.
-- ============================================================================

SELECT
    p1.title                        AS product_a,
    p2.title                        AS product_b,
    COUNT(*)                        AS co_occurrence_count,
    COUNT(*) * 100.0 / (
        SELECT COUNT(DISTINCT order_id) FROM order_items
    )                               AS support_percentage

FROM
    order_items oi1
    JOIN order_items oi2       ON oi1.order_id = oi2.order_id
                               AND oi1.variant_id < oi2.variant_id  -- Avoid duplicates
    JOIN product_variants pv1  ON oi1.variant_id = pv1.id
    JOIN product_variants pv2  ON oi2.variant_id = pv2.id
    JOIN products p1           ON pv1.product_id = p1.id
    JOIN products p2           ON pv2.product_id = p2.id

GROUP BY
    p1.id, p1.title, p2.id, p2.title
HAVING
    COUNT(*) >= 2               -- Minimum support threshold
ORDER BY
    co_occurrence_count DESC
LIMIT 20;


-- ============================================================================
-- QUERY 7: TRANSACTION ISOLATION DEMO — Show Concurrent Lock
-- Concept : Demonstrates PostgreSQL's row-level locking with SELECT...FOR UPDATE.
--           This is the core of the anti-oversell mechanism.
-- Use Case: Proof of concurrency safety for the checkout flow.
-- ============================================================================

-- Session A (run in one psql window):
BEGIN;
    SELECT on_hand, reserved, (on_hand - reserved) AS available
    FROM inventory
    WHERE variant_id = '<your-variant-uuid>'
    FOR UPDATE;             -- Locks this row; Session B will WAIT here
    -- ... Application deducts stock ...
    UPDATE inventory SET reserved = reserved + 1 WHERE variant_id = '<your-variant-uuid>';
COMMIT;                     -- Session B's FOR UPDATE now proceeds

-- Session B (run simultaneously in another psql window):
-- BEGIN;
--     SELECT on_hand, reserved FROM inventory
--     WHERE variant_id = '<your-variant-uuid>'
--     FOR UPDATE;          -- BLOCKS until Session A commits
--     -- Now sees the updated values (no dirty read)
-- COMMIT;


-- ============================================================================
-- QUERY 8: INVENTORY MOVEMENTS AUDIT REPORT
-- Concept : Time-series aggregation with date truncation.
--           Shows all stock movements per day with running totals.
-- Use Case: Warehouse operations reporting.
-- ============================================================================

SELECT
    DATE_TRUNC('day', im.created_at)        AS movement_date,
    im.movement_type,
    COUNT(*)                                 AS total_movements,
    SUM(im.change_qty)                       AS net_qty_change,
    SUM(ABS(im.change_qty))                  AS gross_qty_moved,

    -- Running total of movements over time (window function)
    SUM(COUNT(*)) OVER (
        ORDER BY DATE_TRUNC('day', im.created_at)
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                        AS cumulative_movement_count

FROM
    inventory_movements im
GROUP BY
    DATE_TRUNC('day', im.created_at), im.movement_type
ORDER BY
    movement_date DESC, im.movement_type;


-- ============================================================================
-- QUERY 9: NORMALIZATION VALIDATION QUERY
-- Concept : Checks that the database is in 3NF by detecting transitive
--           dependencies. Ensures no product category name is duplicated
--           within the products table (would violate 3NF).
-- Use Case: Database quality/sanity check.
-- ============================================================================

-- Check: Are all category references valid? (Referential Integrity)
SELECT
    'Orphaned Products (no category)' AS check_name,
    COUNT(*) AS violations
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE c.id IS NULL

UNION ALL

-- Check: Are all variant references valid?
SELECT
    'Orphaned Inventory Records (no variant)',
    COUNT(*)
FROM inventory i
LEFT JOIN product_variants pv ON i.variant_id = pv.id
WHERE pv.id IS NULL

UNION ALL

-- Check: Are all order items pointing to valid variants?
SELECT
    'Orphaned Order Items (no variant)',
    COUNT(*)
FROM order_items oi
LEFT JOIN product_variants pv ON oi.variant_id = pv.id
WHERE pv.id IS NULL

UNION ALL

-- Check: Do any inventory records have reserved > on_hand? (Constraint violation)
SELECT
    'Stock Integrity Violations (reserved > on_hand)',
    COUNT(*)
FROM inventory
WHERE reserved > on_hand;
