# Test Cases — SmartCommerce AI E-Commerce Platform

This document defines the complete test case matrix for the DBMS layer of the SmartCommerce AI platform. Test cases cover functional correctness, edge cases, ACID property validation, and performance benchmarks.

---

## Module 1: User Authentication & Management

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-01 | Register new user | Valid email + password | User created, password hashed, role=CUSTOMER | Write, Hash |
| TC-02 | Register duplicate email | Existing email | HTTP 409 Conflict — unique constraint violation | Unique Constraint |
| TC-03 | Login valid credentials | Correct email + password | JWT token returned | Index lookup on email |
| TC-04 | Login invalid password | Wrong password | HTTP 401 Unauthorized | Authentication |
| TC-05 | Login inactive user | Deactivated account | HTTP 403 Forbidden | is_active filter |
| TC-06 | Soft delete user | Admin deactivates user | is_active=FALSE, orders preserved | Soft Delete, Referential Integrity |

---

## Module 2: Product Catalog & Search

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-07 | List all products | GET /api/products | Paginated list with stock and category | View: v_product_catalog |
| TC-08 | Filter by category | category_id query param | Only products in that category | B-Tree index on category_id |
| TC-09 | Filter by price range | min_price=5000, max_price=50000 | Products within price range | Range query |
| TC-10 | Semantic search — exact match | query="Sony headphones" | Sony WH-1000XM5 in top results | pgvector cosine distance |
| TC-11 | Semantic search — conceptual | query="long flight accessories" | Headphones, neck pillow, travel kit | pgvector semantic similarity |
| TC-12 | Search with out-of-stock exclusion | query="gaming console" — PS5 out of stock | Xbox Series X returned, PS5 excluded | JOIN inventory WHERE available > 0 |
| TC-13 | Full-text fallback search | Model unavailable, query="laptop" | ILIKE match on title/brand | GIN full-text index |
| TC-14 | Get product by slug | /api/products/sony-wh-1000xm5 | Full product with specs from MongoDB | Slug index lookup + Mongo |
| TC-15 | Get similar products | product_id of laptop | Other laptops ordered by cosine distance | pgvector self-join |
| TC-16 | Category hierarchy | GET /api/products/categories | Nested tree structure | Recursive CTE |

---

## Module 3: Inventory Management

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-17 | Check available stock | variant_id | Integer: on_hand - reserved | fn_available_stock() |
| TC-18 | Restock variant | variant_id, qty=50 | on_hand += 50, movement record created | UPSERT (ON CONFLICT DO UPDATE) |
| TC-19 | Low stock alert | Product with on_hand=1, safety=2 | Appears in v_low_stock_alerts view | View, CHECK constraint |
| TC-20 | Out of stock alert | on_hand=reserved=0 | stock_status='OUT_OF_STOCK' | Computed column |
| TC-21 | Prevent negative stock | UPDATE on_hand = -1 | EXCEPTION raised by trigger | trg_prevent_negative_stock |
| TC-22 | Reserve stock | Checkout 3 units, stock=10 | reserved += 3, available = 7 | SELECT FOR UPDATE |
| TC-23 | Release reserved stock | Order cancelled | reserved -= qty, movement='RETURN_RESTOCK' | Compensating transaction |
| TC-24 | Inventory audit trail | View movements for variant | Chronological list of all changes | Audit log query |

---

## Module 4: Order Placement — ACID Transaction Tests

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-25 | Place valid order | Cart with 2 items, sufficient stock | Order CONFIRMED, inventory deducted | ACID Transaction |
| TC-26 | Place order — insufficient stock | Item qty > available | HTTP 400, full rollback, stock unchanged | Atomicity, FOR UPDATE |
| TC-27 | Place order — empty cart | No items | HTTP 400 "Cart is empty" | Validation |
| TC-28 | Cancel confirmed order | order_id | Status=CANCELLED, stock restored | sp_cancel_order, Compensation |
| TC-29 | Cancel shipped order | Shipped order | HTTP 400 "Cannot cancel in status SHIPPED" | State machine constraint |
| TC-30 | Order status history | Any order | Complete chronological status log | trg_log_order_status_change |
| TC-31 | New order notification | Place order | Notification record auto-created | trg_new_order_notification |

---

## Module 5: Concurrency — Race Condition Prevention

| TC# | Test Case | Setup | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-32 | **2 users, 1 item in stock** | Concurrent checkout of same variant, stock=1 | Exactly 1 succeeds, 1 gets "Insufficient Stock" | SELECT FOR UPDATE serialization |
| TC-33 | **100 users, 5 items in stock** | 100 concurrent checkout requests, stock=5 | Exactly 5 orders confirmed, 95 rejected | FOR UPDATE queue |
| TC-34 | **Concurrent restock + checkout** | Restock and checkout at same time | No negative stock, audit trail complete | Locking + check constraint |
| TC-35 | **Deadlock prevention** | Two transactions each locking different rows | No deadlock; PostgreSQL resolves via timeout | Transaction isolation |

### Concurrency Test Procedure

```python
# Run this test to prove TC-32/TC-33:
import asyncio, httpx

async def checkout_once(session_token: str) -> int:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:8000/api/orders/checkout",
            json=[{"variant_id": "VARIANT_UUID", "quantity": 1, "price": 29990}],
            headers={"Authorization": f"Bearer {session_token}"}
        )
        return r.status_code

# Simulate 10 concurrent users checking out the last item:
async def run_concurrency_test():
    tokens = [get_token(f"user{i}@test.com") for i in range(10)]
    results = await asyncio.gather(*[checkout_once(t) for t in tokens])
    successes = results.count(201)
    failures  = results.count(400)
    print(f"Successes: {successes}, Failures: {failures}")
    # Expected: Successes=1, Failures=9 (if stock=1)

asyncio.run(run_concurrency_test())
```

**Expected Result**: Exactly 1 HTTP 201 (Created), 9 HTTP 400 (Bad Request "Insufficient Stock"). Zero oversell.

---

## Module 6: Recommendations Engine

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-36 | Personalized recommendations | User with 3 search history entries | Products matching weighted interest vector | Composite vector, pgvector |
| TC-37 | New user — no history | No search history | Fallback: trending products from Redis | Redis ZSET fallback |
| TC-38 | Trending products | Popular products by view count | Sorted by Redis zincrby score | Redis analytics |
| TC-39 | Frequently bought together | product_id with order history | Co-occurring products with count > 1 | Self-join co-occurrence |
| TC-40 | Recently viewed | User viewed 5 products | Those 5 products in order of viewing | Redis list |
| TC-41 | In-stock alternatives | Out-of-stock product | Same-category in-stock alternatives | Inventory JOIN, category filter |

---

## Module 7: Analytics & Reporting

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-42 | Revenue by category | Admin dashboard | Per-category revenue, order count | v_revenue_by_category view |
| TC-43 | Sales leaderboard | Top 10 query | Products ranked by units sold | RANK() window function |
| TC-44 | Customer lifetime value | Top customers list | Sorted by total spend | v_customer_lifetime_value view |
| TC-45 | Category breadcrumb | category_id for sub-category | "Electronics > Audio & Headphones" | fn_category_breadcrumb, recursive CTE |
| TC-46 | Normalization check | Run Query 9 in advanced_queries.sql | 0 violations in all checks | Referential integrity |
| TC-47 | Inventory movement report | Variant movement history | Grouped by day and type | DATE_TRUNC, GROUP BY |

---

## Module 8: Database Integrity

| TC# | Test Case | Input | Expected Output | DBMS Concept |
|---|---|---|---|---|
| TC-48 | FK constraint: invalid category | Product with non-existent category_id | FOREIGN KEY violation | Referential integrity |
| TC-49 | Email format validation | Invalid email "notanemail" | CHECK constraint violation | Check constraint |
| TC-50 | Negative price | base_price = -100 | CHECK constraint violation | Check constraint |
| TC-51 | Category self-reference | parent_id = own id | EXCEPTION from trigger | trg_prevent_category_self_ref |
| TC-52 | Hard delete product with orders | DELETE from products | EXCEPTION from guard trigger | trg_guard_product_delete |
| TC-53 | Order item qty = 0 | INSERT order_item qty=0 | CHECK constraint violation | Check constraint + trigger |
| TC-54 | Auto inventory on new variant | INSERT product_variant | inventory row auto-created | trg_auto_create_inventory |

---

## Performance Benchmarks (Targets)

| Operation | Target Latency | Index Used |
|---|---|---|
| Login (email lookup) | < 5ms | `idx_users_email` (B-Tree) |
| Product page (slug lookup) | < 10ms | `idx_products_slug` (B-Tree) |
| Semantic search (pgvector) | < 50ms | `idx_product_embeddings_hnsw` (HNSW) |
| Checkout transaction | < 100ms | `FOR UPDATE` lock + B-Tree indexes |
| Low stock dashboard | < 20ms | `v_low_stock_alerts` view |
| Revenue by category | < 30ms | `v_revenue_by_category` view |
| Recommendation generation | < 150ms | pgvector + Redis |

---

## Test Results Summary

| Module | Total TCs | Pass | Fail | Notes |
|---|---|---|---|---|
| Authentication | 6 | — | — | Run with pytest |
| Product & Search | 10 | — | — | Requires seeded DB |
| Inventory | 8 | — | — | Requires V1–V3 migrations |
| Order / ACID | 7 | — | — | Core DBMS validation |
| **Concurrency** | **4** | — | — | **Key proof of ACID** |
| Recommendations | 6 | — | — | Requires seed_all.py |
| Analytics | 6 | — | — | Requires order seed data |
| DB Integrity | 7 | — | — | Run SQL directly in psql |
| **Total** | **54** | **—** | **—** | Fill after running |

> **Note**: Update the Pass/Fail columns after running the tests locally and during your demonstration. The concurrency test (TC-32/TC-33) is the most impactful to demonstrate live.
