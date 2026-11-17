-- ============================================================================
-- MIGRATION V4: REFERENCE DATA — CATEGORIES & BRANDS
-- File   : database/migrations/V4__seed_categories_and_brands.sql
-- Date   : 2026-09-08
-- Depends: V1, V2, V3
-- Purpose: Seeds the reference/lookup data that the platform needs before
--          products can be added. Idempotent — safe to run multiple times.
-- ============================================================================

-- ============================================================================
-- SEED: TOP-LEVEL CATEGORIES
-- ============================================================================
INSERT INTO categories (id, name, slug, parent_id) VALUES
    ('10000000-0000-0000-0000-000000000001', 'Electronics',    'electronics',     NULL),
    ('10000000-0000-0000-0000-000000000002', 'Clothing',        'clothing',        NULL),
    ('10000000-0000-0000-0000-000000000003', 'Home & Kitchen',  'home-kitchen',    NULL),
    ('10000000-0000-0000-0000-000000000004', 'Books',           'books',           NULL),
    ('10000000-0000-0000-0000-000000000005', 'Sports & Fitness','sports-fitness',  NULL),
    ('10000000-0000-0000-0000-000000000006', 'Beauty & Health', 'beauty-health',   NULL),
    ('10000000-0000-0000-0000-000000000007', 'Toys & Games',    'toys-games',      NULL),
    ('10000000-0000-0000-0000-000000000008', 'Automotive',      'automotive',      NULL)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- SEED: SUB-CATEGORIES (Electronics children)
-- ============================================================================
INSERT INTO categories (id, name, slug, parent_id) VALUES
    ('20000000-0000-0000-0000-000000000001', 'Laptops & Computers', 'laptops-computers',   '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000002', 'Smartphones',          'smartphones',          '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000003', 'Audio & Headphones',   'audio-headphones',     '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000004', 'Cameras',              'cameras',              '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000005', 'Wearables',            'wearables',            '10000000-0000-0000-0000-000000000001'),
    ('20000000-0000-0000-0000-000000000006', 'Gaming',               'gaming',               '10000000-0000-0000-0000-000000000001'),
    -- Clothing sub-categories
    ('20000000-0000-0000-0000-000000000007', 'Men''s Fashion',       'mens-fashion',         '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000008', 'Women''s Fashion',     'womens-fashion',       '10000000-0000-0000-0000-000000000002'),
    ('20000000-0000-0000-0000-000000000009', 'Footwear',             'footwear',             '10000000-0000-0000-0000-000000000002'),
    -- Home sub-categories
    ('20000000-0000-0000-0000-000000000010', 'Kitchen Appliances',   'kitchen-appliances',   '10000000-0000-0000-0000-000000000003'),
    ('20000000-0000-0000-0000-000000000011', 'Furniture',            'furniture',            '10000000-0000-0000-0000-000000000003'),
    ('20000000-0000-0000-0000-000000000012', 'Home Decor',           'home-decor',           '10000000-0000-0000-0000-000000000003'),
    -- Sports sub-categories
    ('20000000-0000-0000-0000-000000000013', 'Gym & Fitness',        'gym-fitness',          '10000000-0000-0000-0000-000000000005'),
    ('20000000-0000-0000-0000-000000000014', 'Outdoor & Trekking',   'outdoor-trekking',     '10000000-0000-0000-0000-000000000005')
ON CONFLICT (id) DO NOTHING;

INSERT INTO schema_migrations (version, description)
VALUES ('V4', 'Reference data seeded: 8 top-level categories, 14 sub-categories')
ON CONFLICT (version) DO NOTHING;
