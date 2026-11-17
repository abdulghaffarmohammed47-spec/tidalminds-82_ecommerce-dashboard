# SMARTCOMMERCE: PostgreSQL Relational Database Demonstration & SQL Reference

> **Course**: Database Systems Engineering / DBMS  
> **Topic**: PostgreSQL 3NF Schema, Relational Integrity, ACID Transactions, and Performance Tuning

---

## 1. Relational Schema & Table Definitions (3NF)

SMARTCOMMERCE implements a 3NF normalized schema ensuring data integrity, zero redundancy, and transactional safety:

```sql
-- 1. Categories Schema
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    parent_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Brands Schema
CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Canonical Products Catalog
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INT NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    brand_id INT REFERENCES brands(brand_id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(280) UNIQUE NOT NULL,
    description TEXT,
    base_price NUMERIC(12, 2) NOT NULL CHECK (base_price >= 0),
    rating NUMERIC(3, 2) DEFAULT 4.5 CHECK (rating >= 0 AND rating <= 5),
    reviews_count INT DEFAULT 0 CHECK (reviews_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Multi-Seller Offers & Inventory Isolation
CREATE TABLE seller_products (
    offer_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    seller_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_name VARCHAR(150) NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    delivery_days INT DEFAULT 2 CHECK (delivery_days >= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Physical Warehouse Stocks
CREATE TABLE inventory (
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    stock_on_hand INT NOT NULL CHECK (stock_on_hand >= 0),
    stock_reserved INT DEFAULT 0 CHECK (stock_reserved >= 0),
    PRIMARY KEY (warehouse_id, product_id)
);

-- 6. Authoritative Orders Ledger
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    buyer_id INT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    shipping_address TEXT NOT NULL,
    order_status VARCHAR(50) DEFAULT 'CONFIRMED' CHECK (order_status IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')),
    placed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Order Items (Child Line Items)
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    seller_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0)
);

-- 8. Coupons
CREATE TABLE coupons (
    code VARCHAR(50) PRIMARY KEY,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('PERCENTAGE', 'FLAT')),
    value NUMERIC(10, 2) NOT NULL CHECK (value > 0),
    min_order NUMERIC(12, 2) DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE
);
```

---

## 2. Core SQL Queries & Demonstrations

### A. Multi-Table JOIN (Product Catalog + Best Seller Offer + Category)
```sql
SELECT 
    p.product_id,
    p.title,
    c.name AS category_name,
    b.name AS brand_name,
    p.base_price,
    MIN(sp.price) AS best_marketplace_price,
    SUM(sp.stock_quantity) AS total_fulfillable_stock,
    COUNT(DISTINCT sp.seller_id) AS active_competing_sellers
FROM products p
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN brands b ON p.brand_id = b.brand_id
LEFT JOIN seller_products sp ON p.product_id = sp.product_id
GROUP BY p.product_id, p.title, c.name, b.name, p.base_price
ORDER BY total_fulfillable_stock DESC;
```

### B. GROUP BY & Aggregation (Seller GMV & Fulfillable Units)
```sql
SELECT 
    sp.seller_name,
    COUNT(DISTINCT sp.product_id) AS total_listed_skus,
    SUM(sp.stock_quantity) AS total_inventory_units,
    AVG(sp.price) AS average_listing_price,
    MIN(sp.price) AS lowest_offer_price
FROM seller_products sp
GROUP BY sp.seller_name
HAVING SUM(sp.stock_quantity) > 0
ORDER BY total_inventory_units DESC;
```

### C. Correlated Subqueries (Products with Prices Below Category Average)
```sql
SELECT 
    p.title,
    p.base_price,
    c.name AS category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.base_price < (
    SELECT AVG(p2.base_price)
    FROM products p2
    WHERE p2.category_id = p.category_id
);
```

### D. Advanced Window Functions (Ranking Competing Seller Offers per Product)
```sql
SELECT 
    sp.product_id,
    p.title,
    sp.seller_name,
    sp.price,
    sp.stock_quantity,
    sp.delivery_days,
    DENSE_RANK() OVER (
        PARTITION BY sp.product_id 
        ORDER BY sp.price ASC, sp.delivery_days ASC
    ) AS buybox_seller_rank
FROM seller_products sp
JOIN products p ON sp.product_id = p.product_id
WHERE sp.stock_quantity > 0;
```

---

## 3. ACID Transactions & Row-Level Locking (`FOR UPDATE`)

### Deterministic Checkout Transaction Flow
When a customer purchases a product, the transaction enforces:
1. Row lock on the seller's inventory row to prevent concurrent overselling.
2. Verification of available stock against requested quantity.
3. Decrement of `seller_products.stock_quantity` and `inventory.stock_on_hand`.
4. Creation of `orders` and `order_items` tuples.
5. Deterministic `COMMIT` or `ROLLBACK`.

```sql
BEGIN TRANSACTION;

-- 1. Acquire exclusive row lock on targeted offer
SELECT stock_quantity, price 
FROM seller_products 
WHERE offer_id = 4 
FOR UPDATE;

-- Application checks: IF stock_quantity < requested_quantity THEN ROLLBACK;

-- 2. Atomic Decrement of Merchant Inventory (protected by CHECK stock_quantity >= 0)
UPDATE seller_products 
SET stock_quantity = stock_quantity - 1 
WHERE offer_id = 4;

-- 3. Atomic Decrement of Physical Warehouse Inventory
UPDATE inventory 
SET stock_on_hand = stock_on_hand - 1 
WHERE product_id = 2;

-- 4. Record Authoritative Order
INSERT INTO orders (buyer_id, total_amount, shipping_address, order_status)
VALUES (1, 74999.00, 'Bengaluru 560001, Tech Park #402', 'CONFIRMED')
RETURNING order_id;

-- 5. Record Order Items
INSERT INTO order_items (order_id, product_id, seller_id, quantity, unit_price)
VALUES (currval(pg_get_serial_sequence('orders', 'order_id')), 2, 1, 1, 74999.00);

-- 6. Commit or Rollback
COMMIT;
```

---

## 4. Indexing Decisions & Optimization Rationale

| Index Name | Target Table | Column(s) | Type | Rationale |
|---|---|---|---|---|
| `idx_products_category_id` | `products` | `category_id` | B-Tree | High-frequency category filter operations in catalog |
| `idx_products_base_price` | `products` | `base_price` | B-Tree | Range scanning for price sliders and budget limits |
| `idx_seller_prod_prod_id` | `seller_products` | `product_id, price` | Composite B-Tree | Fast lookup of best buy box price for any given ASIN |
| `idx_orders_buyer_id` | `orders` | `buyer_id, placed_at DESC` | Composite B-Tree | Fast retrieval of user order history in chronological order |
| `idx_prod_embedding_cosine`| `product_embeddings` | `embedding vector_cosine_ops` | HNSW / IVFFlat | Approximate nearest neighbor vector search using pgvector |

---

&copy; 2026 SmartCommerce Database Systems Engineering Group.
