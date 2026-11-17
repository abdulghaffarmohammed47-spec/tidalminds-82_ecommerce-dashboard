import json
import re

# Load 52 products from generate_all_categories_products.py
import sys
sys.path.append('scripts')
from generate_all_categories_products import products as base_products, categories

# Ensure critical IDs for RAG and Concurrency:
# ID 1: AeroSound X9 ANC Studio Headphones (Audio)
# ID 17: QuantumBook Ultra 14 (Laptops) - ACID Race target!
# ID 26: ZenBook Pro 16X OLED (Laptops) - RAG CHK-01 target!

final_products = []
assigned_ids = set()

# Find and place ID 1
aerosound = next(p for p in base_products if "AeroSound" in p['title'])
aerosound['id'] = 1
final_products.append(aerosound)
assigned_ids.add(1)

# Find and place ID 17
quantumbook = next(p for p in base_products if "QuantumBook" in p['title'])
quantumbook['id'] = 17
final_products.append(quantumbook)
assigned_ids.add(17)

# Find and place ID 26
zenbook = next(p for p in base_products if "ZenBook" in p['title'])
zenbook['id'] = 26
final_products.append(zenbook)
assigned_ids.add(26)

# Assign remaining products to available IDs from 2 to 52
next_id = 2
for p in base_products:
    if p['title'] in [aerosound['title'], quantumbook['title'], zenbook['title']]:
        continue
    while next_id in assigned_ids:
        next_id += 1
    p['id'] = next_id
    assigned_ids.add(next_id)
    final_products.append(p)

final_products.sort(key=lambda x: x['id'])
print(f"Final Products Prepared: {len(final_products)} products.")
print("Sample product IDs:")
for p in final_products[:5]:
    print(f"  ID {p['id']:2d}: {p['title']} ({p['category']})")
print(f"  ID 17: {next(p['title'] for p in final_products if p['id'] == 17)}")
print(f"  ID 26: {next(p['title'] for p in final_products if p['id'] == 26)}")

# Format products as JavaScript array
js_products = []
for p in final_products:
    item_str = f"""          {{
            id: {p['id']},
            category: '{p['category']}',
            title: {json.dumps(p['title'])},
            description: {json.dumps(p['description'])},
            price: {p['price']},
            rating: {p['rating']},
            reviews: {p['reviews']},
            image: '{p['image']}',
            specs: JSON.stringify({json.dumps(p['specs'])})
          }}"""
    js_products.append(item_str)

js_products_seed_code = "const productsSeed = [\n" + ",\n".join(js_products) + "\n        ];"

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace productsSeed
seed_pattern = re.compile(r'const productsSeed = \[.*?\];', re.DOTALL)
if seed_pattern.search(html):
    html = seed_pattern.sub(lambda m: js_products_seed_code, html, count=1)
    print("[1] Replaced productsSeed with 52 products across all 16 categories.")
else:
    print("[ERROR] Could not find productsSeed in index.html")

# 2. Update Multi-Seller offers seeding to loop up to 52 products
seller_offers_seed = '''        // 5. Seed Multi-Seller Offers
        // NOTE: Product ID 17 ("QuantumBook Ultra 14") has stock_quantity = 1 for Seller 1 (CONCURRENCY SETUP)!
        const sellerOffers = [
          // QuantumBook Ultra 14 (ID 17): CRITICAL CONCURRENCY SETUP
          { pid: 17, sid: 1, sname: 'PrimeTech Solutions', price: 74999, stock: 1, days: 1 },
          { pid: 17, sid: 2, sname: 'CloudRetail Direct', price: 73499, stock: 0, days: 4 }, // Competitor Out of Stock
          { pid: 17, sid: 3, sname: 'ApexDeals India', price: 76200, stock: 3, days: 2 },

          // ZenBook Pro 16X (ID 26)
          { pid: 26, sid: 1, sname: 'PrimeTech Solutions', price: 149990, stock: 4, days: 1 },
          { pid: 26, sid: 2, sname: 'CloudRetail Direct', price: 147500, stock: 2, days: 3 },
          { pid: 26, sid: 3, sname: 'ApexDeals India', price: 151200, stock: 5, days: 2 },

          // AeroSound X9 (ID 1)
          { pid: 1, sid: 1, sname: 'PrimeTech Solutions', price: 19999, stock: 12, days: 1 },
          { pid: 1, sid: 2, sname: 'CloudRetail Direct', price: 19499, stock: 6, days: 2 }
        ];

        // Seed default offers for all 52 products
        for (let pid = 1; pid <= 52; pid++) {
          if (![1, 17, 26].includes(pid)) {
            const prod = productsSeed.find(p => p.id === pid);
            if (prod) {
              const baseP = prod.price;
              sellerOffers.push({ pid: pid, sid: 1, sname: 'PrimeTech Solutions', price: baseP, stock: 12, days: 1 });
              sellerOffers.push({ pid: pid, sid: 2, sname: 'CloudRetail Direct', price: Math.round(baseP * 0.97), stock: 6, days: 2 });
              if (pid % 2 === 0) {
                sellerOffers.push({ pid: pid, sid: 3, sname: 'ApexDeals India', price: Math.round(baseP * 1.02), stock: 8, days: 3 });
              }
            }
          }
        }'''

seller_pattern = re.compile(r'// 5\. Seed Multi-Seller Offers.*?for \(let pid = 1; pid <= 26; pid\+\+\) \{.*?\}\s*\}', re.DOTALL)
if seller_pattern.search(html):
    html = seller_pattern.sub(lambda m: seller_offers_seed, html, count=1)
    print("[2] Replaced Multi-Seller offers seeding for all 52 products.")
else:
    # Try alternate match if loop was already changed
    seller_pattern2 = re.compile(r'// 5\. Seed Multi-Seller Offers.*?sellerOffers\.forEach', re.DOTALL)
    if seller_pattern2.search(html):
        html = seller_pattern2.sub(lambda m: seller_offers_seed + '\n\n        sellerOffers.forEach', html, count=1)
        print("[2b] Replaced Multi-Seller offers seeding.")

# 3. Update Warehouse physical inventory for all 52 products
warehouse_seed = '''        // 6. Seed Warehouse Physical Inventory
        for (let pid = 1; pid <= 52; pid++) {
          const totalStock = pid === 17 ? 4 : 25;
          db.run(`INSERT INTO inventory (warehouse_id, product_id, stock_on_hand, stock_reserved) VALUES (101, ?, ?, 0)`, [pid, totalStock]);
        }'''

warehouse_pattern = re.compile(r'// 6\. Seed Warehouse Physical Inventory.*?for \(let pid = 1; pid <= \d+; pid\+\+\) \{.*?\}', re.DOTALL)
if warehouse_pattern.search(html):
    html = warehouse_pattern.sub(lambda m: warehouse_seed, html, count=1)
    print("[3] Replaced warehouse physical inventory for 52 products.")

# 4. Overhaul render360Frame to render the ACTUAL PRODUCT IMAGE
render_360_complete = '''    /* ==========================================================================
       INTERACTIVE 360-DEGREE PRODUCT VIEW ENGINE (REAL PRODUCT PHOTOGRAPHY)
       ========================================================================== */
    let active360Img = new Image();
    let is360ImgLoaded = false;

    function load360ProductImage(url) {
      is360ImgLoaded = false;
      active360Img = new Image();
      active360Img.crossOrigin = "anonymous";
      active360Img.onload = () => {
        is360ImgLoaded = true;
        render360Frame();
      };
      active360Img.onerror = () => {
        is360ImgLoaded = false;
        render360Frame();
      };
      active360Img.src = url;
    }

    function setProductViewMode(mode) {
      const photoBtn = document.getElementById('view-mode-photo-btn');
      const btn360 = document.getElementById('view-mode-360-btn');
      const photoContainer = document.getElementById('modal-photo-container');
      const container360 = document.getElementById('modal-360-container');

      if (mode === '360') {
        photoBtn.className = 'text-xs font-bold px-3 py-1 rounded bg-gray-100 text-gray-700 hover:bg-gray-200 flex items-center gap-1';
        btn360.className = 'text-xs font-bold px-3 py-1 rounded bg-gray-900 text-white flex items-center gap-1.5';
        photoContainer.classList.add('hidden');
        container360.classList.remove('hidden');
        
        if (activeModalProduct && (!active360Img.src || !active360Img.src.includes(activeModalProduct.primary_image_url))) {
          load360ProductImage(activeModalProduct.primary_image_url);
        } else {
          render360Frame();
        }
      } else {
        photoBtn.className = 'text-xs font-bold px-3 py-1 rounded bg-gray-900 text-white flex items-center gap-1';
        btn360.className = 'text-xs font-bold px-3 py-1 rounded bg-gray-100 text-gray-700 hover:bg-amazon-amber hover:text-gray-950 flex items-center gap-1.5 transition';
        photoContainer.classList.remove('hidden');
        container360.classList.add('hidden');
        stop360AutoSpin();
      }
      lucide.createIcons();
    }

    function init360CanvasEvents() {
      const canvas = document.getElementById('product-360-canvas');
      if (!canvas) return;

      canvas.addEventListener('mousedown', (e) => {
        is360Dragging = true;
        dragStartX = e.clientX;
        dragStartAngle = view360Angle;
        stop360AutoSpin();
      });

      window.addEventListener('mousemove', (e) => {
        if (!is360Dragging) return;
        const deltaX = e.clientX - dragStartX;
        view360Angle = (dragStartAngle + Math.round(deltaX * 0.75)) % 360;
        if (view360Angle < 0) view360Angle += 360;
        render360Frame();
      });

      window.addEventListener('mouseup', () => {
        is360Dragging = false;
      });

      // Touch events for mobile
      canvas.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
          is360Dragging = true;
          dragStartX = e.touches[0].clientX;
          dragStartAngle = view360Angle;
          stop360AutoSpin();
        }
      });

      window.addEventListener('touchmove', (e) => {
        if (!is360Dragging || e.touches.length !== 1) return;
        const deltaX = e.touches[0].clientX - dragStartX;
        view360Angle = (dragStartAngle + Math.round(deltaX * 0.75)) % 360;
        if (view360Angle < 0) view360Angle += 360;
        render360Frame();
      });

      window.addEventListener('touchend', () => {
        is360Dragging = false;
      });
    }

    function render360Frame() {
      const canvas = document.getElementById('product-360-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;

      ctx.clearRect(0, 0, w, h);

      // Degree indicator HUD
      const degText = `${Math.round(view360Angle)}° Azimuth`;
      const degInd = document.getElementById('spin-deg-indicator');
      if (degInd) degInd.textContent = degText;

      const cx = w / 2;
      const cy = h - 65; // Pedestal center near bottom
      const radX = 145;
      const radY = 40;

      // 1. TURNTABLE BASE / PEDESTAL
      // Base ground shadow
      const gradBase = ctx.createRadialGradient(cx, cy + 6, 20, cx, cy + 6, radX + 15);
      gradBase.addColorStop(0, 'rgba(0, 0, 0, 0.35)');
      gradBase.addColorStop(0.7, 'rgba(0, 0, 0, 0.12)');
      gradBase.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = gradBase;
      ctx.beginPath();
      ctx.ellipse(cx, cy + 6, radX + 15, radY + 8, 0, 0, Math.PI * 2);
      ctx.fill();

      // Pedestal Cylinder Edge (3D bevel)
      ctx.fillStyle = '#cbd5e1';
      ctx.beginPath();
      ctx.ellipse(cx, cy + 10, radX * 0.92, radY * 0.92, 0, 0, Math.PI * 2);
      ctx.fill();

      // Top Glass Pedestal Disc
      const discGrad = ctx.createLinearGradient(cx - radX, cy - radY, cx + radX, cy + radY);
      discGrad.addColorStop(0, '#ffffff');
      discGrad.addColorStop(0.5, '#f8fafc');
      discGrad.addColorStop(1, '#e2e8f0');
      ctx.fillStyle = discGrad;
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.ellipse(cx, cy, radX * 0.92, radY * 0.92, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Inner disc ring
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(cx, cy, radX * 0.78, radY * 0.78, 0, 0, Math.PI * 2);
      ctx.stroke();

      // Degree calibration tick marks
      for (let deg = 0; deg < 360; deg += 30) {
        const rad = (deg - view360Angle) * (Math.PI / 180);
        const px = cx + Math.cos(rad) * (radX * 0.82);
        const py = cy + Math.sin(rad) * (radY * 0.82);
        const isMajor = (deg % 90 === 0);
        ctx.fillStyle = isMajor ? '#0f172a' : '#94a3b8';
        ctx.beginPath();
        ctx.arc(px, py, isMajor ? 3 : 1.5, 0, Math.PI * 2);
        ctx.fill();
      }

      // Center pivot point
      ctx.fillStyle = '#64748b';
      ctx.beginPath();
      ctx.arc(cx, cy, 3, 0, Math.PI * 2);
      ctx.fill();

      // 2. PRODUCT RENDERING (ACTUAL PRODUCT IMAGE WITH 3D PERSPECTIVE)
      const rad = view360Angle * (Math.PI / 180);
      const cosA = Math.cos(rad);
      const sinA = Math.sin(rad);

      // Product Dimensions
      const targetH = 180 * view360Zoom;
      const aspect = (active360Img.naturalWidth && active360Img.naturalHeight)
        ? (active360Img.naturalWidth / active360Img.naturalHeight)
        : 1.0;
      const targetW = Math.min(230, targetH * aspect);
      const bottomY = cy - 10; // Rests firmly on pedestal disc surface

      // Ground Contact Shadow directly under product
      ctx.save();
      ctx.beginPath();
      const shadowW = (targetW * 0.48 * Math.abs(cosA)) + 18;
      ctx.ellipse(cx, cy - 2, shadowW, 10, 0, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 0, 0, 0.38)';
      ctx.fill();
      ctx.restore();

      // Pedestal Mirror Reflection (Luxury showroom glass effect)
      if (is360ImgLoaded && active360Img.complete) {
        ctx.save();
        ctx.beginPath();
        ctx.ellipse(cx, cy, radX * 0.90, radY * 0.90, 0, 0, Math.PI * 2);
        ctx.clip(); // Keep reflection inside the pedestal disc

        ctx.translate(cx, cy - 5);
        ctx.scale(cosA, -0.32); // Flipped and squashed
        ctx.globalAlpha = 0.20;
        ctx.drawImage(active360Img, -targetW / 2, 0, targetW, targetH);
        ctx.restore();
      }

      // Product 3D Yaw Rotation
      ctx.save();
      ctx.translate(cx, bottomY);

      // Scale horizontally by cos(angle) to create genuine 3D perspective spin
      const rotW = Math.max(10, Math.abs(cosA) * targetW);
      const isFront = (view360Angle <= 90 || view360Angle >= 270);

      if (is360ImgLoaded && active360Img.complete) {
        if (isFront) {
          // FRONT HEMISPHERE: Render the actual real product photograph!
          ctx.save();
          // Draw the real product image with perspective compression
          ctx.drawImage(active360Img, -rotW / 2, -targetH, rotW, targetH);

          // Dynamic light sheen / specular reflection sweep that moves with rotation angle
          const lightGrad = ctx.createLinearGradient(-rotW / 2, -targetH, rotW / 2, 0);
          const sweep = 0.5 + 0.5 * Math.sin(rad);
          lightGrad.addColorStop(Math.max(0, sweep - 0.25), 'rgba(255, 255, 255, 0)');
          lightGrad.addColorStop(sweep, 'rgba(255, 255, 255, 0.32)');
          lightGrad.addColorStop(Math.min(1, sweep + 0.25), 'rgba(255, 255, 255, 0)');
          ctx.fillStyle = lightGrad;
          ctx.fillRect(-rotW / 2, -targetH, rotW, targetH);
          ctx.restore();

        } else {
          // REAR HEMISPHERE (Back of the product):
          // Photorealistic rear chassis with brushed finish, brand logo, serial tag, and port accents
          ctx.save();
          const palette = colorwayPalettes[active360Colorway] || colorwayPalettes.onyx;
          
          // Backplate silhouette
          ctx.beginPath();
          ctx.roundRect(-rotW / 2, -targetH, rotW, targetH, 14);
          
          const backGrad = ctx.createLinearGradient(-rotW / 2, -targetH, rotW / 2, 0);
          backGrad.addColorStop(0, `rgb(${palette.r - 20}, ${palette.g - 20}, ${palette.b - 20})`);
          backGrad.addColorStop(0.5, `rgb(${palette.r + 30}, ${palette.g + 30}, ${palette.b + 30})`);
          backGrad.addColorStop(1, `rgb(${palette.r - 15}, ${palette.g - 15}, ${palette.b - 15})`);
          ctx.fillStyle = backGrad;
          ctx.fill();
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
          ctx.lineWidth = 2;
          ctx.stroke();

          // Authentic rear details & brand insignia
          if (rotW > 45 && activeModalProduct) {
            ctx.fillStyle = '#febd69';
            ctx.font = 'bold 12px system-ui, sans-serif';
            ctx.textAlign = 'center';
            const brand = activeModalProduct.title.split(' ')[0].toUpperCase();
            ctx.fillText(brand, 0, -targetH * 0.65);

            ctx.fillStyle = '#94a3b8';
            ctx.font = 'bold 9px monospace';
            ctx.fillText("ENGINEERED 360°", 0, -targetH * 0.52);

            ctx.fillStyle = '#64748b';
            ctx.font = '8px monospace';
            ctx.fillText(`MODEL: SC-${activeModalProduct.category.toUpperCase().slice(0,4)}-${activeModalProduct.product_id}`, 0, -targetH * 0.40);

            // Metallic vent / port details
            ctx.fillStyle = '#0f172a';
            ctx.beginPath();
            ctx.roundRect(-rotW * 0.25, -targetH * 0.22, rotW * 0.5, 5, 2);
            ctx.fill();
          }
          ctx.restore();
        }

        // Side edge profile bevel (drawn when passing near 90° or 270°)
        if (Math.abs(cosA) < 0.28) {
          ctx.save();
          ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
          ctx.fillRect(-rotW / 2, -targetH, 3, targetH);
          ctx.fillRect(rotW / 2 - 3, -targetH, 3, targetH);
          ctx.restore();
        }

      } else {
        // Loading state: draw a sleek rotating radar spinner on pedestal
        ctx.save();
        ctx.fillStyle = '#3b82f6';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText("Loading 360° Texture...", 0, -80);
        ctx.beginPath();
        ctx.arc(0, -50, 16, 0, Math.PI * 1.5);
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.restore();
      }

      ctx.restore();

      // 3. HUD AZIMUTH COMPASS BADGE (Top-Left overlay)
      ctx.save();
      const compassX = 35;
      const compassY = 35;
      ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
      ctx.beginPath();
      ctx.arc(compassX, compassY, 22, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Needle pointer
      ctx.save();
      ctx.translate(compassX, compassY);
      ctx.rotate(rad);
      ctx.fillStyle = '#ef4444'; // Red pointer
      ctx.beginPath();
      ctx.moveTo(0, -16);
      ctx.lineTo(4, 0);
      ctx.lineTo(-4, 0);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = '#94a3b8'; // Silver back needle
      ctx.beginPath();
      ctx.moveTo(0, 16);
      ctx.lineTo(4, 0);
      ctx.lineTo(-4, 0);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Direction readout
      let dirName = "FRONT";
      if (view360Angle >= 45 && view360Angle < 135) dirName = "RIGHT";
      else if (view360Angle >= 135 && view360Angle < 225) dirName = "REAR";
      else if (view360Angle >= 225 && view360Angle < 315) dirName = "LEFT";

      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`${Math.round(view360Angle)}° ${dirName}`, 64, 38);
      ctx.restore();
    }'''

old_360_func_pattern = re.compile(r'function setProductViewMode\(mode\)\s*\{.*?function toggle360AutoSpin\(\)\s*\{', re.DOTALL)
if old_360_func_pattern.search(html):
    html = old_360_func_pattern.sub(lambda m: render_360_complete + '\n\n    function toggle360AutoSpin() {', html, count=1)
    print("[4] Completely overhauled 360 viewer engine with real product image & 3D perspective!")
else:
    print("[ERROR] Could not find 360 functions to replace.")

# Also update openProductModal to call load360ProductImage
modal_load_old = 'activeModalProduct = p;'
modal_load_new = 'activeModalProduct = p;\n      load360ProductImage(p.primary_image_url);'
if modal_load_old in html and 'load360ProductImage' not in html:
    html = html.replace(modal_load_old, modal_load_new, 1)
    print("[5] Added load360ProductImage call to openProductModal.")

# Also update canvas width and height in html
html = html.replace('id="product-360-canvas" width="400" height="300" class="w-full max-h-[290px]', 'id="product-360-canvas" width="480" height="360" class="w-full max-h-[340px]')

# Write updated index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Updated index.html successfully written! Length: {len(html)} bytes.")
