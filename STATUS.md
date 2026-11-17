| Feature | State | Evidence |
|---|---|---|
| S0: Database Architecture & Setup | Complete | PostgreSQL + pgvector, MongoDB specs, Redis caching, migrations V1-V4 |
| S1: Catalog & Product Browsing | Complete | `ProductRepository`, 360-viewer, gallery, specs, seed products |
| S2: Semantic & Vector Search | Complete | HNSW cosine vector search, hybrid keyword/semantic search, recommendation engine |
| S3: Shopping Cart Management | Complete | Redis guest/user carts, cart merge, CRUD operations |
| S4: Orders & ACID Checkout | Complete | `OrderRepository`, seller order splitting, payment simulation state machine |
| S5: Concurrency & Stock Locks | Complete | `SELECT FOR UPDATE` row locking, warehouse & inventory movements, race-condition tests |
| S6: Auth & RBAC Security | Complete | JWT auth, role checker (`customer`, `seller`, `admin`), password hashing |
| S7: Analytics & Reporting | Complete | PostgreSQL views, sales leaderboard, revenue by category, CLV |
| S8: Seller Portal & Dashboard | Complete | Seller metrics, product listing creation, inventory adjustment, order status flow |
| S9: Storefront UI Polish & E2E | Complete | Live cart +/- qty, full checkout + payment simulation, OrderHistory (/orders), live cart badge, semantic/keyword search toggle |
| S10: Stress Test & Concurrency | Complete | Deterministic variant_id lock ordering, `test_concurrency_stress.py` (flash-sale & deadlock tests), `scripts/stress_test.py` CLI benchmark |
| S11: Deployment & Observability | Complete | Prometheus `/metrics` collector & middleware, `prometheus.yml`, Grafana provisioning & dashboard, updated `docker-compose.yml` |
| Checkout idempotency | Complete | `Idempotency-Key` replay protection, request hash validation, regression test |
| Transactional outbox write | Complete | `OrderCreated` event is persisted in the checkout transaction and tested |
| Full production contract | IN PROGRESS | Core marketplace and ACID flows are verified; workers, full API versioning, external providers, and broader security/E2E coverage remain |
