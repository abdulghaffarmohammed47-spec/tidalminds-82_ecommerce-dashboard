# SmartCommerce X Implementation Report

## Scope

SmartCommerce X is an original synthetic-data multi-seller marketplace. PostgreSQL is the transactional source of truth; MongoDB stores flexible content; Redis provides cache and supporting runtime services.

## Verified Architecture

- React and Vite storefront
- FastAPI backend with SQLAlchemy and Alembic
- PostgreSQL/pgvector, MongoDB, and Redis Docker services
- JWT authentication, password hashing, and role checks
- Seller offers, warehouse inventory, and seller order splitting
- Row-level inventory locks using `SELECT FOR UPDATE`
- Payment simulation with success and failure state handling
- Hybrid/search and recommendation foundations
- Prometheus request metrics and service health endpoint
- Dockerized transactional outbox worker with Redis Stream publication
- Versioned `/api/v1` compatibility routes and measured component health endpoints
- PostgreSQL-backed wishlist with authenticated customer UI integration

## Checkout and Consistency

Checkout validates the server-side cart and active offer, locks inventory rows in deterministic order, reserves stock, creates the parent and seller orders, and commits atomically. Insufficient stock explicitly rolls back the SQLAlchemy session.

Checkout now accepts `Idempotency-Key`. The key and request hash are stored in PostgreSQL. Replays return the original order, while reuse with a different request is rejected. The same checkout transaction writes an `OrderCreated` outbox record, so the order and event cannot commit independently.

## Verification Evidence

- Backend suite: 23 tests passed
- Checkout/payment tests: 3 tests passed
- Frontend TypeScript/Vite build: passed
- Backend compilation and diagnostics: passed
- Live `/health`: PostgreSQL, MongoDB, and Redis healthy
- Frontend live page: rendered successfully after catalog price fallback fix
- Outbox worker: processed events published to Redis Stream; dead-letter state observed
- Browser smoke flows: home and product routes rendered without failed API responses or console warnings
- Payment authorization: cross-customer payment mutation rejected; order transition is row-locked
- Versioned API smoke check: `/api/v1/products/` returned HTTP 200
- Wishlist API: add/list/remove, duplicate rejection, and unauthenticated rejection passed
- Wishlist browser guard: unauthenticated `/wishlist` redirects to `/login`
- Coupon checkout: `WELCOME10`-style rules are validated server-side and redeemed atomically inside checkout; focused coupon tests pass
- Shipping tracking: seller-authorized mock shipment creation, tracking persistence, shipment events, customer ownership checks, and order-history display are implemented and tested

## Failure Behavior

MongoDB and Redis startup failures degrade those optional services instead of preventing core API startup. Semantic/recommendation features can fall back to normal catalog behavior where implemented. Payment failure does not mark an order paid and releases its reservation.

## Remaining Work

The attached production contract is broader than the currently verified implementation. Remaining work includes broader webhook/refund/return idempotency, complete document-level RAG security, external payment and shipping adapters, expanded Playwright/security/database integration coverage, production TLS/secrets/backups, and observability image deployment.

These items are recorded as IN PROGRESS or PENDING in `PROJECT_STATUS.md`; no unexecuted metrics or production claims are presented as complete.
