# SMARTCOMMERCE: AI-Powered Multi-Seller E-Commerce Marketplace & ACID DBMS Engine

> **Academic Course Project**: Database Systems Engineering / DBMS & Information Retrieval  
> **Architecture**: Amazon-Style Multi-Seller Marketplace &bull; 3NF Relational Engine (sql.js WebAssembly / PostgreSQL) &bull; Grounded Vector RAG &bull; Explainable Hybrid Recommendations &bull; ACID Concurrency Protection

---

## 1. Executive Summary & Project Vision

**SMARTCOMMERCE** is an academic engineering project demonstrating the seamless synergy between **rigorous relational database engineering (3NF / ACID transactions)**, **information retrieval (RAG with pgvector embeddings)**, **multi-factor recommendation systems**, and an authentic **Amazon-style multi-seller customer shopping experience**.

The system strictly adheres to the fundamental architectural separation of concerns:
- **AI Recommends & Explains**: Generates structured explanations based on verifiable user affinity vectors.
- **RAG Retrieves & Grounds**: Ingests manufacturer whitepapers, manuals, and warranty policies to produce cited answers with strict anti-hallucination guardrails.
- **Authoritative SQL Verifies Facts**: Real-time physical inventory, dynamic pricing, and multi-seller offers are queried directly from the relational ledger (`seller_products`, `inventory`).
- **Deterministic ACID Transactions**: Prevents race conditions and negative inventory via explicit `BEGIN TRANSACTION;` ... `COMMIT;` blocks with row checks.

---

## 2. Core Architectural Pillars

```
+--------------------------------------------------------------------------------+
|                                SMARTCOMMERCE                                   |
+--------------------------------------------------------------------------------+
                                       |
    +------------------+---------------+----------------+------------------+
    |                  |                                |                  |
+---v-------------+ +--v----------------+      +---------v------+   +----------v---------+
|  Storefront UI  | | Grounded Vector   |      | Explainable    |   | In-Memory WASM /   |
|  (Amazon-Style) | | RAG Copilot       |      | Recommendation |   | PostgreSQL Engine  |
|                 | | ("SmartAssist")   |      | Engine         |   |                    |
| - Header & Nav  | |                   |      |                |   | - 3NF Normalized   |
| - Buy Box       | | - 32D Embeddings  |      | Score =        |   | - CHECK Constraints|
| - Competing     | | - Cosine Sim      |      |   w1*Sim +     |   | - Row Locks        |
|   Sellers       | | - Citations       |      |   w2*Cat +     |   | - ACID Atomicity   |
| - Cart & Orders | | - Anti-Halluc     |      |   w3*Rating +  |   | - Zero Overselling |
+-----------------+ +-------------------+      |   w4*Stock     |   +--------------------+
                                               +----------------+
```

---

## 3. Database Specification (3NF Relational Schema)

The database schema is strictly normalized into Third Normal Form (3NF) and executed in-memory using `sql.js` WebAssembly:

1. **`users`** *(Authentication & Role-Based Access Control)*:
   - `user_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `email` (TEXT UNIQUE NOT NULL)
   - `password_hash` (TEXT NOT NULL)
   - `full_name` (TEXT NOT NULL)
   - `role` (TEXT NOT NULL CHECK (`role` IN ('CUSTOMER', 'SELLER', 'ADMIN')))
   - `created_at` (DATETIME DEFAULT CURRENT_TIMESTAMP)
2. **`categories`**:
   - `category_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `name` (TEXT UNIQUE NOT NULL)
3. **`products`**:
   - `product_id` (INTEGER PRIMARY KEY)
   - `category` (TEXT NOT NULL)
   - `title` (TEXT NOT NULL)
   - `description` (TEXT)
   - `base_price` (REAL NOT NULL)
   - `rating` (REAL DEFAULT 4.5)
   - `reviews_count` (INTEGER DEFAULT 120)
   - `image_url` (TEXT)
   - `specs_json` (TEXT)

3. **`seller_products`** *(Multi-Seller Inventory Isolation)*:
   - `offer_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `product_id` (INTEGER NOT NULL, FK to `products`)
   - `seller_id` (INTEGER NOT NULL)
   - `seller_name` (TEXT NOT NULL)
   - `price` (REAL NOT NULL)
   - `stock_quantity` (INTEGER NOT NULL CHECK (`stock_quantity` >= 0))
   - `delivery_days` (INTEGER DEFAULT 2)
4. **`inventory`** *(Physical Warehouse Stocks)*:
   - `warehouse_id` (INTEGER NOT NULL)
   - `product_id` (INTEGER NOT NULL, FK to `products`)
   - `stock_on_hand` (INTEGER NOT NULL CHECK (`stock_on_hand` >= 0))
   - `stock_reserved` (INTEGER DEFAULT 0)
   - PRIMARY KEY (`warehouse_id`, `product_id`)
5. **`orders`**:
   - `order_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `buyer_id` (INTEGER NOT NULL)
   - `total_amount` (REAL NOT NULL)
   - `shipping_address` (TEXT NOT NULL)
   - `order_status` (TEXT DEFAULT 'CONFIRMED')
   - `placed_at` (DATETIME DEFAULT CURRENT_TIMESTAMP)
6. **`order_items`**:
   - `item_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `order_id` (INTEGER NOT NULL, FK to `orders`)
   - `product_id` (INTEGER NOT NULL)
   - `seller_id` (INTEGER NOT NULL)
   - `quantity` (INTEGER NOT NULL)
   - `unit_price` (REAL NOT NULL)
7. **`coupons`**:
   - `code` (TEXT PRIMARY KEY)
   - `discount_type` (TEXT NOT NULL: `'PERCENTAGE'` | `'FLAT'`)
   - `value` (REAL NOT NULL)
8. **`reviews`**:
   - `review_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `product_id` (INTEGER NOT NULL)
   - `buyer_name` (TEXT NOT NULL)
   - `rating` (INTEGER NOT NULL)
   - `comment` (TEXT)
   - `verified_purchase` (INTEGER DEFAULT 1)

---

## 4. Key Functional Capabilities

### A. Authentic Amazon Storefront UI, Buy Box & 52-Product Multi-Category Catalog
- **Header Navigation**: Amazon Dark Navy (`#131921`) with location selector ("Deliver to Alex - Bengaluru 560001"), multi-department dropdown, search bar with NLP budget extraction & Voice Search, persona switcher, Returns & Orders modal trigger, wishlist badge, and cart counter.
- **Enterprise 52-Product Catalog Across ALL 16 Categories**:
  - **Laptops (4)**: QuantumBook Ultra 14 *(ACID Race item)*, ZenBook Pro 16X OLED, ThinkPad X1 Carbon Gen 12, ROG Strix SCAR 16 RTX 4080.
  - **Displays (3)**: ProView 34" Curved WQHD 165Hz, UltraSharp 32" 4K IPS Black, Odyssey OLED G9 49" Curved 240Hz.
  - **Audio (3)**: AeroSound X9 ANC Studio Headphones, SonicPro Master TWS, StudioCraft 5" Powered Reference Monitors.
  - **Peripherals (3)**: CyberKey Mechanical RGB Keyboard, LuminaDesk Asymmetric Monitor Bar Lamp, MasterGrip Pro Wireless Laser Mouse.
  - **Smart Devices (3)**: NovaWatch Ultra Titanium, SmartHub 10.1" Touch Display, AuraGlow Smart LED Bar.
  - **Electronics (3)**: WaveCast 4K Zero-Latency Transmitter, PowerMax 140W GaN Bank, Alpha 4K Mirrorless Camera.
  - **Home & Kitchen (4)**: KitchenMaster Dual-Zone Air Fryer 9L, IronClad Biometric Safe, RoboClean LiDAR Vacuum, UltraBreeze Bladeless Tower Fan.
  - **Beauty (3)**: SilkGlow Hyaluronic Peptide Serum, Botanical Renewal Retinol Cream, AeroStyler Multi-Styler.
  - **Sports & Fitness (4)**: FitPulse Smart Treadmill, HydroPeak UV-C Bottle, X-Grip Dumbbells 24kg, YogiMat Yoga Mat.
  - **Automotive (3)**: DashPro 4K Dual Lens Dashcam, MasterCraft 128-Pc Tool Kit, VoltBoost 2000A Jump Starter.
  - **Grocery (3)**: Gourmet Roast Ethiopian Coffee, Organic Valley Extra Virgin Olive Oil, Raw Manuka Honey MGO 550+.
  - **Fashion (3)**: Jordan Heritage Leather High-Top Sneakers, Heritage Selvedge Raw Denim, Promaster Eco-Drive Titanium Watch.
  - **Toys & Games (3)**: TitanFlight AI 4K Drone, NASA Apollo Saturn V 1969-Pc Set, OLED Handheld Gaming Console.
  - **Baby Care (3)**: BabyComfort 3-in-1 Stroller, SmartView HD Wi-Fi Monitor, All-in-One 4-Stage Convertible Car Seat.
  - **Health & Wellness (3)**: VelocityX Pro Percussion Gun, CardioCheck Arm BP Monitor, Prestige AI Sonic Toothbrush.
  - **Office & Industrial (4)**: Ergonomic Pro Mesh Chair, Aeron Kinetic Desk Chair, Dual-Motor Standing Desk, AutoMax 100M Shredder.
- **Iconic Amazon Buy Box**: Right-hand column with real-time stock levels, seller selection, Prime delivery guarantees, quantity selector, yellow **Add to Cart** (`#ffd814`), and orange **Buy Now** (`#ffa41c`).
- **Other Sellers on SmartCommerce**: Side-by-side comparison of competing seller offers by price, lead time, and stock.

### B. Photorealistic 360-Degree Product Spin Viewer (Real Image Engine)
- **Actual Product Photography Rendering**: The 360 viewer directly renders the authentic product image on top of a realistic showroom glass turntable disc, replacing geometric placeholder boxes.
- **Grounded Pedestal Physics**: Product sits firmly on the turntable surface with a dynamically squashing/stretching ground contact shadow (`(targetW * 0.48 * |cosA|) + 18`).
- **Luxury Showroom Glass Reflection**: An inverted, semi-transparent reflection (`ctx.scale(cosA, -0.32)`, `alpha = 0.20`) clipped directly within the top glass turntable disc.
- **3D Perspective Yaw Rotation**: Continuous horizontal scaling by $\cos(\theta)$ as the user drags horizontally, with dynamic specular light glare sweeping across the photo.
- **Engineered Rear Chassis Backplate**: When rotated past $90^\circ$ to $270^\circ$, renders an authentic rear metallic chassis with brand typography, model number, cooling vents, and custom colorway finish (**Midnight Onyx**, **Space Silver**, **Cosmic Blue**, **Rose Gold**).
- **Azimuth Compass HUD**: Compass dial in the upper left with a rotating red needle and continuous degree readout (`0° FRONT`, `90° RIGHT`, `180° REAR`, `270° LEFT`).
- **Multi-Level Zoom**: Interactive scaling controls (`0.6x` to `2.0x`) for close-up inspection.

### C. Complete Authentication & Role-Based Access Control (RBAC)
- **Relational `users` Ledger**: Backed by SQLite WASM with unique email constraints, password hash storage, full names, roles (`CUSTOMER`, `SELLER`, `ADMIN`), and timestamps.
- **Sign In & Register Modal**: Multi-tab authentication dialog with real-time validation, password verification, and instant session synchronization.
- **Pre-Seeded Demo Accounts & One-Click Login**:
  - **Alex Chen** (`alex@smartcommerce.dev` / `Customer123!`) - Customer Role (auto-switches persona)
  - **Sarah Miller** (`sarah@smartcommerce.dev` / `Customer123!`) - Customer Role
  - **Marcus Vance** (`marcus@smartcommerce.dev` / `Customer123!`) - Customer Role
  - **PrimeTech Solutions** (`seller@primetech.com` / `Seller123!`) - Merchant Role
  - **CloudRetail Direct** (`seller2@cloudretail.com` / `Seller123!`) - Merchant Role
  - **Platform Administrator** (`admin@smartcommerce.dev` / `Admin123!`) - Admin Role
- **Session State Management**: Dynamic navigation bar with user greetings ("Hello, Alex"), role badge in account menu, and RBAC guards protecting Seller Central and Admin Portals.

### D. Grounded Vector RAG & Shopping Copilot ("SmartAssist")
- **Indexed Whitepaper Chunks**: Hardware whitepapers (ZenBook Pro dual Thunderbolt 4 display capabilities, QuantumBook secondary M.2 NVMe SSD expansion, AeroSound acoustic driver warranty, Universal 10-day return policy).
- **Cosine Similarity Retrieval**: Uses 32-dimensional synthetic embeddings to match user queries with verified knowledge chunks.
- **Strict Anti-Hallucination Guardrail**: Queries with insufficient evidence (similarity < 0.30) are rejected with a clear explanation rather than fabricated.
- **Authoritative SQL Lookup**: Questions regarding pricing and current stock bypass document text and execute direct SQL queries against `seller_products`.

### E. Explainable Hybrid Recommendations
- **Dynamic Formula**:
  $$\text{Score} = w_1 \cdot \text{CosineSim} + w_2 \cdot \text{CategoryAffinity} + w_3 \cdot \text{NormalizedRating} + w_4 \cdot \text{StockBonus}$$
- **Persona Contexts**: Alex Chen (Coder / Laptops & Displays), Sarah Miller (Sound Designer / Audio & Peripherals), Marcus Vance (Athlete / Sports & Fitness).
- **Interactive Weight Tuner**: Sliders in the AWS RDS Dev Studio allow real-time tuning of $w_1, w_2, w_3, w_4$.

### F. ACID Concurrency Race Engine (Review-3 Defense)
- Demonstrates race condition prevention: Product #17 (*QuantumBook Ultra 14*) has `stock_quantity = 1` for Seller 1.
- Simultaneous simulated checkouts from Customer A and Customer B execute interleaved SQL statements.
- Customer A acquires the lock, checks `1 >= 1`, decrements stock to 0, and executes `COMMIT;`.
- Customer B checks `0 < 1`, encounters a check constraint violation, and executes `ROLLBACK;`.
- Interactive terminal output provides colored logs and verifies that inventory never becomes negative.

### G. Seller Central & Admin Portals
- **Seller Central**: Row-level isolated inventory management for active merchants (PrimeTech Solutions, CloudRetail Direct, ApexDeals India) with an instant "+5 Units" restock action.
- **Admin Portal**: Platform-wide metrics (Gross GMV, Catalog SKUs, Indexed RAG Chunks, ACID Integrity Score), dynamic category creation, and custom whitepaper chunk ingestion.

### H. Side-by-Side Product Comparison Matrix
- **Compare with Similar Items**: Dynamically pairs the selected product with two other items from the same or related category directly inside the product modal.
- **Side-by-Side Metrics**: Cross-compares product thumbnails, titles, star ratings, review counts, Buy Box lowest pricing, Prime delivery lead times, multi-seller stock status, and provides an instant "Add to Cart" CTA for each item.

### I. Customer Reviews & 5-Star Rating Breakdown
- **Rating Distribution Histogram**: Visual progress bars representing 5★, 4★, 3★, 2★, and 1★ customer rating percentages computed dynamically from the SQLite `reviews` table.
- **Live Review Submission Dialog**: Verified customer review modal allowing buyers to select star ratings (1–5), provide written commentary, and submit. The system executes `INSERT INTO reviews`, recalculates the product's average rating in real-time, and updates both the modal and catalog cards.

### J. Advanced 360° Viewer (Multi-Level Zoom & Colorways)
- **Canvas Zoom Control**: Smooth zoom scaling (`0.6x` to `2.0x`) using HTML5 Canvas 2D scale transformation.
- **Colorway / Finish Switcher**: Instant switching between 4 finishes (**Midnight Onyx**, **Space Silver**, **Cosmic Blue**, **Rose Gold**) which interactively updates the turntable lighting model and specular shading gradients.

### K. Interactive SQL Query Console (AWS RDS Studio)
- **Direct DBMS Querying**: Tab 5 in the AWS RDS Dev Studio provides a full SQL query editor connected to the in-memory SQLite WASM engine.
- **Pre-Configured Presets**: Low stock alerts, category pricing aggregations, customer order ledgers, and multi-seller price comparisons.
- **Execution Telemetry**: Displays query runtime in milliseconds (`Executed in 0.42ms`) and dynamically formats result sets into interactive data grids.

### L. Order Tracking Timeline & Amazon-Style Tax Invoice
- **4-Stage Delivery Tracking**: Visual milestone tracker (*Ordered* &rarr; *Dispatched* &rarr; *In Transit* &rarr; *Delivered*) with carrier partner details (*SmartCommerce Prime Air Express*), unique Air Waybill tracking numbers, and delivery confirmation.
- **Official Tax Invoice Modal**: Printable Amazon India tax invoice with seller GSTIN, billing address, line items, and itemized Indian GST tax breakdown (CGST 9% + SGST 9%).

### M. Voice Search (Speech-to-Text) & Hero Deals Carousel
- **Web Speech Recognition**: Search bar microphone button with animated listening pulses and automatic speech-to-text transcription.
- **Hero Deals Banner Carousel**: 3 cycling promotional slides with category deep-links, next/prev arrow buttons, and indicator dots that auto-advance every 7 seconds.


---

## 5. How to Run Locally

### Option 1: Standalone Browser Launch (Zero-Configuration)
Since `index.html` is fully self-contained with CDN-based libraries (Tailwind CSS, Lucide Icons, and sql.js WASM):
1. Simply double-click `index.html` or open it in any modern web browser (Chrome, Edge, Firefox, Safari).

### Option 2: Local HTTP Server (Recommended)
```bash
# In the repository root
python -m http.server 8088
```
Navigate to:
```
http://localhost:8088/index.html
```

### Railway deployment

The React storefront and FastAPI service have separate production Dockerfiles
for Railway. See [docs/deployment/RAILWAY.md](docs/deployment/RAILWAY.md) for
service setup, required secrets, database migrations, and health checks.

---

## 6. Automated Benchmark & Academic Evaluation Suite

Access the built-in **Academic Benchmark** tab in the **RDS & ACID Race** developer studio to run the automated test suite:

| Test ID | Test Name | Target Requirement | Status |
|---|---|---|---|
| **RAG-01** | Hardware Specification Grounding | ZenBook dual external 4K 60Hz display support via Thunderbolt 4 | **PASSED** |
| **RAG-02** | Anti-Hallucination Refusal | Unknown coffee-maker specification rejected | **PASSED** |
| **RAG-03** | Real-Time Authoritative SQL Lookup | Live physical inventory queried from `seller_products` | **PASSED** |
| **ACID-01** | Negative Stock Prevention | Check constraint `stock_quantity >= 0` enforced with rollback | **PASSED** |
| **SEC-01** | Multi-Seller Row-Level Isolation | Seller 1 cannot view or modify Seller 2 private listings | **PASSED** |
| **NLP-01** | NLP Budget Intent Extraction | Parses "laptop under 80000" into category and budget | **PASSED** |

---

## 7. Technology Stack Summary

| Layer | Technologies |
|---|---|
| **Frontend UI** | HTML5, Tailwind CSS CDN, Lucide Icons, Custom Amazon Ember Styling |
| **Database Engine** | SQLite WebAssembly (`sql.js` v1.8.0), 3NF Relational Tables, ACID Transactions |
| **Information Retrieval** | 32-Dimensional Vector Space, Cosine Similarity, Grounded RAG Pipeline |
| **Concurrency Control** | Explicit `BEGIN TRANSACTION;` ... `COMMIT;` / `ROLLBACK;`, CHECK constraints |
| **Analytics & Telemetry** | Multi-Buyer Personas, Explainable Recommendation Formulas, GMV Tracking |

---

&copy; 2026 SmartCommerce Systems Engineering Group. All rights reserved.