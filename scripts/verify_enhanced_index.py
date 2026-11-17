import urllib.request
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = {
    # Voice Search
    'Voice Search Mic Button': 'id="voice-search-btn"' in html,
    'Voice Search JS Handler': 'startVoiceSearch()' in html or 'function startVoiceSearch' in html,
    
    # Hero Carousel
    'Hero Carousel Slide 1': 'id="hero-slide-1"' in html,
    'Hero Carousel Slide 2': 'id="hero-slide-2"' in html,
    'Hero Carousel Slide 3': 'id="hero-slide-3"' in html,
    'Hero Carousel Next/Prev Handlers': 'nextHeroSlide' in html and 'prevHeroSlide' in html,
    
    # Enhanced 360 Viewer
    '360 Zoom In/Out Handler': 'zoom360' in html,
    '360 Zoom Level Indicator': 'id="zoom-level-indicator"' in html,
    '360 Colorway Finishes': 'set360Colorway' in html and 'colorwayPalettes' in html,
    '360 Colorway Buttons': 'cw-btn-onyx' in html and 'cw-btn-gold' in html,
    
    # Comparison Matrix
    'Comparison Matrix Section': 'id="modal-comparison-section"' in html,
    'Comparison Table ID': 'id="modal-comparison-table"' in html,
    'Comparison Matrix JS Handler': 'renderComparisonMatrix' in html,
    
    # Customer Reviews & 5-Star Histogram
    'Reviews Section ID': 'id="modal-reviews-section"' in html,
    'Reviews Histogram Bars': 'id="reviews-histogram-bars"' in html,
    'Write Review Modal': 'id="write-review-modal"' in html,
    'Write Review Form Handler': 'handleReviewSubmit' in html,
    'Seeded Customer Reviews': 'Vikram Mehta' in html and 'Elena Rostova' in html,
    
    # Interactive SQL Query Console
    'SQL Console Tab Button': 'id="tab-btn-sqlconsole"' in html,
    'SQL Console Tab Panel': 'id="dev-tab-sqlconsole"' in html,
    'SQL Query Input Area': 'id="sql-console-input"' in html,
    'SQL Execution Handler': 'executeAdhocSql' in html,
    'SQL Query Presets Map': 'sqlQueryPresetsMap' in html,
    
    # Order Tracking & Tax Invoice
    'Order Tracking Modal': 'id="order-tracking-modal"' in html,
    'Order Tracking 4-Step Bar': 'AWB-SC-' in html and 'Prime Air Express' in html,
    'Order Invoice Modal': 'id="order-invoice-modal"' in html,
    'Tax Invoice GST Calculation': 'GSTIN: 29AABCU9603R1ZM' in html and 'CGST' in html,
    'Open Tracking/Invoice Buttons': 'openOrderTrackingModal' in html and 'openOrderInvoiceModal' in html,
}

print("=== SMARTCOMMERCE ENHANCEMENT VERIFICATION ===")
passed = 0
for name, ok in checks.items():
    status = "PASS" if ok else "FAIL"
    if ok: passed += 1
    print(f"[{status}] {name}")

print(f"\nScore: {passed}/{len(checks)} features verified.")

# Test HTTP Server
try:
    resp = urllib.request.urlopen("http://localhost:8088/index.html")
    content = resp.read()
    print(f"[PASS] HTTP Server Port 8088: HTTP {resp.status} OK (Served {len(content)} bytes)")
except Exception as e:
    print(f"[FAIL] HTTP Server Port 8088 check failed: {e}")
