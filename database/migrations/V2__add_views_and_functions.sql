-- ============================================================================
-- MIGRATION V2: VIEWS & STORED PROCEDURES
-- File   : database/migrations/V2__add_views_and_functions.sql
-- Date   : 2026-09-05
-- Depends: V1__initial_schema.sql
-- Purpose: Adds all analytical views and business-logic stored procedures.
--          Views encapsulate complex JOINs; functions enforce transactional
--          business rules at the database layer.
-- ============================================================================

-- Apply views from queries/01_views.sql
\i '../queries/01_views.sql'

-- Apply stored procedures from queries/02_stored_procedures.sql
\i '../queries/02_stored_procedures.sql'

-- ============================================================================
-- ADDITIONAL VIEW: v_inventory_dashboard
-- Purpose: Combines inventory status with product info for admin panel.
-- ============================================================================
CREATE OR REPLACE VIEW v_inventory_dashboard AS
SELECT
    p.id                                            AS product_id,
    p.sku                                           AS product_sku,
    p.title                                         AS product_title,
    p.brand,
    c.name                                          AS category,
    pv.id                                           AS variant_id,
    pv.sku                                          AS variant_sku,
    pv.title                                        AS variant_title,
    pv.attributes,
    i.on_hand,
    i.reserved,
    (i.on_hand - i.reserved)                       AS available,
    i.safety_stock,
    CASE
        WHEN (i.on_hand - i.reserved) <= 0              THEN 'OUT_OF_STOCK'
        WHEN (i.on_hand - i.reserved) <= i.safety_stock THEN 'LOW_STOCK'
        WHEN (i.on_hand - i.reserved) <= i.safety_stock * 2 THEN 'WATCH'
        ELSE 'HEALTHY'
    END                                             AS stock_health,
    -- Last movement date
    (SELECT MAX(im.created_at) FROM inventory_movements im WHERE im.variant_id = pv.id) AS last_movement_at
FROM
    inventory i
    JOIN product_variants pv ON i.variant_id = pv.id
    JOIN products p          ON pv.product_id = p.id
    JOIN categories c        ON p.category_id = c.id
WHERE
    p.is_active = TRUE
ORDER BY
    (i.on_hand - i.reserved) ASC; -- Most critical first

-- ============================================================================
-- ADDITIONAL FUNCTION: fn_user_order_stats
-- Purpose: Returns a summary of a user's order history for profile page.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_user_order_stats(p_user_id UUID)
RETURNS TABLE (
    total_orders    BIGINT,
    total_spent     NUMERIC,
    avg_order_value NUMERIC,
    first_order_at  TIMESTAMPTZ,
    last_order_at   TIMESTAMPTZ
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(id)::BIGINT,
        COALESCE(SUM(total_amount), 0),
        COALESCE(AVG(total_amount), 0),
        MIN(created_at),
        MAX(created_at)
    FROM orders
    WHERE user_id = p_user_id
      AND status NOT IN ('CANCELLED');
END;
$$;

INSERT INTO schema_migrations (version, description)
VALUES ('V2', 'Added: product catalog view, low-stock view, revenue views, order summary views, stored procedures for order placement and cancellation, restock function')
ON CONFLICT (version) DO NOTHING;
