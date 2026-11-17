import os

with open('scripts/generate_full_index.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find key anchor lines
anchors = {
    'Search input': -1,
    'Dev tabs': -1,
    'Dev panels': -1,
    'Product modal specs': -1,
    'Orders modal': -1,
    'initDatabase reviews seeding': -1,
    'switchDevTab function': -1,
    'openProductModal function': -1,
    'loadOrdersHistory function': -1,
    'render360Frame function': -1
}

for i, line in enumerate(lines):
    if 'id="nav-search-input"' in line:
        anchors['Search input'] = i + 1
    if 'id="tab-btn-concurrency"' in line:
        anchors['Dev tabs'] = i + 1
    if 'id="dev-panel-concurrency"' in line:
        anchors['Dev panels'] = i + 1
    if 'Technical Specs Table' in line:
        anchors['Product modal specs'] = i + 1
    if 'id="orders-modal"' in line:
        anchors['Orders modal'] = i + 1
    if 'INSERT INTO reviews' in line:
        anchors['initDatabase reviews seeding'] = i + 1
    if 'function switchDevTab(' in line:
        anchors['switchDevTab function'] = i + 1
    if 'function openProductModal(' in line:
        anchors['openProductModal function'] = i + 1
    if 'function loadOrdersHistory(' in line:
        anchors['loadOrdersHistory function'] = i + 1
    if 'function render360Frame(' in line:
        anchors['render360Frame function'] = i + 1

for k, v in anchors.items():
    print(f"{k:<35}: line {v}")
