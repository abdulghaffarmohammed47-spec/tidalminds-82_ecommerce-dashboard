import os
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Original index.html length:", len(html))

# -----------------------------------------------------------------------------
# 1. ADD VOICE SEARCH BUTTON TO SEARCH BAR
# -----------------------------------------------------------------------------
voice_btn_html = '''          <button 
            id="voice-search-btn" 
            onclick="startVoiceSearch()" 
            class="bg-white hover:bg-gray-100 text-gray-500 hover:text-amazon-amber px-2.5 py-2 flex items-center justify-center transition border-l border-gray-200"
            title="Search with your voice (Voice AI)"
          >
            <i data-lucide="mic" id="voice-search-icon" class="w-4 h-4"></i>
          </button>
          <button'''

if 'id="voice-search-btn"' not in html:
    html = html.replace('class="bg-amazon-amber hover:bg-amazon-amberHover px-4 py-2 rounded-r-md', voice_btn_html + ' class="bg-amazon-amber hover:bg-amazon-amberHover px-4 py-2 rounded-r-md', 1)
    print("[1] Voice search button injected.")

# -----------------------------------------------------------------------------
# 2. ENHANCE HERO BANNER WITH INTERACTIVE DEALS CAROUSEL
# -----------------------------------------------------------------------------
hero_carousel_html = '''    <!-- Hero Banner with Interactive Deals Carousel (Amazon Style) -->
    <section id="hero-banner" class="relative rounded-lg overflow-hidden mb-6 bg-gradient-to-r from-[#1b2838] via-[#232f3e] to-[#0d141e] text-white p-6 md:p-8 shadow-sm">
      <div id="hero-carousel-slides">
        <!-- Slide 1: Super Tech Days -->
        <div id="hero-slide-1" class="hero-slide max-w-3xl relative z-10 transition-opacity duration-300">
          <div class="inline-flex items-center gap-2 bg-amazon-amber/20 border border-amazon-amber/40 text-amazon-amber text-xs font-bold px-3 py-1 rounded-full mb-3">
            <i data-lucide="cpu" class="w-3.5 h-3.5"></i> Super Tech Days &bull; A–Z Hardware Catalog &bull; 360° Inspection
          </div>
          <h1 class="text-2xl md:text-4xl font-extrabold tracking-tight mb-2">
            Enterprise Multi-Seller E-Commerce with 360° Inspection
          </h1>
          <p class="text-gray-300 text-sm md:text-base mb-4 leading-relaxed">
            Experience interactive 360-degree product geometry, verifiable 3NF relational transactions, vector RAG grounding, and mathematically explainable recommendations.
          </p>
          <div class="flex flex-wrap gap-2.5">
            <button onclick="openSmartAssistDrawer()" class="bg-amazon-amber hover:bg-amazon-amberHover text-gray-950 font-bold text-xs md:text-sm px-5 py-2.5 rounded-full flex items-center gap-2 shadow transition">
              <i data-lucide="message-square" class="w-4 h-4"></i> Consult SmartAssist AI
            </button>
            <button onclick="openDevStudio('concurrency')" class="bg-gray-800/80 hover:bg-gray-700 text-white font-semibold text-xs md:text-sm px-4 py-2.5 rounded-full border border-gray-600 flex items-center gap-2 transition">
              <i data-lucide="zap" class="w-4 h-4 text-yellow-400"></i> Run ACID Race Test (Stock=1)
            </button>
            <button onclick="openDevStudio('sqlconsole')" class="bg-emerald-800/80 hover:bg-emerald-700 text-white font-semibold text-xs md:text-sm px-4 py-2.5 rounded-full border border-emerald-600 flex items-center gap-2 transition">
              <i data-lucide="terminal" class="w-4 h-4 text-emerald-300"></i> Interactive SQL Console
            </button>
          </div>
        </div>

        <!-- Slide 2: Audio Festival -->
        <div id="hero-slide-2" class="hero-slide max-w-3xl relative z-10 hidden transition-opacity duration-300">
          <div class="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-400/40 text-purple-300 text-xs font-bold px-3 py-1 rounded-full mb-3">
            <i data-lucide="headphones" class="w-3.5 h-3.5"></i> Acoustic &amp; Studio Audio Fest &bull; Up to 35% Off
          </div>
          <h1 class="text-2xl md:text-4xl font-extrabold tracking-tight mb-2">
            AeroSound X9 Studio ANC Headphones
          </h1>
          <p class="text-gray-300 text-sm md:text-base mb-4 leading-relaxed">
            Lossless LDAC audio, 45mm Beryllium custom drivers, and 55-hour battery life. Certified Prime Same-Day delivery with 360-degree interactive preview.
          </p>
          <div class="flex flex-wrap gap-2.5">
            <button onclick="openProductModal(1)" class="bg-amazon-amber hover:bg-amazon-amberHover text-gray-950 font-bold text-xs md:text-sm px-5 py-2.5 rounded-full flex items-center gap-2 shadow transition">
              <i data-lucide="eye" class="w-4 h-4"></i> View AeroSound X9 in 360°
            </button>
            <button onclick="filterByCategory('Audio')" class="bg-gray-800/80 hover:bg-gray-700 text-white font-semibold text-xs md:text-sm px-4 py-2.5 rounded-full border border-gray-600 flex items-center gap-2 transition">
              <i data-lucide="disc" class="w-4 h-4 text-purple-400"></i> Explore All Audio SKUs
            </button>
          </div>
        </div>

        <!-- Slide 3: Smart Living & Fitness -->
        <div id="hero-slide-3" class="hero-slide max-w-3xl relative z-10 hidden transition-opacity duration-300">
          <div class="inline-flex items-center gap-2 bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-bold px-3 py-1 rounded-full mb-3">
            <i data-lucide="activity" class="w-3.5 h-3.5"></i> Smart Home &amp; Pro Fitness Deals &bull; Flat ₹500 Off with FLAT500
          </div>
          <h1 class="text-2xl md:text-4xl font-extrabold tracking-tight mb-2">
            Elevate Your Productivity, Fitness &amp; Home
          </h1>
          <p class="text-gray-300 text-sm md:text-base mb-4 leading-relaxed">
            From FitPulse Treadmills and RoboClean LiDAR Vacuums to Ergonomic Mesh Chairs. Backed by guaranteed transactional ACID inventory reservation.
          </p>
          <div class="flex flex-wrap gap-2.5">
            <button onclick="filterByCategory('Sports & Fitness')" class="bg-amazon-amber hover:bg-amazon-amberHover text-gray-950 font-bold text-xs md:text-sm px-5 py-2.5 rounded-full flex items-center gap-2 shadow transition">
              <i data-lucide="dumbbell" class="w-4 h-4"></i> Fitness Equipment
            </button>
            <button onclick="filterByCategory('Home & Kitchen')" class="bg-gray-800/80 hover:bg-gray-700 text-white font-semibold text-xs md:text-sm px-4 py-2.5 rounded-full border border-gray-600 flex items-center gap-2 transition">
              <i data-lucide="home" class="w-4 h-4 text-emerald-400"></i> Smart Home Appliances
            </button>
          </div>
        </div>
      </div>

      <!-- Carousel Navigation Dots & Controls -->
      <div class="absolute bottom-4 right-6 flex items-center gap-2 z-20">
        <button onclick="prevHeroSlide()" class="w-7 h-7 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center text-white transition text-xs">
          <i data-lucide="chevron-left" class="w-4 h-4"></i>
        </button>
        <div class="flex items-center gap-1.5 px-2">
          <span id="hero-dot-1" onclick="setHeroSlide(1)" class="w-2.5 h-2.5 rounded-full bg-amazon-amber cursor-pointer transition"></span>
          <span id="hero-dot-2" onclick="setHeroSlide(2)" class="w-2.5 h-2.5 rounded-full bg-white/40 hover:bg-white cursor-pointer transition"></span>
          <span id="hero-dot-3" onclick="setHeroSlide(3)" class="w-2.5 h-2.5 rounded-full bg-white/40 hover:bg-white cursor-pointer transition"></span>
        </div>
        <button onclick="nextHeroSlide()" class="w-7 h-7 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center text-white transition text-xs">
          <i data-lucide="chevron-right" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="absolute right-0 top-0 bottom-0 w-1/3 hidden lg:flex items-center justify-end pr-10 opacity-20 pointer-events-none">
        <i data-lucide="layers" class="w-72 h-72 text-gray-400"></i>
      </div>
    </section>'''

# Replace old hero banner
old_hero_pattern = re.compile(r'<section id="hero-banner".*?</section>', re.DOTALL)
if old_hero_pattern.search(html):
    html = old_hero_pattern.sub(hero_carousel_html, html, count=1)
    print("[2] Hero Deals Carousel injected.")

# -----------------------------------------------------------------------------
# 3. ENHANCE 360° CANVAS CONTROLS WITH ZOOM & COLORWAY SELECTOR
# -----------------------------------------------------------------------------
enhanced_360_controls = '''            <!-- 360 Floating Controls Overlay with Zoom & Colorway Switcher -->
            <div class="w-full space-y-2 mt-2 pt-2 border-t border-gray-300 text-xs">
              <!-- Top Row: Spin controls & Zoom -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1">
                  <button onclick="toggle360AutoSpin()" id="btn-autospin" class="bg-white hover:bg-gray-100 text-gray-800 font-semibold px-2.5 py-1 rounded border border-gray-300 flex items-center gap-1 text-[11px]">
                    <i data-lucide="play" class="w-3 h-3 text-emerald-600"></i> Auto-Spin
                  </button>
                  <button onclick="reset360View()" class="bg-white hover:bg-gray-100 text-gray-800 px-2 py-1 rounded border border-gray-300 text-[11px]">
                    Reset
                  </button>
                </div>

                <!-- Zoom Controls -->
                <div class="flex items-center gap-1 bg-white px-2 py-0.5 rounded border border-gray-300">
                  <span class="text-[10px] text-gray-500 font-semibold mr-1">Zoom:</span>
                  <button onclick="zoom360(-0.2)" class="w-5 h-5 flex items-center justify-center font-bold text-gray-700 hover:bg-gray-100 rounded text-xs">-</button>
                  <span id="zoom-level-indicator" class="text-[10px] font-mono w-7 text-center font-bold">1.0x</span>
                  <button onclick="zoom360(0.2)" class="w-5 h-5 flex items-center justify-center font-bold text-gray-700 hover:bg-gray-100 rounded text-xs">+</button>
                </div>

                <!-- Quick Angle Snap Buttons -->
                <div class="flex items-center gap-1 text-[10px]">
                  <button onclick="set360Angle(0)" class="bg-white px-1.5 py-0.5 rounded border border-gray-300 font-semibold">0°</button>
                  <button onclick="set360Angle(90)" class="bg-white px-1.5 py-0.5 rounded border border-gray-300 font-semibold">90°</button>
                  <button onclick="set360Angle(180)" class="bg-white px-1.5 py-0.5 rounded border border-gray-300 font-semibold">180°</button>
                  <button onclick="set360Angle(270)" class="bg-white px-1.5 py-0.5 rounded border border-gray-300 font-semibold">270°</button>
                </div>
              </div>

              <!-- Bottom Row: Colorway Finish Selector -->
              <div class="flex items-center justify-between bg-white/80 p-1.5 rounded border border-gray-200">
                <span class="text-[10px] text-gray-600 font-semibold flex items-center gap-1">
                  <i data-lucide="palette" class="w-3 h-3 text-indigo-600"></i> Colorway Finish:
                </span>
                <div class="flex items-center gap-2">
                  <button onclick="set360Colorway('onyx')" class="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-gray-400 bg-gray-900 text-white font-medium" id="cw-btn-onyx">
                    <span class="w-2.5 h-2.5 rounded-full bg-black border border-gray-400"></span> Onyx
                  </button>
                  <button onclick="set360Colorway('silver')" class="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-800 font-medium hover:bg-gray-50" id="cw-btn-silver">
                    <span class="w-2.5 h-2.5 rounded-full bg-slate-300 border border-gray-400"></span> Silver
                  </button>
                  <button onclick="set360Colorway('blue')" class="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-800 font-medium hover:bg-gray-50" id="cw-btn-blue">
                    <span class="w-2.5 h-2.5 rounded-full bg-blue-600 border border-gray-400"></span> Blue
                  </button>
                  <button onclick="set360Colorway('gold')" class="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-800 font-medium hover:bg-gray-50" id="cw-btn-gold">
                    <span class="w-2.5 h-2.5 rounded-full bg-amber-600 border border-gray-400"></span> Gold
                  </button>
                </div>
              </div>
            </div>'''

old_360_controls_pattern = re.compile(r'<!-- 360 Floating Controls Overlay -->.*?<!-- Quick Angle Snap Buttons -->.*?</div>\s*</div>', re.DOTALL)
if old_360_controls_pattern.search(html):
    html = old_360_controls_pattern.sub(enhanced_360_controls, html, count=1)
    print("[3] Enhanced 360° Zoom & Colorway controls injected.")

# -----------------------------------------------------------------------------
# 4. INJECT COMPARISON MATRIX & CUSTOMER REVIEWS HISTOGRAM IN PRODUCT MODAL
# -----------------------------------------------------------------------------
modal_enhancements_html = '''      <!-- Other Competing Sellers Section -->
      <div class="p-6 border-t border-gray-200 bg-gray-50">
        <h3 class="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
          <i data-lucide="users" class="w-4 h-4 text-amazon-link"></i>
          <span>Other Sellers on SmartCommerce</span>
          <span class="text-xs text-gray-500 font-normal">(Compare prices &amp; delivery)</span>
        </h3>
        <div id="modal-other-sellers" class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <!-- Dynamic seller offer cards -->
        </div>
      </div>

      <!-- SIDE-BY-SIDE PRODUCT COMPARISON MATRIX SECTION -->
      <div id="modal-comparison-section" class="p-6 border-t border-gray-200 bg-white">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
              <i data-lucide="git-compare" class="w-4 h-4 text-indigo-600"></i>
              <span>Compare with Similar Items</span>
            </h3>
            <p class="text-xs text-gray-500">Side-by-side technical specs, pricing spread, and fulfillment speed</p>
          </div>
          <span class="text-xs font-semibold bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded border border-indigo-200">Interactive Spec Matrix</span>
        </div>
        
        <div class="overflow-x-auto border border-gray-200 rounded-lg">
          <table class="w-full text-xs text-left" id="modal-comparison-table">
            <!-- Rendered dynamically -->
          </table>
        </div>
      </div>

      <!-- CUSTOMER REVIEWS & 5-STAR RATING BREAKDOWN HISTOGRAM SECTION -->
      <div id="modal-reviews-section" class="p-6 border-t border-gray-200 bg-gray-50">
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-6">
          
          <!-- Rating Breakdown Summary Column -->
          <div class="md:w-1/3 bg-white p-4 rounded-lg border border-gray-200 space-y-3">
            <h3 class="font-bold text-sm text-gray-900 flex items-center gap-2">
              <i data-lucide="star" class="w-4 h-4 text-amazon-amber fill-amazon-amber"></i> Customer Reviews
            </h3>
            <div class="flex items-baseline gap-2">
              <span class="text-3xl font-black text-gray-900" id="reviews-avg-rating">4.8</span>
              <span class="text-xs text-gray-500">out of 5</span>
            </div>
            <div id="reviews-stars-summary" class="flex text-amazon-amber"></div>
            <span class="text-xs text-gray-500 block" id="reviews-total-count">512 global ratings</span>

            <!-- Rating Progress Histogram -->
            <div class="space-y-1.5 pt-2 border-t border-gray-200" id="reviews-histogram-bars">
              <!-- Rendered dynamically: 5 star, 4 star, 3 star, 2 star, 1 star -->
            </div>

            <div class="pt-2 border-t border-gray-200">
              <button onclick="openWriteReviewModal()" class="w-full bg-white hover:bg-gray-100 text-gray-900 font-bold py-2 px-3 rounded border border-gray-300 text-xs shadow-sm flex items-center justify-center gap-1.5 transition">
                <i data-lucide="edit-3" class="w-3.5 h-3.5 text-blue-600"></i> Write a Customer Review
              </button>
            </div>
          </div>

          <!-- Customer Reviews Feed Column -->
          <div class="md:w-2/3 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="font-bold text-xs text-gray-900 uppercase tracking-wider">Top Verified Purchase Reviews</h4>
              <span class="text-[11px] text-gray-500">Stored in 3NF <code class="font-mono text-gray-800">reviews</code> table</span>
            </div>
            <div id="modal-reviews-list" class="space-y-3 max-h-80 overflow-y-auto pr-1">
              <!-- Rendered dynamically -->
            </div>
          </div>

        </div>
      </div>'''

old_sellers_section_pattern = re.compile(r'<!-- Other Competing Sellers Section -->.*?<div id="modal-other-sellers".*?</div>\s*</div>', re.DOTALL)
if old_sellers_section_pattern.search(html):
    html = old_sellers_section_pattern.sub(modal_enhancements_html, html, count=1)
    print("[4] Product Comparison Matrix & Customer Reviews Histogram injected.")

# -----------------------------------------------------------------------------
# 5. INJECT TAB 5: INTERACTIVE SQL QUERY CONSOLE IN DEV STUDIO
# -----------------------------------------------------------------------------
sql_tab_btn = '''      <button id="tab-btn-weights" onclick="switchDevTab('weights')" class="px-4 py-2.5 font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200">
        Hybrid Weights
      </button>
      <button id="tab-btn-sqlconsole" onclick="switchDevTab('sqlconsole')" class="px-4 py-2.5 font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200">
        SQL Console
      </button>'''

html = html.replace('''      <button id="tab-btn-weights" onclick="switchDevTab('weights')" class="px-4 py-2.5 font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200">
        Hybrid Weights
      </button>''', sql_tab_btn, 1)

sql_console_panel = '''      <!-- TAB 5: INTERACTIVE SQL QUERY CONSOLE -->
      <div id="dev-tab-sqlconsole" class="hidden space-y-4">
        <div class="bg-gray-800/80 p-3.5 rounded border border-gray-700">
          <h4 class="font-bold text-amazon-amber text-xs mb-1 flex items-center gap-1.5">
            <i data-lucide="terminal" class="w-4 h-4"></i> Interactive SQLite / PostgreSQL WASM Console
          </h4>
          <p class="text-gray-300 text-[11px] leading-relaxed">
            Execute ad-hoc SQL queries directly against the in-memory 3NF relational engine. Supports JOINs, aggregations, window functions, and transaction inspection.
          </p>
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <label class="text-gray-400 text-xs font-semibold">SQL Query Statement:</label>
            <div class="flex items-center gap-1.5">
              <span class="text-gray-400 text-[11px]">Presets:</span>
              <select id="sql-query-presets" onchange="loadSqlPreset(this.value)" class="bg-gray-800 text-gray-200 border border-gray-700 rounded px-2 py-0.5 text-xs outline-none">
                <option value="">-- Choose Sample Query --</option>
                <option value="low_stock">1. Low Stock &amp; Multi-Seller Offers</option>
                <option value="category_summary">2. Category Inventory &amp; Pricing Aggregates</option>
                <option value="orders_buyers">3. Order Fulfillment &amp; Buyer Ledgers</option>
                <option value="quantum_race">4. QuantumBook Multi-Seller Offer Spread</option>
                <option value="top_reviews">5. Top Rated Products with Review Counts</option>
              </select>
            </div>
          </div>

          <textarea id="sql-console-input" rows="4" class="w-full bg-black text-emerald-400 font-mono text-xs p-3 rounded border border-gray-800 focus:border-amazon-amber outline-none leading-relaxed" spellcheck="false">SELECT p.product_id, p.title, sp.seller_name, sp.price, sp.stock_quantity 
FROM products p 
JOIN seller_products sp ON p.product_id = sp.product_id 
WHERE sp.stock_quantity <= 2;</textarea>

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <button onclick="executeAdhocSql()" class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded text-xs flex items-center gap-1.5 transition">
                <i data-lucide="play" class="w-3.5 h-3.5"></i> Run SQL Query
              </button>
              <button onclick="document.getElementById('sql-console-input').value = 'SELECT * FROM products LIMIT 5;'" class="bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-2 rounded text-xs border border-gray-700">
                Clear / Reset
              </button>
            </div>
            <span id="sql-execution-stats" class="text-gray-400 text-[11px] font-mono">Ready to execute</span>
          </div>
        </div>

        <!-- Query Output Grid -->
        <div class="border border-gray-800 rounded-lg overflow-hidden bg-gray-950">
          <div class="bg-black px-3 py-1.5 border-b border-gray-800 text-[10px] text-gray-400 flex items-center justify-between">
            <span>QUERY RESULTS &bull; RESULT SET</span>
            <span id="sql-rows-badge" class="text-amazon-amber font-mono">0 rows</span>
          </div>
          <div class="max-h-64 overflow-auto">
            <table class="w-full text-left text-[11px]">
              <thead id="sql-results-head" class="bg-gray-900 text-gray-400 sticky top-0 uppercase font-mono"></thead>
              <tbody id="sql-results-body" class="divide-y divide-gray-800 text-gray-300 font-mono">
                <tr><td class="p-3 text-gray-500 text-center italic">Run a query to view live result set</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>'''

# Inject before dev-tab-eval
html = html.replace('      <!-- TAB 4: ACADEMIC EVALUATION & BENCHMARK SUITE -->', sql_console_panel + '\n\n      <!-- TAB 4: ACADEMIC EVALUATION & BENCHMARK SUITE -->', 1)
print("[5] Interactive SQL Query Console injected into Dev Studio.")

# -----------------------------------------------------------------------------
# 6. INJECT NEW MODALS: WRITE REVIEW, ORDER TRACKING, ORDER INVOICE
# -----------------------------------------------------------------------------
additional_modals_html = '''  <!-- ================= WRITE CUSTOMER REVIEW MODAL ================= -->
  <div id="write-review-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-lg w-full p-6 shadow-2xl border border-gray-300">
      <div class="flex items-center justify-between pb-3 border-b border-gray-200">
        <h3 class="font-bold text-sm text-gray-900 flex items-center gap-2">
          <i data-lucide="edit-3" class="w-4 h-4 text-amazon-amber"></i> Write a Verified Customer Review
        </h3>
        <button onclick="closeWriteReviewModal()" class="text-gray-400 hover:text-gray-800"><i data-lucide="x" class="w-5 h-5"></i></button>
      </div>

      <form id="write-review-form" onsubmit="handleReviewSubmit(event)" class="py-4 space-y-4 text-xs">
        <div>
          <span class="text-gray-500 text-[11px] block">Reviewing Item:</span>
          <span class="font-bold text-gray-900 text-xs" id="review-modal-product-title">Product Title</span>
        </div>

        <div>
          <label class="block font-semibold text-gray-700 mb-1">Overall Rating:</label>
          <div class="flex items-center gap-1.5" id="review-rating-stars-input">
            <button type="button" onclick="setReviewRating(1)" class="text-2xl text-gray-300 hover:text-amazon-amber transition" id="star-btn-1">★</button>
            <button type="button" onclick="setReviewRating(2)" class="text-2xl text-gray-300 hover:text-amazon-amber transition" id="star-btn-2">★</button>
            <button type="button" onclick="setReviewRating(3)" class="text-2xl text-gray-300 hover:text-amazon-amber transition" id="star-btn-3">★</button>
            <button type="button" onclick="setReviewRating(4)" class="text-2xl text-gray-300 hover:text-amazon-amber transition" id="star-btn-4">★</button>
            <button type="button" onclick="setReviewRating(5)" class="text-2xl text-amazon-amber hover:text-amazon-amber transition" id="star-btn-5">★</button>
            <span class="ml-2 font-bold text-gray-700" id="review-rating-score-label">5 of 5 Stars</span>
          </div>
        </div>

        <div>
          <label class="block font-semibold text-gray-700 mb-1">Your Name / Handle:</label>
          <input type="text" id="review-author-name" required class="w-full p-2 border border-gray-300 rounded outline-none focus:ring-1 focus:ring-amazon-amber" placeholder="e.g. Alex Chen" />
        </div>

        <div>
          <label class="block font-semibold text-gray-700 mb-1">Written Feedback / Experience:</label>
          <textarea id="review-comment-text" required rows="3" class="w-full p-2 border border-gray-300 rounded outline-none focus:ring-1 focus:ring-amazon-amber leading-relaxed" placeholder="What did you like or dislike? How does the build quality feel?"></textarea>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t border-gray-200">
          <button type="button" onclick="closeWriteReviewModal()" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded">Cancel</button>
          <button type="submit" class="px-5 py-2 amazon-btn-yellow font-bold text-gray-950 rounded">Submit Review</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ================= ORDER TRACKING MODAL ================= -->
  <div id="order-tracking-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-xl w-full p-6 shadow-2xl border border-gray-300">
      <div class="flex items-center justify-between pb-3 border-b border-gray-200">
        <div class="flex items-center gap-2">
          <i data-lucide="truck" class="w-5 h-5 text-blue-600"></i>
          <h3 class="font-bold text-sm text-gray-900" id="tracking-modal-title">Live Package Tracking</h3>
        </div>
        <button onclick="closeOrderTrackingModal()" class="text-gray-400 hover:text-gray-800"><i data-lucide="x" class="w-5 h-5"></i></button>
      </div>

      <div class="py-4 space-y-4 text-xs">
        <div class="bg-blue-50 border border-blue-200 p-3 rounded flex items-center justify-between">
          <div>
            <span class="text-gray-500 text-[11px] block">Courier Partner</span>
            <span class="font-bold text-blue-900">SmartCommerce Prime Air Express</span>
          </div>
          <div class="text-right">
            <span class="text-gray-500 text-[11px] block">Tracking AWB</span>
            <span class="font-mono font-bold text-blue-900" id="tracking-awb-num">AWB-SC-982341</span>
          </div>
        </div>

        <!-- 4-Step Milestone Progress Bar -->
        <div class="py-4 px-2">
          <div class="relative flex items-center justify-between">
            <div class="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-emerald-500 w-full z-0"></div>
            
            <!-- Step 1 -->
            <div class="relative z-10 flex flex-col items-center">
              <div class="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold shadow">
                <i data-lucide="check" class="w-4 h-4"></i>
              </div>
              <span class="text-[10px] font-bold mt-1 text-gray-800">Ordered</span>
              <span class="text-[9px] text-gray-500" id="track-step1-time">10:30 AM</span>
            </div>

            <!-- Step 2 -->
            <div class="relative z-10 flex flex-col items-center">
              <div class="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold shadow">
                <i data-lucide="package-check" class="w-4 h-4"></i>
              </div>
              <span class="text-[10px] font-bold mt-1 text-gray-800">Dispatched</span>
              <span class="text-[9px] text-gray-500">Hub 101</span>
            </div>

            <!-- Step 3 -->
            <div class="relative z-10 flex flex-col items-center">
              <div class="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold shadow">
                <i data-lucide="truck" class="w-4 h-4"></i>
              </div>
              <span class="text-[10px] font-bold mt-1 text-gray-800">In Transit</span>
              <span class="text-[9px] text-gray-500">Air Express</span>
            </div>

            <!-- Step 4 -->
            <div class="relative z-10 flex flex-col items-center">
              <div class="w-7 h-7 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold shadow animate-pulse">
                <i data-lucide="home" class="w-4 h-4"></i>
              </div>
              <span class="text-[10px] font-bold mt-1 text-emerald-700">Delivered</span>
              <span class="text-[9px] text-emerald-700 font-semibold">Today</span>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 p-3 rounded border border-gray-200 text-[11px] space-y-1">
          <div class="flex justify-between">
            <span class="text-gray-500">Shipping Address:</span>
            <span class="font-semibold text-gray-800" id="tracking-address">Bengaluru 560001</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Delivery Status:</span>
            <span class="font-bold text-emerald-600">Shipment Completed (Signed by Alex)</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= AMAZON-STYLE TAX INVOICE MODAL ================= -->
  <div id="order-invoice-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl border border-gray-300 text-xs">
      
      <div class="flex items-center justify-between pb-3 border-b border-gray-300">
        <div class="flex items-center gap-2">
          <span class="text-lg font-black tracking-tight text-amazon-navy">smart<span class="text-amazon-amber">commerce</span></span>
          <span class="bg-gray-100 text-gray-700 text-[10px] font-bold px-2 py-0.5 rounded border border-gray-300">Official Tax Invoice</span>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="window.print()" class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold px-3 py-1 rounded border border-gray-300 flex items-center gap-1 text-[11px]">
            <i data-lucide="printer" class="w-3.5 h-3.5"></i> Print Invoice
          </button>
          <button onclick="closeOrderInvoiceModal()" class="text-gray-400 hover:text-gray-800"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
      </div>

      <div class="py-4 space-y-4" id="invoice-modal-content">
        <!-- Dynamic invoice content with GST breakdown -->
      </div>
    </div>
  </div>'''

# Inject additional modals before system-toast
html = html.replace('  <!-- ================= SYSTEM NOTIFICATION TOAST ================= -->', additional_modals_html + '\n\n  <!-- ================= SYSTEM NOTIFICATION TOAST ================= -->', 1)
print("[6] Additional modals (Review, Tracking, Invoice) injected.")

# -----------------------------------------------------------------------------
# 7. INJECT ADVANCED JAVASCRIPT FUNCTIONS
# -----------------------------------------------------------------------------
enhanced_js = '''
    /* ==========================================================================
       HERO DEALS CAROUSEL LOGIC
       ========================================================================== */
    let currentHeroSlide = 1;
    let heroTimer = null;

    function setHeroSlide(slideNum) {
      currentHeroSlide = slideNum;
      for (let i = 1; i <= 3; i++) {
        const slide = document.getElementById(`hero-slide-${i}`);
        const dot = document.getElementById(`hero-dot-${i}`);
        if (slide) slide.classList.toggle('hidden', i !== slideNum);
        if (dot) {
          dot.className = (i === slideNum)
            ? 'w-2.5 h-2.5 rounded-full bg-amazon-amber cursor-pointer transition'
            : 'w-2.5 h-2.5 rounded-full bg-white/40 hover:bg-white cursor-pointer transition';
        }
      }
      lucide.createIcons();
    }

    function nextHeroSlide() {
      let next = currentHeroSlide + 1;
      if (next > 3) next = 1;
      setHeroSlide(next);
    }

    function prevHeroSlide() {
      let prev = currentHeroSlide - 1;
      if (prev < 1) prev = 3;
      setHeroSlide(prev);
    }

    // Auto-advance hero carousel every 7 seconds
    heroTimer = setInterval(nextHeroSlide, 7000);

    /* ==========================================================================
       VOICE SEARCH / SPEECH RECOGNITION (WEB SPEECH API)
       ========================================================================== */
    let isVoiceListening = false;
    let voiceRecognition = null;

    function startVoiceSearch() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        showToast("Voice Search Notice", "Speech Recognition is not supported in this browser. Please use Chrome/Edge or type your search query.", "mic-off");
        return;
      }

      if (isVoiceListening && voiceRecognition) {
        voiceRecognition.stop();
        return;
      }

      try {
        voiceRecognition = new SpeechRecognition();
        voiceRecognition.continuous = false;
        voiceRecognition.interimResults = false;
        voiceRecognition.lang = 'en-US';

        const btn = document.getElementById('voice-search-btn');
        const icon = document.getElementById('voice-search-icon');
        const input = document.getElementById('search-input');

        voiceRecognition.onstart = () => {
          isVoiceListening = true;
          btn.classList.add('bg-red-50', 'text-red-600');
          icon.classList.add('animate-pulse');
          showToast("Listening...", "Speak your search query now (e.g., 'wireless headphones under 20000')", "mic");
        };

        voiceRecognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          input.value = transcript;
          showToast("Speech Captured", `Searching for: "${transcript}"`, "search");
          executeSearch();
        };

        voiceRecognition.onerror = (event) => {
          console.warn("Speech recognition error:", event.error);
          showToast("Voice Search", `Recognition error: ${event.error}`, "alert-circle");
        };

        voiceRecognition.onend = () => {
          isVoiceListening = false;
          btn.classList.remove('bg-red-50', 'text-red-600');
          icon.classList.remove('animate-pulse');
          lucide.createIcons();
        };

        voiceRecognition.start();
      } catch (err) {
        console.error("Voice search initialization error:", err);
        showToast("Voice Search", "Unable to access microphone.", "alert-triangle");
      }
    }

    /* ==========================================================================
       ENHANCED 360° TURNTABLE ZOOM & COLORWAYS
       ========================================================================== */
    let view360Zoom = 1.0;
    let active360Colorway = 'onyx';

    const colorwayPalettes = {
      onyx: { r: 35, g: 40, b: 50, ear: '#0f172a', name: 'Midnight Onyx' },
      silver: { r: 160, g: 170, b: 185, ear: '#475569', name: 'Space Silver' },
      blue: { r: 30, g: 70, b: 160, ear: '#1e3a8a', name: 'Cosmic Blue' },
      gold: { r: 200, g: 140, b: 90, ear: '#78350f', name: 'Rose Gold' }
    };

    function zoom360(delta) {
      view360Zoom = Math.max(0.6, Math.min(2.0, Math.round((view360Zoom + delta) * 10) / 10));
      document.getElementById('zoom-level-indicator').textContent = `${view360Zoom.toFixed(1)}x`;
      render360Frame();
    }

    function set360Colorway(cw) {
      active360Colorway = cw;
      ['onyx', 'silver', 'blue', 'gold'].forEach(c => {
        const btn = document.getElementById(`cw-btn-${c}`);
        if (btn) {
          btn.className = (c === cw)
            ? 'flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-gray-400 bg-gray-900 text-white font-bold'
            : 'flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-gray-300 bg-white text-gray-800 font-medium hover:bg-gray-50';
        }
      });
      render360Frame();
      showToast("360° Colorway Updated", `Finish changed to ${colorwayPalettes[cw].name}`, "palette");
    }

    /* ==========================================================================
       SIDE-BY-SIDE COMPARISON MATRIX
       ========================================================================== */
    function renderComparisonMatrix(productId) {
      const current = getHydratedProducts().find(p => p.product_id === productId);
      const table = document.getElementById('modal-comparison-table');
      if (!current || !table) return;

      // Find 2 similar products in same category or adjacent
      const all = getHydratedProducts();
      const sameCat = all.filter(p => p.category === current.category && p.product_id !== current.product_id);
      const others = all.filter(p => p.category !== current.category && p.product_id !== current.product_id);
      const comparePool = [...sameCat, ...others].slice(0, 2);
      const items = [current, ...comparePool];

      let specsKeys = ['Category', 'Customer Rating', 'Best Price', 'Delivery', 'Prime', 'Stock Status'];

      table.innerHTML = `
        <thead>
          <tr class="bg-gray-100 border-b border-gray-200">
            <th class="p-3 font-bold text-gray-700 w-36">Metric / Feature</th>
            ${items.map((item, idx) => `
              <th class="p-3 text-center ${idx === 0 ? 'bg-amber-50/70 border-x border-amber-200' : ''}">
                <div class="flex flex-col items-center">
                  <img src="${item.primary_image_url}" class="h-16 w-16 object-contain mb-1.5" />
                  <span class="font-bold text-gray-900 text-[11px] line-clamp-2 max-w-[140px]">${item.title}</span>
                  ${idx === 0 ? '<span class="bg-amazon-amber text-gray-950 text-[9px] font-black px-1.5 py-0.5 rounded mt-1">CURRENT ITEM</span>' : ''}
                </div>
              </th>
            `).join('')}
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 font-sans">
          <tr>
            <td class="p-2.5 font-bold text-gray-600 bg-gray-50">Category</td>
            ${items.map((item, idx) => `<td class="p-2.5 text-center ${idx === 0 ? 'bg-amber-50/30 border-x border-amber-200 font-semibold' : ''}">${item.category}</td>`).join('')}
          </tr>
          <tr>
            <td class="p-2.5 font-bold text-gray-600 bg-gray-50">Rating</td>
            ${items.map((item, idx) => `<td class="p-2.5 text-center text-amazon-amber font-bold ${idx === 0 ? 'bg-amber-50/30 border-x border-amber-200' : ''}">★ ${item.rating} (${item.reviews_count})</td>`).join('')}
          </tr>
          <tr>
            <td class="p-2.5 font-bold text-gray-600 bg-gray-50">Buy Box Price</td>
            ${items.map((item, idx) => `<td class="p-2.5 text-center font-bold text-amazon-priceRed text-sm ${idx === 0 ? 'bg-amber-50/30 border-x border-amber-200' : ''}">₹${Math.round(item.price).toLocaleString('en-IN')}</td>`).join('')}
          </tr>
          <tr>
            <td class="p-2.5 font-bold text-gray-600 bg-gray-50">Delivery Speed</td>
            ${items.map((item, idx) => `<td class="p-2.5 text-center ${idx === 0 ? 'bg-amber-50/30 border-x border-amber-200' : ''}">${item.delivery_days} Day(s) (${item.delivery_days === 1 ? 'Prime Same-Day' : 'Standard'})</td>`).join('')}
          </tr>
          <tr>
            <td class="p-2.5 font-bold text-gray-600 bg-gray-50">Stock Quantity</td>
            ${items.map((item, idx) => `<td class="p-2.5 text-center ${idx === 0 ? 'bg-amber-50/30 border-x border-amber-200' : ''}"><span class="font-bold ${item.stock_quantity <= 2 ? 'text-amber-600' : 'text-emerald-600'}">${item.stock_quantity} in stock</span></td>`).join('')}
          </tr>
          <tr class="bg-gray-50">
            <td class="p-2.5 font-bold text-gray-600">Action</td>
            ${items.map((item, idx) => `
              <td class="p-2.5 text-center ${idx === 0 ? 'bg-amber-50/50 border-x border-amber-200' : ''}">
                <button onclick="quickAddToCart(${item.product_id})" class="amazon-btn-yellow font-bold text-[10px] px-3 py-1.5 rounded shadow-sm">
                  Add to Cart
                </button>
              </td>
            `).join('')}
          </tr>
        </tbody>
      `;
    }

    /* ==========================================================================
       CUSTOMER REVIEWS & 5-STAR HISTOGRAM ENGINE
       ========================================================================== */
    let currentReviewRating = 5;

    function renderReviewsSection(productId) {
      const res = db.exec("SELECT review_id, buyer_name, rating, comment, verified_purchase FROM reviews WHERE product_id = ? ORDER BY review_id DESC", [productId]);
      const reviews = (res && res[0]) ? res[0].values : [];

      // Compute star distribution
      const total = reviews.length;
      const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
      let sum = 0;

      reviews.forEach(r => {
        const star = r[2];
        if (counts[star] !== undefined) counts[star]++;
        sum += star;
      });

      const avg = total > 0 ? (sum / total).toFixed(1) : "4.8";
      document.getElementById('reviews-avg-rating').textContent = avg;
      document.getElementById('reviews-total-count').textContent = `${total} verified rating(s)`;

      // Render stars
      const numStars = Math.round(parseFloat(avg));
      document.getElementById('reviews-stars-summary').innerHTML = '★'.repeat(numStars) + '☆'.repeat(5 - numStars);

      // Render Progress Bars for 5, 4, 3, 2, 1
      const histContainer = document.getElementById('reviews-histogram-bars');
      histContainer.innerHTML = '';
      [5, 4, 3, 2, 1].forEach(star => {
        const c = counts[star] || 0;
        const pct = total > 0 ? Math.round((c / total) * 100) : (star === 5 ? 75 : star === 4 ? 18 : 3);
        histContainer.innerHTML += `
          <div class="flex items-center gap-2 text-[11px]">
            <span class="text-amazon-link hover:underline font-semibold w-8">${star} star</span>
            <div class="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
              <div class="bg-amazon-amber h-3 rounded-full" style="width: ${pct}%"></div>
            </div>
            <span class="text-gray-500 font-mono w-7 text-right">${pct}%</span>
          </div>
        `;
      });

      // Render Reviews List
      const listContainer = document.getElementById('modal-reviews-list');
      if (reviews.length === 0) {
        listContainer.innerHTML = `<p class="text-xs text-gray-500 italic">No customer reviews yet. Be the first to review!</p>`;
      } else {
        listContainer.innerHTML = reviews.map(r => {
          const [id, author, rating, comment, verified] = r;
          return `
            <div class="border-b border-gray-200 pb-3 space-y-1">
              <div class="flex items-center gap-1.5">
                <div class="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center font-bold text-[10px] text-gray-700">
                  ${author.charAt(0)}
                </div>
                <span class="font-bold text-gray-900 text-xs">${author}</span>
                ${verified ? '<span class="text-emerald-600 text-[10px] font-semibold flex items-center gap-0.5"><i data-lucide="check" class="w-3 h-3"></i> Verified Purchase</span>' : ''}
              </div>
              <div class="flex items-center gap-2">
                <span class="text-amazon-amber font-bold text-xs">${'★'.repeat(rating)}${'☆'.repeat(5 - rating)}</span>
                <span class="font-bold text-gray-800 text-xs">Authentic Experience</span>
              </div>
              <p class="text-gray-700 text-xs leading-relaxed">${comment}</p>
            </div>
          `;
        }).join('');
      }
      lucide.createIcons();
    }

    function openWriteReviewModal() {
      if (!activeModalProduct) return;
      document.getElementById('review-modal-product-title').textContent = activeModalProduct.title;
      document.getElementById('review-author-name').value = currentUser ? currentUser.full_name : 'Verified Customer';
      document.getElementById('write-review-modal').classList.remove('hidden');
      setReviewRating(5);
      lucide.createIcons();
    }

    function closeWriteReviewModal() {
      document.getElementById('write-review-modal').classList.add('hidden');
    }

    function setReviewRating(star) {
      currentReviewRating = star;
      document.getElementById('review-rating-score-label').textContent = `${star} of 5 Stars`;
      for (let i = 1; i <= 5; i++) {
        const btn = document.getElementById(`star-btn-${i}`);
        if (btn) {
          btn.className = (i <= star)
            ? 'text-2xl text-amazon-amber transition font-bold'
            : 'text-2xl text-gray-300 transition';
        }
      }
    }

    function handleReviewSubmit(e) {
      e.preventDefault();
      if (!activeModalProduct) return;

      const author = document.getElementById('review-author-name').value.trim();
      const comment = document.getElementById('review-comment-text').value.trim();

      try {
        db.run(
          "INSERT INTO reviews (product_id, buyer_name, rating, comment, verified_purchase) VALUES (?, ?, ?, ?, 1)",
          [activeModalProduct.product_id, author, currentReviewRating, comment]
        );

        // Recalculate average rating for product
        const aggRes = db.exec("SELECT AVG(rating), COUNT(review_id) FROM reviews WHERE product_id = ?", [activeModalProduct.product_id]);
        if (aggRes && aggRes[0]) {
          const newAvg = Math.round(aggRes[0].values[0][0] * 10) / 10;
          const newCount = aggRes[0].values[0][1];
          db.run("UPDATE products SET rating = ?, reviews_count = ? WHERE product_id = ?", [newAvg, newCount, activeModalProduct.product_id]);
        }

        closeWriteReviewModal();
        recalculateAndRender();
        openProductModal(activeModalProduct.product_id);
        showToast("Review Published", "Your review has been recorded in the database and ratings updated.", "check-circle");
      } catch (err) {
        showToast("Error", err.message, "alert-triangle");
      }
    }

    /* ==========================================================================
       INTERACTIVE SQL QUERY CONSOLE LOGIC
       ========================================================================== */
    const sqlQueryPresetsMap = {
      low_stock: "SELECT p.product_id, p.title, sp.seller_name, sp.price, sp.stock_quantity FROM products p JOIN seller_products sp ON p.product_id = sp.product_id WHERE sp.stock_quantity <= 2;",
      category_summary: "SELECT category, COUNT(product_id) as skus, ROUND(AVG(base_price),2) as avg_price, MIN(base_price) as min_price, MAX(base_price) as max_price FROM products GROUP BY category ORDER BY skus DESC;",
      orders_buyers: "SELECT o.order_id, u.full_name as customer, o.total_amount, o.order_status, o.placed_at, o.shipping_address FROM orders o JOIN users u ON o.buyer_id = u.user_id ORDER BY o.order_id DESC;",
      quantum_race: "SELECT sp.offer_id, sp.seller_id, sp.seller_name, sp.price, sp.stock_quantity, sp.delivery_days FROM seller_products sp WHERE sp.product_id = 17;",
      top_reviews: "SELECT p.product_id, p.title, p.rating, p.reviews_count, COUNT(r.review_id) as seeded_reviews FROM products p LEFT JOIN reviews r ON p.product_id = r.product_id GROUP BY p.product_id ORDER BY p.rating DESC LIMIT 8;"
    };

    function loadSqlPreset(presetKey) {
      if (sqlQueryPresetsMap[presetKey]) {
        document.getElementById('sql-console-input').value = sqlQueryPresetsMap[presetKey];
        executeAdhocSql();
      }
    }

    function executeAdhocSql() {
      const query = document.getElementById('sql-console-input').value.trim();
      const stats = document.getElementById('sql-execution-stats');
      const badge = document.getElementById('sql-rows-badge');
      const thead = document.getElementById('sql-results-head');
      const tbody = document.getElementById('sql-results-body');

      if (!query) return;

      const t0 = performance.now();
      try {
        const res = db.exec(query);
        const t1 = performance.now();
        const latencyMs = (t1 - t0).toFixed(2);

        if (!res || res.length === 0) {
          stats.textContent = `Executed in ${latencyMs}ms (0 rows returned / DDL Statement)`;
          badge.textContent = '0 rows';
          thead.innerHTML = '';
          tbody.innerHTML = `<tr><td class="p-3 text-emerald-400 font-mono">Statement executed successfully with zero result rows.</td></tr>`;
          return;
        }

        const cols = res[0].columns;
        const rows = res[0].values;
        stats.textContent = `Executed in ${latencyMs}ms (${rows.length} rows returned)`;
        badge.textContent = `${rows.length} rows`;

        thead.innerHTML = `<tr>${cols.map(c => `<th class="p-2 border-b border-gray-800 bg-gray-900 text-gray-300 font-bold">${c}</th>`).join('')}</tr>`;
        tbody.innerHTML = rows.map(r => `
          <tr class="hover:bg-gray-900/50">
            ${r.map(val => `<td class="p-2 border-b border-gray-800/60">${val === null ? '<span class="text-gray-500 italic">NULL</span>' : val}</td>`).join('')}
          </tr>
        `).join('');

      } catch (err) {
        stats.textContent = `Error executing query`;
        badge.textContent = 'Error';
        thead.innerHTML = '';
        tbody.innerHTML = `<tr><td class="p-3 text-red-400 font-mono">SQL Error: ${err.message}</td></tr>`;
      }
    }

    /* ==========================================================================
       ORDER TRACKING & TAX INVOICE LOGIC
       ========================================================================== */
    function openOrderTrackingModal(orderId) {
      document.getElementById('tracking-modal-title').textContent = `Tracking for Order #${orderId}`;
      document.getElementById('tracking-awb-num').textContent = `AWB-SC-${892300 + parseInt(orderId)}`;
      document.getElementById('tracking-address').textContent = currentUser ? `${currentUser.full_name} - Bengaluru 560001` : 'Bengaluru 560001';
      document.getElementById('order-tracking-modal').classList.remove('hidden');
      lucide.createIcons();
    }

    function closeOrderTrackingModal() {
      document.getElementById('order-tracking-modal').classList.add('hidden');
    }

    function openOrderInvoiceModal(orderId) {
      const res = db.exec(`
        SELECT o.order_id, o.total_amount, o.shipping_address, o.order_status, o.placed_at,
               oi.product_id, oi.quantity, oi.unit_price, p.title, sp.seller_name
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN seller_products sp ON oi.product_id = sp.product_id AND oi.seller_id = sp.seller_id
        WHERE o.order_id = ?;
      `, [orderId]);

      if (!res || !res[0] || res[0].values.length === 0) {
        showToast("Invoice Notice", `Invoice details for Order #${orderId} not found.`, "file-text");
        return;
      }

      const rows = res[0].values;
      const first = rows[0];
      const [oid, total, address, status, date] = first;

      const subtotal = Math.round(total / 1.18);
      const taxGst = total - subtotal;
      const cgst = Math.round(taxGst / 2);
      const sgst = Math.round(taxGst / 2);

      const content = document.getElementById('invoice-modal-content');
      content.innerHTML = `
        <div class="grid grid-cols-2 gap-4 pb-4 border-b border-gray-200">
          <div>
            <span class="text-gray-500 block text-[11px]">Sold By:</span>
            <span class="font-bold text-gray-900">${first[9]}</span>
            <span class="text-gray-500 block text-[10px]">GSTIN: 29AABCU9603R1ZM</span>
            <span class="text-gray-500 block text-[10px]">Fulfillment Center: BLR-101</span>
          </div>
          <div class="text-right">
            <span class="font-bold text-gray-900 block">Invoice #: SC-INV-${oid}-2026</span>
            <span class="text-gray-500 block text-[11px]">Order ID: #${oid}</span>
            <span class="text-gray-500 block text-[10px]">Order Date: ${date}</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 pb-3 border-b border-gray-200">
          <div>
            <span class="text-gray-500 block text-[11px]">Billing &amp; Shipping Address:</span>
            <span class="font-bold text-gray-900">${currentUser ? currentUser.full_name : 'Alex Chen'}</span>
            <span class="text-gray-600 block text-[11px]">${address}</span>
            <span class="text-gray-500 text-[10px]">Place of Supply: Karnataka (State Code 29)</span>
          </div>
          <div class="text-right">
            <span class="text-gray-500 block text-[11px]">Payment Mode:</span>
            <span class="font-bold text-gray-900">ACID Relational Transfer (Prepaid)</span>
            <span class="text-emerald-600 font-bold block text-[10px]">Status: PAID / ${status}</span>
          </div>
        </div>

        <!-- Line Items Table -->
        <table class="w-full text-left text-xs border border-gray-200 rounded">
          <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 font-bold">
            <tr>
              <th class="p-2">Description</th>
              <th class="p-2 text-center">Qty</th>
              <th class="p-2 text-right">Gross Price</th>
              <th class="p-2 text-right">Total</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            ${rows.map(r => `
              <tr>
                <td class="p-2 font-medium text-gray-900">${r[8]}</td>
                <td class="p-2 text-center">${r[6]}</td>
                <td class="p-2 text-right font-mono">₹${Math.round(r[7]).toLocaleString('en-IN')}</td>
                <td class="p-2 text-right font-mono font-bold">₹${Math.round(r[6] * r[7]).toLocaleString('en-IN')}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <!-- Tax & Summary -->
        <div class="bg-gray-50 p-3 rounded border border-gray-200 space-y-1.5 font-mono text-[11px]">
          <div class="flex justify-between">
            <span class="text-gray-600">Net Taxable Value:</span>
            <span class="font-semibold">₹${subtotal.toLocaleString('en-IN')}</span>
          </div>
          <div class="flex justify-between text-gray-600">
            <span>CGST (9.0%):</span>
            <span>₹${cgst.toLocaleString('en-IN')}</span>
          </div>
          <div class="flex justify-between text-gray-600">
            <span>SGST (9.0%):</span>
            <span>₹${sgst.toLocaleString('en-IN')}</span>
          </div>
          <div class="flex justify-between font-bold text-sm text-gray-900 pt-2 border-t border-gray-300">
            <span>Invoice Grand Total:</span>
            <span class="text-amazon-priceRed">₹${Math.round(total).toLocaleString('en-IN')}</span>
          </div>
        </div>
      `;

      document.getElementById('order-invoice-modal').classList.remove('hidden');
      lucide.createIcons();
    }

    function closeOrderInvoiceModal() {
      document.getElementById('order-invoice-modal').classList.add('hidden');
    }
'''

# Update openProductModal to call comparison matrix and reviews
open_modal_old = '''    function openProductModal(productId) {
      const p = getHydratedProducts().find(prod => prod.product_id === productId);
      if (!p) return;

      activeModalProduct = p;'''

open_modal_new = '''    function openProductModal(productId) {
      const p = getHydratedProducts().find(prod => prod.product_id === productId);
      if (!p) return;

      activeModalProduct = p;
      renderComparisonMatrix(productId);
      renderReviewsSection(productId);'''

html = html.replace(open_modal_old, open_modal_new, 1)

# Update switchDevTab to handle 'sqlconsole'
switch_tab_old = '''    function switchDevTab(tabName) {
      ['concurrency', 'rds', 'weights', 'eval'].forEach(t => {
        document.getElementById(`dev-tab-${t}`).classList.add('hidden');
        document.getElementById(`tab-btn-${t}`).className = 'px-4 py-2.5 font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200';
      });

      document.getElementById(`dev-tab-${tabName}`).classList.remove('hidden');
      document.getElementById(`tab-btn-${tabName}`).className = 'px-4 py-2.5 font-bold border-b-2 border-amazon-amber text-amazon-amber';'''

switch_tab_new = '''    function switchDevTab(tabName) {
      ['concurrency', 'rds', 'weights', 'eval', 'sqlconsole'].forEach(t => {
        const tabEl = document.getElementById(`dev-tab-${t}`);
        const btnEl = document.getElementById(`tab-btn-${t}`);
        if (tabEl) tabEl.classList.add('hidden');
        if (btnEl) btnEl.className = 'px-4 py-2.5 font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200';
      });

      const activeTab = document.getElementById(`dev-tab-${tabName}`);
      const activeBtn = document.getElementById(`tab-btn-${tabName}`);
      if (activeTab) activeTab.classList.remove('hidden');
      if (activeBtn) activeBtn.className = 'px-4 py-2.5 font-bold border-b-2 border-amazon-amber text-amazon-amber';
      if (tabName === 'sqlconsole') executeAdhocSql();'''

html = html.replace(switch_tab_old, switch_tab_new, 1)

# Update loadOrdersHistory to add Track Package and View Tax Invoice buttons
load_orders_old = '''            <span class="bg-white border border-gray-300 px-2 py-1 rounded text-gray-700 font-semibold">${count} Item(s)</span>
          </div>
        `;
        container.appendChild(card);'''

load_orders_new = '''            <span class="bg-white border border-gray-300 px-2 py-1 rounded text-gray-700 font-semibold">${count} Item(s)</span>
          </div>
          <div class="flex items-center gap-2 pt-2 border-t border-gray-200">
            <button onclick="openOrderTrackingModal(${id})" class="bg-white hover:bg-gray-100 text-gray-800 text-[11px] font-semibold px-2.5 py-1 rounded border border-gray-300 flex items-center gap-1 transition">
              <i data-lucide="truck" class="w-3.5 h-3.5 text-blue-600"></i> Track Package
            </button>
            <button onclick="openOrderInvoiceModal(${id})" class="bg-white hover:bg-gray-100 text-gray-800 text-[11px] font-semibold px-2.5 py-1 rounded border border-gray-300 flex items-center gap-1 transition">
              <i data-lucide="file-text" class="w-3.5 h-3.5 text-amazon-amber"></i> View Tax Invoice
            </button>
          </div>
        `;
        container.appendChild(card);'''

html = html.replace(load_orders_old, load_orders_new, 1)

# Update render360Frame to support zoom and colorway palette
render_360_old = '''      ctx.save();
      ctx.translate(cx, objCy);

      // Lighting & Shading Gradient based on rotation angle
      const lightFactor = 0.5 + 0.5 * Math.cos(rad - Math.PI / 4);
      const shadeR = Math.round(40 + lightFactor * 60);
      const shadeG = Math.round(50 + lightFactor * 80);
      const shadeB = Math.round(70 + lightFactor * 120);'''

render_360_new = '''      ctx.save();
      ctx.translate(cx, objCy);
      ctx.scale(view360Zoom, view360Zoom);

      // Lighting & Shading Gradient based on rotation angle and colorway palette
      const palette = colorwayPalettes[active360Colorway] || colorwayPalettes.onyx;
      const lightFactor = 0.5 + 0.5 * Math.cos(rad - Math.PI / 4);
      const shadeR = Math.round(palette.r + lightFactor * 50);
      const shadeG = Math.round(palette.g + lightFactor * 60);
      const shadeB = Math.round(palette.b + lightFactor * 75);'''

html = html.replace(render_360_old, render_360_new, 1)

# Seed realistic reviews in initDatabase
seed_reviews_old = '''        // 8. Seed Initial Orders
        db.run(`
          INSERT INTO orders (buyer_id, total_amount, shipping_address, order_status, placed_at)
          VALUES (1, 19999, 'Bengaluru 560001, Tech Park View, #402', 'DELIVERED', '2026-09-10 14:22:00')
        `);'''

seed_reviews_new = '''        // 7b. Seed Authenticated Customer Reviews
        const reviewsSeed = [
          { pid: 1, name: 'Vikram Mehta', r: 5, c: 'Exceptional sound stage and LDAC clarity. The active noise cancellation easily outperforms my previous Sony XM4s on flights.' },
          { pid: 1, name: 'Ananya Roy', r: 5, c: '55 hours battery is no joke. I charge it twice a month with heavy daily use. Multipoint bluetooth connects seamlessly.' },
          { pid: 1, name: 'David Miller', r: 4, c: 'Premium build and comfortable ear cushions. Slightly heavy for marathon running, but fantastic for studio listening.' },
          { pid: 17, name: 'Rahul Sharma', r: 5, c: 'Unbelievable performance from the Ryzen 7 7840U. Compiled Linux kernel in under 4 minutes. Secondary M.2 slot accepted my 2TB Samsung 980 Pro without warranty issues!' },
          { pid: 17, name: 'Elena Rostova', r: 5, c: 'Best developer laptop for the price. 18-hour battery is real. Gorgeous OLED screen.' },
          { pid: 17, name: 'Karthik N.', r: 4, c: 'Super lightweight and rigid chassis. Keyboard travel is crisp. Trackpad is large and responsive.' },
          { pid: 26, name: 'Siddharth Sen', r: 5, c: 'The 3.2K 120Hz OLED screen is unmatched for DaVinci Resolve color grading. Dual Thunderbolt 4 drives my two 4K displays.' },
          { pid: 7, name: 'Priya Nair', r: 5, c: 'Floral jasmine aroma with crisp citrus finish. Truly authentic Ethiopian Yirgacheffe single origin!' },
          { pid: 6, name: 'Arjun Kapoor', r: 5, c: 'Motor is completely silent and auto-incline changes smoothly during HIIT workouts.' }
        ];

        reviewsSeed.forEach(rv => {
          db.run("INSERT INTO reviews (product_id, buyer_name, rating, comment, verified_purchase) VALUES (?, ?, ?, ?, 1)", [rv.pid, rv.name, rv.r, rv.c]);
        });

        // 8. Seed Initial Orders
        db.run(`
          INSERT INTO orders (buyer_id, total_amount, shipping_address, order_status, placed_at)
          VALUES (1, 19999, 'Bengaluru 560001, Tech Park View, #402', 'DELIVERED', '2026-09-10 14:22:00')
        `);'''

html = html.replace(seed_reviews_old, seed_reviews_new, 1)

# Append enhanced JS functions before </script>
html = html.replace('  </script>\n</body>', enhanced_js + '\n  </script>\n</body>', 1)

# Write updated index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Enhanced index.html written successfully! New length: {len(html)} bytes.")
