-- ============================================================================
-- SEED DATA: REFERENCE DATA — CATEGORIES & USERS
-- File   : database/seed/01_seed_reference_data.sql
-- Purpose: Seeds fundamental reference data — categories (mirrors V4 migration)
--          plus test user accounts for local development and demos.
-- NOTE   : Run AFTER V1__initial_schema.sql. Idempotent (ON CONFLICT DO NOTHING).
-- ============================================================================

-- ============================================================================
-- SECTION 1: TEST USERS
-- All passwords = 'Password@123' hashed with bcrypt (cost=12)
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q (placeholder)
-- ============================================================================
INSERT INTO users (id, email, password_hash, full_name, role, is_active) VALUES
    (
        'a0000000-0000-0000-0000-000000000001',
        'admin@smartcommerce.ai',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q',
        'Admin User',
        'ADMIN',
        TRUE
    ),
    (
        'a0000000-0000-0000-0000-000000000002',
        'seller1@smartcommerce.ai',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q',
        'TechVendor India',
        'SELLER',
        TRUE
    ),
    (
        'a0000000-0000-0000-0000-000000000003',
        'seller2@smartcommerce.ai',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q',
        'Fashion Hub',
        'SELLER',
        TRUE
    ),
    (
        'a0000000-0000-0000-0000-000000000004',
        'customer1@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q',
        'Arjun Mehta',
        'CUSTOMER',
        TRUE
    ),
    (
        'a0000000-0000-0000-0000-000000000005',
        'customer2@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q',
        'Priya Sharma',
        'CUSTOMER',
        TRUE
    ),
    (
        'a0000000-0000-0000-0000-000000000006',
        'customer3@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HD.A13q',
        'Rohan Verma',
        'CUSTOMER',
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SECTION 2: CATEGORIES (mirror of V4 migration — safe to run standalone)
-- ============================================================================
INSERT INTO categories (id, name, slug, parent_id) VALUES
    ('10000000-0000-0000-0000-000000000001', 'Electronics',    'electronics',     NULL),
    ('10000000-0000-0000-0000-000000000002', 'Clothing',        'clothing',        NULL),
    ('10000000-0000-0000-0000-000000000003', 'Home & Kitchen',  'home-kitchen',    NULL),
    ('10000000-0000-0000-0000-000000000004', 'Books',           'books',           NULL),
    ('10000000-0000-0000-0000-000000000005', 'Sports & Fitness','sports-fitness',  NULL),
    ('10000000-0000-0000-0000-000000000006', 'Beauty & Health', 'beauty-health',   NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO categories (id, name, slug, parent_id) VALUES
    ('20000000-0000-0000-0000-000000000001', 'Laptops & Computers', 'laptops-computers', '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000002', 'Smartphones',          'smartphones',        '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000003', 'Audio & Headphones',   'audio-headphones',   '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000004', 'Cameras',              'cameras',            '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000005', 'Wearables',            'wearables',          '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000006', 'Gaming',               'gaming',             '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000007', 'Men''s Fashion',       'mens-fashion',       '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000008', 'Women''s Fashion',     'womens-fashion',     '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000009', 'Footwear',             'footwear',           '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000010', 'Kitchen Appliances',   'kitchen-appliances', '10000000-0000-0000-0000-000000000003'),
    ('20000000-0000-0000-0000-000000000013', 'Gym & Fitness',        'gym-fitness',        '10000000-0000-0000-0000-000000000005'),
    ('20000000-0000-0000-0000-000000000014', 'Outdoor & Trekking',   'outdoor-trekking',   '10000000-0000-0000-0000-000000000005')
ON CONFLICT (id) DO NOTHING;

-- Verify seeding
SELECT
    'Users seeded'      AS entity, COUNT(*) AS total FROM users
UNION ALL
SELECT 'Categories seeded', COUNT(*) FROM categories;
