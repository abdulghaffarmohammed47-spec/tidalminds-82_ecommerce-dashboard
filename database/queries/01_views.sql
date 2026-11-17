-- ============================================================================
-- SMARTCOMMERCE AI: DATABASE VIEWS
-- File: database/queries/01_views.sql
-- Purpose: Pre-defined views encapsulating complex joins for common query
--          patterns. Views simplify application queries and enforce
--          consistent data presentation logic at the database layer.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- VIEW 1: v_product_catalog
-- Purpose: Full product card view joining products, inventory stock,
--          category names. Used by the storefront listing and search results.
--          Demonstrates: Multi-table JOIN, Aggregation with GROUP BY.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_product_catalog AS
SELECT
    p.id                                                    AS product_id,
    p.sku,
    p.title,
    p.slug,
    p.brand,
    p.base_price,
    p.compare_at_price,
    p.rating_avg,
    p.review_count,
    p.is_active,
    p.created_at,
    c.id                                                    AS category_id,
    c.name                                                  AS category_name,
    c.slug                                                  AS category_slug,
    COALESCE(SUM(GREATEST(i.on_hand - i.reserved, 0)), 0)  AS available_stock,
    COALESCE(SUM(i.on_hand), 0)                            AS total_on_hand,
    COALESCE(SUM(i.reserved), 0)                           AS total_reserved,
    COUNT(pv.id)                                            AS variant_count,
    CASE
        WHEN COALESCE(SUM(GREATEST(i.on_hand - i.reserved, 0)), 0) > 0
        THEN TRUE ELSE FALSE
    END                                                     AS is_in_stock
FROM
    products p
    JOIN categories c         ON p.category_id = c.id
    LEFT JOIN product_variants pv ON p.id = pv.product_id AND pv.is_active = TRUE
    LEFT JOIN inventory i     ON pv.id = i.variant_id
WHERE
    p.is_active = TRUE
GROUP BY
    p.id, p.sku, p.title, p.slug, p.brand,
    p.base_price, p.compare_at_price, p.rating_avg, p.review_count,
    p.is_active, p.created_at,
    c.id, c.name, c.slug;

COMMENT ON VIEW v_product_catalog IS
'Unified product catalog view: joins products with live inventory stock counts
 and category metadata. Used by storefront listing and search endpoints.';


-- ----------------------------------------------------------------------------
-- VIEW 2: v_low_stock_alerts
-- Purpose: Identifies variant inventory records that have fallen at or below
--          the safety_stock threshold. Used by the Admin dashboard.
--          Demonstrates: Filtering with computed column, JOIN, CASE expression.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_low_stock_alerts AS
SELECT
    i.id                                    AS inventory_id,
    i.variant_id,
    pv.sku                                  AS variant_sku,
    pv.title                                AS variant_title,
    p.id                                    AS product_id,
    p.title                                 AS product_title,
    p.sku                                   AS product_sku,
    c.name                                  AS category_name,
    i.on_hand,
    i.reserved,
    (i.on_hand - i.reserved)               AS available_stock,
    i.safety_stock,
    CASE
        WHEN (i.on_hand - i.reserved) <= 0              THEN 'OUT_OF_STOCK'
        WHEN (i.on_hand - i.reserved) <= i.safety_stock THEN 'LOW_STOCK'
        ELSE 'HEALTHY'
    END                                     AS stock_status,
    (i.safety_stock - (i.on_hand - i.reserved)) AS units_needed_to_restock
FROM
    inventory i
    JOIN product_variants pv ON i.variant_id = pv.id
    JOIN products p          ON pv.product_id = p.id
    JOIN categories c        ON p.category_id = c.id
WHERE
    (i.on_hand - i.reserved) <= i.safety_stock
    AND p.is_active = TRUE
ORDER BY
    (i.on_hand - i.reserved) ASC;

COMMENT ON VIEW v_low_stock_alerts IS
'Alert view for inventory management: surfaces all variants at or below their
 safety stock threshold with urgency classification and restock quantities.';


-- ----------------------------------------------------------------------------
-- VIEW 3: v_revenue_by_category
-- Purpose: Aggregates confirmed order revenue by product category.
--          Demonstrates: Multi-table JOIN, GROUP BY, SUM aggregation,
--          filtering on ENUM status.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_revenue_by_category AS
SELECT
    c.id                                    AS category_id,
    c.name                                  AS category_name,
    COUNT(DISTINCT o.id)                   AS total_orders,
    COUNT(oi.id)                            AS total_line_items,
    SUM(oi.quantity)                        AS total_units_sold,
    SUM(oi.unit_price * oi.quantity)       AS gross_revenue,
    AVG(oi.unit_price * oi.quantity)       AS avg_line_item_value,
    MAX(o.created_at)                       AS last_order_at
FROM
    order_items oi
    JOIN product_variants pv ON oi.variant_id = pv.id
    JOIN products p          ON pv.product_id = p.id
    JOIN categories c        ON p.category_id = c.id
    JOIN orders o            ON oi.order_id = o.id
WHERE
    o.status IN ('CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED')
GROUP BY
    c.id, c.name
ORDER BY
    gross_revenue DESC;

COMMENT ON VIEW v_revenue_by_category IS
'Revenue analytics view: aggregates gross sales, unit volumes, and order counts
 per product category for confirmed/fulfilled orders only.';


-- ----------------------------------------------------------------------------
-- VIEW 4: v_order_summary
-- Purpose: Flattened order view with customer name, item count, and total.
--          Used by Admin order management and customer order history pages.
--          Demonstrates: Subquery in FROM, JOIN, COUNT aggregation.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_order_summary AS
SELECT
    o.id                                    AS order_id,
    o.status,
    o.total_amount,
    o.created_at,
    o.shipping_address,
    u.id                                    AS customer_id,
    u.full_name                             AS customer_name,
    u.email                                 AS customer_email,
    COUNT(oi.id)                            AS total_line_items,
    SUM(oi.quantity)                        AS total_units,
    COALESCE(MAX(ship.tracking_number), 'Not Shipped')  AS tracking_number
FROM
    orders o
    JOIN users u                ON o.user_id = u.id
    LEFT JOIN order_items oi   ON o.id = oi.order_id
    LEFT JOIN shipments ship   ON o.id = ship.order_id
GROUP BY
    o.id, o.status, o.total_amount, o.created_at, o.shipping_address,
    u.id, u.full_name, u.email
ORDER BY
    o.created_at DESC;

COMMENT ON VIEW v_order_summary IS
'Order management view: flattens orders with customer identity, item counts,
 totals, and tracking numbers for the admin dashboard.';


-- ----------------------------------------------------------------------------
-- VIEW 5: v_customer_lifetime_value
-- Purpose: Computes total spend, order count, and avg order value per customer.
--          Demonstrates: Window functions, aggregation, HAVING clause.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_customer_lifetime_value AS
SELECT
    u.id                                    AS customer_id,
    u.full_name,
    u.email,
    u.created_at                            AS member_since,
    COUNT(o.id)                             AS total_orders,
    COALESCE(SUM(o.total_amount), 0)       AS lifetime_value,
    COALESCE(AVG(o.total_amount), 0)       AS avg_order_value,
    MAX(o.created_at)                       AS last_order_at,
    EXTRACT(DAY FROM NOW() - u.created_at) AS days_since_join
FROM
    users u
    LEFT JOIN orders o ON u.id = o.user_id
        AND o.status NOT IN ('CANCELLED')
GROUP BY
    u.id, u.full_name, u.email, u.created_at
ORDER BY
    lifetime_value DESC;

COMMENT ON VIEW v_customer_lifetime_value IS
'Customer analytics view: computes lifetime value, order frequency, and
 average order value per customer. Useful for segmentation and CRM.';


-- ----------------------------------------------------------------------------
-- VIEW 6: v_semantic_search_ready_products
-- Purpose: Joins products eligible for vector search (active, in-stock, 
--          has embedding). This is the core pgvector query source.
--          Demonstrates: Hybrid AI + relational query readiness.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_semantic_search_ready_products AS
SELECT
    p.id                                    AS product_id,
    p.title,
    p.slug,
    p.brand,
    p.base_price,
    p.rating_avg,
    c.name                                  AS category_name,
    pe.embedding,
    COALESCE(SUM(GREATEST(i.on_hand - i.reserved, 0)), 0)  AS available_stock
FROM
    products p
    JOIN product_embeddings pe ON p.id = pe.product_id
    JOIN categories c          ON p.category_id = c.id
    JOIN product_variants pv   ON p.id = pv.product_id AND pv.is_active = TRUE
    JOIN inventory i           ON pv.id = i.variant_id
WHERE
    p.is_active = TRUE
GROUP BY
    p.id, p.title, p.slug, p.brand, p.base_price, p.rating_avg, c.name, pe.embedding
HAVING
    COALESCE(SUM(GREATEST(i.on_hand - i.reserved, 0)), 0) > 0;

COMMENT ON VIEW v_semantic_search_ready_products IS
'pgvector search source view: only in-stock, active products with embeddings.
 Enables transaction-safe semantic search: similarity AND stock check in one query.';
