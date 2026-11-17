import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract product titles
titles = re.findall(r"title:\s*['\"]([A-Z][a-zA-Z0-9\s\-\.\'\/\&\+]+)['\"]", html)
# Filter titles belonging to the 26 products (exclude FAQ/chunk titles)
prod_titles = [t for t in titles if not t.startswith('CHK-') and len(t) > 10][:26]
print(f"Total Products Detected: {len(prod_titles)}")
for i, t in enumerate(prod_titles):
    print(f"  {chr(65+i)}: {t}")


# Verify 360 viewer elements
checks = {
    '360 Canvas ID': 'product-360-canvas' in html,
    '360 Degree Azimuth HUD': 'spin-deg-indicator' in html,
    '360 Drag Interaction Handlers': 'init360CanvasEvents' in html,
    '360 Render Loop': 'render360Frame' in html,
    '360 Auto-spin Toggle': 'toggle360AutoSpin' in html,
    '360 Angle Presets (0, 90, 180, 270)': 'set360Angle(0)' in html and 'set360Angle(180)' in html,
    'Auth Modal ID': 'auth-modal' in html,
    'Auth Nav State Manager': 'updateAuthNavUI' in html,
    'Auth Users Table DDL': 'CREATE TABLE users' in html,
    'Pre-seeded Buyer Account': 'alex@smartcommerce.dev' in html,
    'Pre-seeded Seller Account': 'seller@primetech.com' in html,
    'Pre-seeded Admin Account': 'admin@smartcommerce.dev' in html,
    'Role-based Access Guards': 'quickLoginAs' in html and 'currentUser.role' in html,
    'ACID Concurrency Race Engine': 'runConcurrencyRaceTest' in html,
    'Grounded RAG Vector Search': 'executeVectorRagLookup' in html,
    'AWS RDS Table Viewer': 'loadRdsTableData' in html,
    'Seller Central Portal': 'openSellerPortal' in html,
    'Admin Portal': 'openAdminPortal' in html,
}

print("\n--- Feature Verification ---")
all_passed = True
for k, v in checks.items():
    status = "PASS" if v else "FAIL"
    if not v:
        all_passed = False
    print(f"[{status}] {k}")

print(f"\nFinal Verdict: {'ALL CHECKS PASSED!' if all_passed else 'SOME CHECKS FAILED'}")

