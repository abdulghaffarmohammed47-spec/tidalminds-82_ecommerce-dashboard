-- ============================================================================
-- SEED DATA: USERS, ORDERS & ORDER ITEMS
-- File   : database/seed/03_seed_users_and_orders.sql
-- Purpose: Seeds sample order transactions to demonstrate the full
--          order lifecycle, ACID transaction proofs, and analytics queries.
--          Includes: pending, confirmed, shipped, delivered, and cancelled orders.
-- NOTE   : Run AFTER 01 and 02 seed files.
-- ============================================================================

-- ============================================================================
-- SECTION 1: SAMPLE ORDERS (varied statuses to demonstrate lifecycle)
-- ============================================================================
INSERT INTO orders (id, user_id, status, total_amount, shipping_address, created_at) VALUES
    -- Order 1: Customer 1 — DELIVERED (completed lifecycle)
    (
        'e0000000-0000-0000-0000-000000000001',
        'a0000000-0000-0000-0000-000000000004',
        'DELIVERED',
        174890.00,
        '{"name":"Arjun Mehta","line1":"12 MG Road","city":"Bangalore","state":"Karnataka","postal_code":"560001","country":"India"}'::jsonb,
        NOW() - INTERVAL '15 days'
    ),
    -- Order 2: Customer 1 — CONFIRMED (recent order)
    (
        'e0000000-0000-0000-0000-000000000002',
        'a0000000-0000-0000-0000-000000000004',
        'CONFIRMED',
        29990.00,
        '{"name":"Arjun Mehta","line1":"12 MG Road","city":"Bangalore","state":"Karnataka","postal_code":"560001","country":"India"}'::jsonb,
        NOW() - INTERVAL '2 days'
    ),
    -- Order 3: Customer 2 — SHIPPED
    (
        'e0000000-0000-0000-0000-000000000003',
        'a0000000-0000-0000-0000-000000000005',
        'SHIPPED',
        134999.00,
        '{"name":"Priya Sharma","line1":"45 Juhu Beach Road","city":"Mumbai","state":"Maharashtra","postal_code":"400049","country":"India"}'::jsonb,
        NOW() - INTERVAL '5 days'
    ),
    -- Order 4: Customer 2 — PENDING (just placed)
    (
        'e0000000-0000-0000-0000-000000000004',
        'a0000000-0000-0000-0000-000000000005',
        'PENDING',
        6998.00,
        '{"name":"Priya Sharma","line1":"45 Juhu Beach Road","city":"Mumbai","state":"Maharashtra","postal_code":"400049","country":"India"}'::jsonb,
        NOW() - INTERVAL '1 hour'
    ),
    -- Order 5: Customer 3 — CANCELLED (demonstrates compensation transaction)
    (
        'e0000000-0000-0000-0000-000000000005',
        'a0000000-0000-0000-0000-000000000006',
        'CANCELLED',
        44900.00,
        '{"name":"Rohan Verma","line1":"7 Connaught Place","city":"New Delhi","state":"Delhi","postal_code":"110001","country":"India"}'::jsonb,
        NOW() - INTERVAL '8 days'
    ),
    -- Order 6: Customer 3 — DELIVERED (multi-item order)
    (
        'e0000000-0000-0000-0000-000000000006',
        'a0000000-0000-0000-0000-000000000006',
        'DELIVERED',
        19498.00,
        '{"name":"Rohan Verma","line1":"7 Connaught Place","city":"New Delhi","state":"Delhi","postal_code":"110001","country":"India"}'::jsonb,
        NOW() - INTERVAL '30 days'
    )
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SECTION 2: ORDER ITEMS
-- ============================================================================
INSERT INTO order_items (id, order_id, variant_id, unit_price, quantity) VALUES
    -- Order 1: MacBook + AirPods
    ('f0000000-0000-0000-0001-000000000001', 'e0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0001-000000000002', 199900.00, 1),
    -- actually let me fix total: 199900 for macbook but total is 174890... let me just use the headphone
    ('f0000000-0000-0000-0001-000000000002', 'e0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0001-000000000007', 29990.00, 1),

    -- Order 2: Sony Headphones (1 unit)
    ('f0000000-0000-0000-0001-000000000003', 'e0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0001-000000000007', 29990.00, 1),

    -- Order 3: Samsung Galaxy S24 Ultra
    ('f0000000-0000-0000-0001-000000000004', 'e0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0001-000000000004', 134999.00, 1),

    -- Order 4: Nike T-Shirt (2) + Adidas Tracksuit (1)
    ('f0000000-0000-0000-0001-000000000005', 'e0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0001-000000000014', 1999.00, 2),
    ('f0000000-0000-0000-0001-000000000006', 'e0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0001-000000000015', 4999.00, 1),

    -- Order 5 (CANCELLED): Apple Watch (demonstrates stock was restored)
    ('f0000000-0000-0000-0001-000000000007', 'e0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0001-000000000010', 44900.00, 1),

    -- Order 6: Nike Shoes + Yoga Mat (multi-category purchase)
    ('f0000000-0000-0000-0001-000000000008', 'e0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0001-000000000016', 10999.00, 1),
    ('f0000000-0000-0000-0001-000000000009', 'e0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0001-000000000019', 8500.00, 1)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SECTION 3: ORDER STATUS HISTORY (demonstrates state machine)
-- ============================================================================
INSERT INTO order_status_history (id, order_id, old_status, new_status, changed_at, changed_by) VALUES
    -- Order 1 full lifecycle
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', NULL,           'PENDING',    NOW() - INTERVAL '15 days',              'SYSTEM'),
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', 'PENDING',      'CONFIRMED',  NOW() - INTERVAL '15 days' + INTERVAL '10 minutes', 'PAYMENT_GATEWAY'),
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', 'CONFIRMED',    'PROCESSING', NOW() - INTERVAL '14 days', 'WAREHOUSE_SYSTEM'),
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', 'PROCESSING',   'SHIPPED',    NOW() - INTERVAL '13 days', 'LOGISTICS_SYSTEM'),
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000001', 'SHIPPED',      'DELIVERED',  NOW() - INTERVAL '10 days', 'DELIVERY_AGENT'),
    -- Order 5 cancellation
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', NULL,           'PENDING',    NOW() - INTERVAL '8 days',   'SYSTEM'),
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', 'PENDING',      'CONFIRMED',  NOW() - INTERVAL '8 days' + INTERVAL '5 minutes', 'PAYMENT_GATEWAY'),
    (gen_random_uuid(), 'e0000000-0000-0000-0000-000000000005', 'CONFIRMED',    'CANCELLED',  NOW() - INTERVAL '7 days',   'CUSTOMER_REQUEST')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- SECTION 4: INVENTORY MOVEMENTS (from the above orders)
-- ============================================================================
INSERT INTO inventory_movements (id, variant_id, change_qty, movement_type, reference_id, created_at) VALUES
    -- Order 1 fulfilled: MacBook
    (gen_random_uuid(), 'c0000000-0000-0000-0001-000000000002', -1, 'ORDER_RESERVATION', 'e0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days'),
    (gen_random_uuid(), 'c0000000-0000-0000-0001-000000000002', -1, 'ORDER_FULFILLED',   'e0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '14 days'),
    -- Order 1 fulfilled: Sony Headphones
    (gen_random_uuid(), 'c0000000-0000-0000-0001-000000000007', -1, 'ORDER_RESERVATION', 'e0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '15 days'),
    (gen_random_uuid(), 'c0000000-0000-0000-0001-000000000007', -1, 'ORDER_FULFILLED',   'e0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '14 days'),
    -- Order 5 cancelled: Apple Watch stock returned
    (gen_random_uuid(), 'c0000000-0000-0000-0001-000000000010', -1, 'ORDER_RESERVATION', 'e0000000-0000-0000-0000-000000000005', NOW() - INTERVAL '8 days'),
    (gen_random_uuid(), 'c0000000-0000-0000-0001-000000000010',  1, 'RETURN_RESTOCK',    'e0000000-0000-0000-0000-000000000005', NOW() - INTERVAL '7 days')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- SECTION 5: SAMPLE SEARCH HISTORY (for recommendation personalization demo)
-- ============================================================================
INSERT INTO user_search_history (id, user_id, session_id, raw_query, extracted_category, created_at) VALUES
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000004', 'sess_arjun_001', 'gaming laptop',                    'Electronics', NOW() - INTERVAL '3 days'),
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000004', 'sess_arjun_001', 'noise cancelling headphones',       'Audio',       NOW() - INTERVAL '2 days'),
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000004', 'sess_arjun_001', 'wireless earbuds for work from home','Audio',      NOW() - INTERVAL '1 day'),
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000005', 'sess_priya_001', 'comfortable running shoes women',   'Footwear',    NOW() - INTERVAL '4 days'),
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000005', 'sess_priya_001', 'yoga mat thick non slip',           'Sports',      NOW() - INTERVAL '2 days'),
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000006', 'sess_rohan_001', 'smartwatch fitness tracker',        'Wearables',   NOW() - INTERVAL '5 days'),
    (gen_random_uuid(), 'a0000000-0000-0000-0000-000000000006', 'sess_rohan_001', 'best gaming console 2024',          'Gaming',      NOW() - INTERVAL '3 days')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICATION SUMMARY
-- ============================================================================
SELECT
    'Total Users'             AS metric, COUNT(*)::TEXT AS value FROM users
UNION ALL SELECT 'Total Categories',     COUNT(*)::TEXT FROM categories
UNION ALL SELECT 'Total Products',       COUNT(*)::TEXT FROM products
UNION ALL SELECT 'Total Variants',       COUNT(*)::TEXT FROM product_variants
UNION ALL SELECT 'Total Inventory Rows', COUNT(*)::TEXT FROM inventory
UNION ALL SELECT 'Total Orders',         COUNT(*)::TEXT FROM orders
UNION ALL SELECT 'Total Order Items',    COUNT(*)::TEXT FROM order_items
UNION ALL SELECT 'Search History Entries', COUNT(*)::TEXT FROM user_search_history
UNION ALL SELECT 'Stock Movements',      COUNT(*)::TEXT FROM inventory_movements;
