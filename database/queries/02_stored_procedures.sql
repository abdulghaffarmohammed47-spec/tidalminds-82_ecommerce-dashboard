-- ============================================================================
-- SMARTCOMMERCE AI: STORED PROCEDURES & FUNCTIONS
-- File: database/queries/02_stored_procedures.sql
-- Purpose: Encapsulates critical business logic at the database layer using
--          PL/pgSQL. Guarantees atomicity, reduces network round-trips,
--          and enforces business rules independent of the application layer.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- FUNCTION 1: fn_available_stock
-- Purpose : Returns the currently available (uncommitted) stock for a variant.
--           Available = on_hand - reserved
-- Returns : INTEGER — units available for purchase.
-- Demonstrates: Simple scalar UDF, NULL-safe COALESCE.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_available_stock(p_variant_id UUID)
RETURNS INTEGER
LANGUAGE plpgsql
STABLE -- Does not modify DB; can be safely cached per transaction
AS $$
DECLARE
    v_available INTEGER;
BEGIN
    SELECT COALESCE(on_hand - reserved, 0)
    INTO v_available
    FROM inventory
    WHERE variant_id = p_variant_id;

    -- Returns 0 if the variant has no inventory record yet
    RETURN COALESCE(v_available, 0);
END;
$$;

COMMENT ON FUNCTION fn_available_stock(UUID) IS
'Returns available stock (on_hand - reserved) for a given product variant.
 Returns 0 if no inventory record exists.';


-- ----------------------------------------------------------------------------
-- FUNCTION 2: fn_restock_variant
-- Purpose : Safely adds stock to a product variant and creates an audit entry.
--           Uses UPSERT (INSERT ... ON CONFLICT) to handle missing records.
-- Returns : INTEGER — new on_hand quantity after restock.
-- Demonstrates: UPSERT pattern, audit trail creation, OUT parameter.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_restock_variant(
    p_variant_id    UUID,
    p_quantity      INTEGER,
    p_reason        TEXT DEFAULT 'RESTOCK',
    p_reference_id  TEXT DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_new_on_hand   INTEGER;
    v_inventory_id  UUID;
BEGIN
    -- Validate input
    IF p_quantity <= 0 THEN
        RAISE EXCEPTION 'Restock quantity must be positive. Got: %', p_quantity;
    END IF;

    -- UPSERT: create or update inventory record
    INSERT INTO inventory (id, variant_id, on_hand, reserved, safety_stock)
    VALUES (gen_random_uuid(), p_variant_id, p_quantity, 0, 2)
    ON CONFLICT (variant_id) DO UPDATE
        SET on_hand = inventory.on_hand + EXCLUDED.on_hand
    RETURNING id, on_hand INTO v_inventory_id, v_new_on_hand;

    -- Audit movement record
    INSERT INTO inventory_movements (
        id, variant_id, change_qty, movement_type, reference_id, created_at
    ) VALUES (
        gen_random_uuid(),
        p_variant_id,
        p_quantity,
        'RESTOCK',
        p_reference_id,
        NOW()
    );

    RETURN v_new_on_hand;
END;
$$;

COMMENT ON FUNCTION fn_restock_variant(UUID, INTEGER, TEXT, TEXT) IS
'Atomically restocks a product variant: upserts the inventory record and
 creates an audit movement entry. Returns new on_hand quantity.';


-- ----------------------------------------------------------------------------
-- PROCEDURE 3: sp_place_order
-- Purpose : Full atomic order creation with pessimistic row-locking.
--           Implements the SAGA pattern entirely in SQL:
--           1. Validates cart items exist and have stock.
--           2. Locks inventory rows with SELECT ... FOR UPDATE.
--           3. Deducts reserved stock.
--           4. Inserts order and order_items.
--           5. Records inventory movements.
--           If any step fails, the entire transaction ROLLBACKS.
-- Demonstrates: Transactions, FOR UPDATE locking, EXCEPTION handling, LOOP.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_place_order(
    p_user_id           UUID,
    p_items             JSONB,      -- [{"variant_id":"...", "quantity":2, "unit_price":99.99}, ...]
    p_shipping_address  JSONB,
    OUT p_order_id      UUID,
    OUT p_status        TEXT,
    OUT p_message       TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item          JSONB;
    v_variant_id    UUID;
    v_quantity      INTEGER;
    v_unit_price    NUMERIC(12,2);
    v_on_hand       INTEGER;
    v_reserved      INTEGER;
    v_available     INTEGER;
    v_total_amount  NUMERIC(12,2) := 0.00;
    v_order_id      UUID := gen_random_uuid();
BEGIN
    -- ---- STEP 1: Validate input ----
    IF p_items IS NULL OR jsonb_array_length(p_items) = 0 THEN
        p_order_id := NULL;
        p_status   := 'ERROR';
        p_message  := 'Cannot place an order with no items.';
        RETURN;
    END IF;

    -- ---- STEP 2: Per-item validation and stock locking ----
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        v_variant_id  := (v_item->>'variant_id')::UUID;
        v_quantity    := (v_item->>'quantity')::INTEGER;
        v_unit_price  := (v_item->>'unit_price')::NUMERIC(12,2);

        -- Pessimistic row-level lock: blocks concurrent checkout of same variant
        SELECT on_hand, reserved
        INTO v_on_hand, v_reserved
        FROM inventory
        WHERE variant_id = v_variant_id
        FOR UPDATE;  -- KEY: Prevents race conditions / overselling

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Inventory record not found for variant: %', v_variant_id;
        END IF;

        v_available := v_on_hand - v_reserved;

        IF v_available < v_quantity THEN
            RAISE EXCEPTION
                'Insufficient stock for variant %. Available: %, Requested: %',
                v_variant_id, v_available, v_quantity;
        END IF;

        -- Reserve the stock (soft lock)
        UPDATE inventory
        SET reserved = reserved + v_quantity
        WHERE variant_id = v_variant_id;

        -- Record reservation movement
        INSERT INTO inventory_movements (id, variant_id, change_qty, movement_type, reference_id, created_at)
        VALUES (gen_random_uuid(), v_variant_id, -v_quantity, 'ORDER_RESERVATION', v_order_id::TEXT, NOW());

        v_total_amount := v_total_amount + (v_unit_price * v_quantity);
    END LOOP;

    -- ---- STEP 3: Create Order record ----
    INSERT INTO orders (id, user_id, status, total_amount, shipping_address, created_at)
    VALUES (v_order_id, p_user_id, 'CONFIRMED', v_total_amount, p_shipping_address, NOW());

    -- ---- STEP 4: Create Order Items ----
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        v_variant_id := (v_item->>'variant_id')::UUID;
        v_quantity   := (v_item->>'quantity')::INTEGER;
        v_unit_price := (v_item->>'unit_price')::NUMERIC(12,2);

        INSERT INTO order_items (id, order_id, variant_id, unit_price, quantity)
        VALUES (gen_random_uuid(), v_order_id, v_variant_id, v_unit_price, v_quantity);

        -- Fulfill stock: deduct from on_hand
        UPDATE inventory
        SET on_hand   = on_hand - v_quantity,
            reserved  = reserved - v_quantity
        WHERE variant_id = v_variant_id;

        -- Record fulfillment movement
        INSERT INTO inventory_movements (id, variant_id, change_qty, movement_type, reference_id, created_at)
        VALUES (gen_random_uuid(), v_variant_id, -v_quantity, 'ORDER_FULFILLED', v_order_id::TEXT, NOW());
    END LOOP;

    p_order_id := v_order_id;
    p_status   := 'SUCCESS';
    p_message  := FORMAT('Order %s placed successfully. Total: %s', v_order_id, v_total_amount);

EXCEPTION WHEN OTHERS THEN
    -- Full rollback happens automatically on EXCEPTION in a PL/pgSQL block
    p_order_id := NULL;
    p_status   := 'ERROR';
    p_message  := SQLERRM;
    RAISE; -- Re-raise so the caller's transaction also rolls back
END;
$$;

COMMENT ON PROCEDURE sp_place_order(UUID, JSONB, JSONB, UUID, TEXT, TEXT) IS
'Atomic order placement with pessimistic inventory locking (SELECT...FOR UPDATE).
 Guarantees zero oversell under concurrent load. Rolls back entirely on any failure.';


-- ----------------------------------------------------------------------------
-- PROCEDURE 4: sp_cancel_order
-- Purpose : Cancels an order and releases all reserved/fulfilled stock.
--           Demonstrates: Compensating transaction (Saga rollback).
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_cancel_order(
    p_order_id  UUID,
    p_user_id   UUID DEFAULT NULL,    -- Optional: validate ownership
    OUT p_status    TEXT,
    OUT p_message   TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order         orders%ROWTYPE;
    v_item          order_items%ROWTYPE;
BEGIN
    -- Fetch and validate order
    SELECT * INTO v_order FROM orders WHERE id = p_order_id FOR UPDATE;

    IF NOT FOUND THEN
        p_status  := 'ERROR';
        p_message := FORMAT('Order %s not found.', p_order_id);
        RETURN;
    END IF;

    -- Ownership check if user_id provided
    IF p_user_id IS NOT NULL AND v_order.user_id != p_user_id THEN
        p_status  := 'ERROR';
        p_message := 'Unauthorized: you do not own this order.';
        RETURN;
    END IF;

    -- Can only cancel PENDING or CONFIRMED orders
    IF v_order.status NOT IN ('PENDING', 'CONFIRMED') THEN
        p_status  := 'ERROR';
        p_message := FORMAT('Cannot cancel order in status: %s', v_order.status);
        RETURN;
    END IF;

    -- Compensating transaction: return stock for all items
    FOR v_item IN SELECT * FROM order_items WHERE order_id = p_order_id
    LOOP
        UPDATE inventory
        SET on_hand  = on_hand + v_item.quantity,
            reserved = GREATEST(reserved - v_item.quantity, 0)
        WHERE variant_id = v_item.variant_id;

        INSERT INTO inventory_movements (id, variant_id, change_qty, movement_type, reference_id, created_at)
        VALUES (gen_random_uuid(), v_item.variant_id, v_item.quantity, 'RETURN_RESTOCK', p_order_id::TEXT, NOW());
    END LOOP;

    -- Mark order as CANCELLED
    UPDATE orders SET status = 'CANCELLED' WHERE id = p_order_id;

    p_status  := 'SUCCESS';
    p_message := FORMAT('Order %s successfully cancelled and stock restored.', p_order_id);

EXCEPTION WHEN OTHERS THEN
    p_status  := 'ERROR';
    p_message := SQLERRM;
    RAISE;
END;
$$;

COMMENT ON PROCEDURE sp_cancel_order(UUID, UUID, TEXT, TEXT) IS
'Cancels an order and performs compensating stock restoration.
 Implements the Saga compensation pattern for failed/cancelled transactions.';


-- ----------------------------------------------------------------------------
-- FUNCTION 5: fn_category_breadcrumb
-- Purpose : Returns the full hierarchical path for a category using a
--           recursive CTE (WITH RECURSIVE).
-- Returns : TEXT — e.g., "Electronics > Laptops > Gaming Laptops"
-- Demonstrates: Recursive CTE, self-referential table traversal.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_category_breadcrumb(p_category_id UUID)
RETURNS TEXT
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_breadcrumb TEXT;
BEGIN
    WITH RECURSIVE category_path AS (
        -- Base case: start at the given category
        SELECT id, name, parent_id, 1 AS depth
        FROM categories
        WHERE id = p_category_id

        UNION ALL

        -- Recursive case: walk up to parent
        SELECT c.id, c.name, c.parent_id, cp.depth + 1
        FROM categories c
        JOIN category_path cp ON c.id = cp.parent_id
    )
    SELECT STRING_AGG(name, ' > ' ORDER BY depth DESC)
    INTO v_breadcrumb
    FROM category_path;

    RETURN COALESCE(v_breadcrumb, 'Unknown Category');
END;
$$;

COMMENT ON FUNCTION fn_category_breadcrumb(UUID) IS
'Recursively builds a breadcrumb path for a category hierarchy.
 Example output: "Electronics > Computers > Laptops"';


-- ----------------------------------------------------------------------------
-- FUNCTION 6: fn_product_search_rank
-- Purpose : Computes a composite search relevance score combining:
--           - pgvector cosine similarity (AI match)
--           - Stock availability bonus
--           - Rating boost
-- Returns : NUMERIC — normalized score 0.0–1.0 (higher = more relevant)
-- Demonstrates: Hybrid scoring, computed columns, pgvector integration.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_product_search_rank(
    p_product_id    UUID,
    p_query_vector  vector(384)
)
RETURNS NUMERIC
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_cosine_sim    NUMERIC := 0.0;
    v_stock_bonus   NUMERIC := 0.0;
    v_rating_boost  NUMERIC := 0.0;
    v_available     INTEGER := 0;
    v_rating        NUMERIC := 0.0;
BEGIN
    -- Cosine similarity from pgvector (1 - distance, so higher = more similar)
    SELECT (1 - (pe.embedding <=> p_query_vector))
    INTO v_cosine_sim
    FROM product_embeddings pe
    WHERE pe.product_id = p_product_id;

    -- Available stock (capped bonus: in-stock = 1.0, out-of-stock = 0.0)
    SELECT CASE WHEN fn_available_stock(pv.id) > 0 THEN 1.0 ELSE 0.0 END
    INTO v_stock_bonus
    FROM product_variants pv
    WHERE pv.product_id = p_product_id
    LIMIT 1;

    -- Rating boost (normalized 0–5 scale to 0.0–1.0)
    SELECT COALESCE(rating_avg / 5.0, 0.0)
    INTO v_rating_boost
    FROM products
    WHERE id = p_product_id;

    -- Weighted composite: 70% semantic, 20% stock, 10% rating
    RETURN ROUND(
        (COALESCE(v_cosine_sim, 0.0)  * 0.70) +
        (COALESCE(v_stock_bonus, 0.0) * 0.20) +
        (COALESCE(v_rating_boost, 0.0) * 0.10),
        4
    );
END;
$$;

COMMENT ON FUNCTION fn_product_search_rank(UUID, vector) IS
'Hybrid search ranking: combines pgvector cosine similarity (70%), stock
 availability (20%), and product rating (10%) into a composite score 0.0-1.0.';
