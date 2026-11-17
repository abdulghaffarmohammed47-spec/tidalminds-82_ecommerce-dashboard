-- ============================================================================
-- SMARTCOMMERCE AI: DATABASE TRIGGERS
-- File: database/queries/03_triggers.sql
-- Purpose: Automate data integrity enforcement, audit logging, and derived
--          column updates directly at the database layer — independently of
--          the application code. Triggers fire on DML events (INSERT/UPDATE).
-- ============================================================================

-- ============================================================================
-- TRIGGER 1: trg_update_user_timestamp
-- Purpose : Automatically sets `updated_at` to NOW() whenever a user row
--           is modified. Ensures timestamp accuracy without relying on the
--           application layer to remember to set it.
-- Event   : BEFORE UPDATE on users
-- Demonstrates: BEFORE trigger, auto-managed audit column.
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_set_updated_at() IS
'Generic trigger function: sets the updated_at column to the current timestamp.
 Reused across multiple tables via separate trigger bindings.';

-- Bind to users table
DROP TRIGGER IF EXISTS trg_update_user_timestamp ON users;
CREATE TRIGGER trg_update_user_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();


-- ============================================================================
-- TRIGGER 2: trg_audit_inventory_change
-- Purpose : Automatically creates an audit record in `inventory_movements`
--           whenever inventory `on_hand` or `reserved` changes.
--           Provides a complete, tamper-proof ledger of all stock movements
--           without requiring the application to manually write audit rows.
-- Event   : AFTER UPDATE on inventory
-- Demonstrates: AFTER trigger, conditional logic (NEW vs OLD), audit trail.
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_audit_inventory_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_change_qty    INTEGER;
    v_movement_type movement_type;
BEGIN
    -- Only fire if stock quantities actually changed
    IF NEW.on_hand = OLD.on_hand AND NEW.reserved = OLD.reserved THEN
        RETURN NEW;
    END IF;

    v_change_qty := NEW.on_hand - OLD.on_hand;

    -- Classify the movement type based on quantity direction and magnitude
    IF v_change_qty > 0 THEN
        v_movement_type := 'RESTOCK';
    ELSIF NEW.reserved > OLD.reserved THEN
        v_movement_type := 'ORDER_RESERVATION';
    ELSIF NEW.reserved < OLD.reserved AND NEW.on_hand < OLD.on_hand THEN
        v_movement_type := 'ORDER_FULFILLED';
    ELSIF NEW.reserved < OLD.reserved AND NEW.on_hand = OLD.on_hand THEN
        v_movement_type := 'RETURN_RESTOCK';
    ELSE
        v_movement_type := 'MANUAL_ADJUST';
    END IF;

    INSERT INTO inventory_movements (
        id,
        variant_id,
        change_qty,
        movement_type,
        reference_id,
        created_at
    ) VALUES (
        gen_random_uuid(),
        NEW.variant_id,
        v_change_qty,
        v_movement_type,
        'TRIGGER_AUTO',     -- Marks this as a trigger-generated record
        NOW()
    );

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_audit_inventory_change() IS
'Trigger function: auto-creates inventory_movements audit entries on any
 on_hand or reserved column change. Classifies movement type automatically.';

DROP TRIGGER IF EXISTS trg_audit_inventory_change ON inventory;
CREATE TRIGGER trg_audit_inventory_change
    AFTER UPDATE OF on_hand, reserved ON inventory
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_inventory_change();


-- ============================================================================
-- TRIGGER 3: trg_prevent_negative_stock
-- Purpose : Database-level guard that RAISES EXCEPTION if any UPDATE would
--           result in on_hand becoming negative. Acts as the last line of
--           defense against application-level bugs that might bypass the
--           service-layer checks.
-- Event   : BEFORE UPDATE on inventory
-- Demonstrates: BEFORE trigger for data validation, RAISE EXCEPTION.
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_prevent_negative_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Guard 1: on_hand cannot go below zero
    IF NEW.on_hand < 0 THEN
        RAISE EXCEPTION
            'STOCK INTEGRITY VIOLATION: on_hand cannot be negative. '
            'Variant: %, Attempted on_hand: %',
            NEW.variant_id, NEW.on_hand
            USING ERRCODE = 'check_violation';
    END IF;

    -- Guard 2: reserved cannot exceed on_hand
    IF NEW.reserved > NEW.on_hand THEN
        RAISE EXCEPTION
            'STOCK INTEGRITY VIOLATION: reserved (%) cannot exceed on_hand (%) '
            'for variant: %',
            NEW.reserved, NEW.on_hand, NEW.variant_id
            USING ERRCODE = 'check_violation';
    END IF;

    -- Guard 3: reserved cannot go below zero
    IF NEW.reserved < 0 THEN
        RAISE EXCEPTION
            'STOCK INTEGRITY VIOLATION: reserved cannot be negative. '
            'Variant: %, Attempted reserved: %',
            NEW.variant_id, NEW.reserved
            USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_prevent_negative_stock() IS
'BEFORE UPDATE trigger: enforces non-negative on_hand and reserved invariants.
 Provides database-level stock integrity as a last line of defense.';

DROP TRIGGER IF EXISTS trg_prevent_negative_stock ON inventory;
CREATE TRIGGER trg_prevent_negative_stock
    BEFORE UPDATE OF on_hand, reserved ON inventory
    FOR EACH ROW
    EXECUTE FUNCTION fn_prevent_negative_stock();


-- ============================================================================
-- TRIGGER 4: trg_log_order_status_change
-- Purpose : Automatically inserts a status-history record into
--           `order_status_history` whenever an order's status field changes.
--           Provides a complete audit trail of order lifecycle transitions.
-- Event   : AFTER UPDATE OF status on orders
-- Demonstrates: AFTER trigger, tracking state machine transitions.
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_log_order_status_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Only fire on actual status change
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO order_status_history (
            id,
            order_id,
            old_status,
            new_status,
            changed_at,
            changed_by
        ) VALUES (
            gen_random_uuid(),
            NEW.id,
            OLD.status::TEXT,
            NEW.status::TEXT,
            NOW(),
            'SYSTEM_TRIGGER'
        );
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_log_order_status_change() IS
'AFTER UPDATE trigger: logs every order status transition to order_status_history.
 Creates a tamper-proof audit trail of the order lifecycle.';

DROP TRIGGER IF EXISTS trg_log_order_status_change ON orders;
CREATE TRIGGER trg_log_order_status_change
    AFTER UPDATE OF status ON orders
    FOR EACH ROW
    EXECUTE FUNCTION fn_log_order_status_change();


-- ============================================================================
-- TRIGGER 5: trg_new_order_send_notification
-- Purpose : When a new order is INSERTED, automatically creates a notification
--           record for the customer. Demonstrates event-driven behavior
--           implemented at the database layer.
-- Event   : AFTER INSERT on orders
-- Demonstrates: AFTER INSERT trigger, cross-table side effects.
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_new_order_notification()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO notifications (
        id,
        user_id,
        title,
        message,
        notification_type,
        is_read,
        created_at
    ) VALUES (
        gen_random_uuid(),
        NEW.user_id,
        'Order Confirmed!',
        FORMAT(
            'Your order #%s has been placed successfully. Total: ₹%.2f. We will update you when it ships.',
            SUBSTRING(NEW.id::TEXT, 1, 8),
            NEW.total_amount
        ),
        'ORDER_UPDATE',
        FALSE,
        NOW()
    );

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION fn_new_order_notification() IS
'AFTER INSERT trigger on orders: auto-creates an in-app notification record
 for the customer upon order placement. Event-driven notification at DB level.';

DROP TRIGGER IF EXISTS trg_new_order_notification ON orders;
CREATE TRIGGER trg_new_order_notification
    AFTER INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION fn_new_order_notification();


-- ============================================================================
-- TRIGGER 6: trg_enforce_order_item_positive_quantity
-- Purpose : Prevents insertion of order_items with quantity <= 0.
--           Demonstrates: BEFORE INSERT validation trigger.
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_enforce_positive_quantity()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.quantity <= 0 THEN
        RAISE EXCEPTION
            'ORDER INTEGRITY VIOLATION: order_item quantity must be > 0. Got: %',
            NEW.quantity
            USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.unit_price < 0 THEN
        RAISE EXCEPTION
            'ORDER INTEGRITY VIOLATION: unit_price cannot be negative. Got: %',
            NEW.unit_price
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_enforce_positive_order_quantity ON order_items;
CREATE TRIGGER trg_enforce_positive_order_quantity
    BEFORE INSERT OR UPDATE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION fn_enforce_positive_quantity();
