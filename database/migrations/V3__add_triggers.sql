-- ============================================================================
-- MIGRATION V3: TRIGGERS
-- File   : database/migrations/V3__add_triggers.sql
-- Date   : 2026-09-07
-- Depends: V1__initial_schema.sql, V2__add_views_and_functions.sql
-- Purpose: Adds all database triggers for automated auditing, integrity
--          enforcement, and event-driven notifications.
-- ============================================================================

-- Apply all triggers from queries/03_triggers.sql
\i '../queries/03_triggers.sql'

-- ============================================================================
-- ADDITIONAL TRIGGER: trg_prevent_self_referential_category
-- Purpose: Prevents a category from being set as its own parent (infinite loop).
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_prevent_category_self_ref()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.parent_id = NEW.id THEN
        RAISE EXCEPTION
            'INTEGRITY ERROR: Category cannot be its own parent. Category ID: %',
            NEW.id
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_prevent_category_self_ref ON categories;
CREATE TRIGGER trg_prevent_category_self_ref
    BEFORE INSERT OR UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION fn_prevent_category_self_ref();

-- ============================================================================
-- ADDITIONAL TRIGGER: trg_auto_create_inventory
-- Purpose: When a new product_variant is inserted, automatically creates
--          a default inventory record. Ensures every variant always has
--          an inventory row (simplifies queries — no LEFT JOIN needed).
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_auto_create_inventory()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO inventory (id, variant_id, on_hand, reserved, safety_stock)
    VALUES (gen_random_uuid(), NEW.id, 0, 0, 2)
    ON CONFLICT (variant_id) DO NOTHING;  -- Idempotent: safe to run multiple times
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_auto_create_inventory() IS
'AFTER INSERT trigger: auto-creates a zero-stock inventory record for every
 new product variant. Guarantees every variant has a corresponding inventory row.';

DROP TRIGGER IF EXISTS trg_auto_create_inventory ON product_variants;
CREATE TRIGGER trg_auto_create_inventory
    AFTER INSERT ON product_variants
    FOR EACH ROW
    EXECUTE FUNCTION fn_auto_create_inventory();

-- ============================================================================
-- ADDITIONAL TRIGGER: trg_soft_delete_guard
-- Purpose: Prevents hard-deletion of products that have associated orders.
--          Forces soft-delete (is_active = FALSE) instead.
--          Maintains referential integrity of historical data.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_guard_product_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_order_count
    FROM order_items oi
    JOIN product_variants pv ON oi.variant_id = pv.id
    WHERE pv.product_id = OLD.id;

    IF v_order_count > 0 THEN
        RAISE EXCEPTION
            'INTEGRITY ERROR: Cannot delete product "%" (ID: %) — it has % associated orders. '
            'Use soft-delete (is_active = FALSE) instead.',
            OLD.title, OLD.id, v_order_count
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    RETURN OLD;
END;
$$;

DROP TRIGGER IF EXISTS trg_guard_product_delete ON products;
CREATE TRIGGER trg_guard_product_delete
    BEFORE DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION fn_guard_product_delete();

INSERT INTO schema_migrations (version, description)
VALUES ('V3', 'Added: all triggers — updated_at auto-management, inventory audit, negative stock guard, order status history, new order notification, order item validation, category self-ref guard, auto inventory creation, product delete guard')
ON CONFLICT (version) DO NOTHING;
