import asyncio
import uuid
import sys
import os
import random
import math

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.product import Category, Product, ProductVariant, ProductEmbedding
from app.models.inventory import Inventory, InventoryMovement, MovementType
from app.core.mongo import get_mongo_db
from app.core.security import get_password_hash
from database.seeds.seed_multimedia import synthesize_product_multimedia

try:
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Notice: SentenceTransformer fallback mode: {e}")
    embed_model = None

# Deterministic embedding fallback if transformer fails
def generate_fallback_embedding(text_str: str) -> list:
    random.seed(hash(text_str))
    raw = [random.gauss(0, 1) for _ in range(384)]
    norm = math.sqrt(sum(x*x for x in raw))
    return [x / norm for x in raw]

CATEGORIES_SPEC = {
    "Laptops & Computing": [
        ("QuantumBook Pro X", "Quantum", 1899.00, 2099.00, "16-inch M3 Max Ultra-speed workstation with 64GB Unified RAM and 2TB NVMe PCIe 5.0 SSD."),
        ("AeroBlade Carbon 14", "AeroBlade", 1399.00, 1499.00, "Ultra-light 980g magnesium-lithium alloy body, Intel Core Ultra 9, 32GB LPDDR5X, 120Hz OLED."),
        ("ThinkStation DevEdition 15", "Lenovo", 1549.00, 1699.00, "Linux-optimized developer workstation with AMD Ryzen AI 9, dual NVMe slots, 4K matte anti-glare screen."),
        ("Zenith Infinity Flip", "ASUS", 1199.00, 1299.00, "2-in-1 convertible touchscreen with 360-degree hinge, magnetic active stylus, 100% DCI-P3 color gamut."),
        ("Titan Blade RTX Studio", "Razer", 2799.00, 3099.00, "NVIDIA GeForce RTX 4090 Mobile, 240Hz QHD+ mini-LED display, vapor chamber liquid cooling."),
        ("Chromebook CloudMaster Enterprise", "Google", 699.00, 799.00, "Titan C security chip, all-day 18-hour battery, Wi-Fi 7, military-grade MIL-STD 810H durability."),
        ("Predator Helios Extreme 18", "Acer", 2199.00, 2399.00, "Desktop-class Intel i9-14900HX, mechanical keyboard with per-key RGB, dual AeroBlade 3D fans."),
        ("SwiftEdge AI Thin", "Acer", 999.00, 1099.00, "Sleek 16-inch 3.2K OLED laptop with copilot key, NPU-powered background noise cancellation."),
        ("Surface Studio Pro Book", "Microsoft", 1999.00, 2199.00, "Dynamic woven hinge, PixelSense Flow touchscreen with tactile haptic feedback."),
        ("Galaxy Ultra Book 4", "Samsung", 1649.00, 1799.00, "Dynamic AMOLED 2X touch display, Knox security platform, ecosystem multi-control linking."),
        ("MacBook Pro 14 Space Black", "Apple", 1999.00, 2199.00, "Apple M3 Pro chip with 12-core CPU and 18-core GPU, Liquid Retina XDR display, up to 18 hours battery."),
        ("MacBook Air 15 Starlight", "Apple", 1299.00, 1399.00, "Strikingly thin design with M3 processor, silent fanless architecture, 1080p FaceTime HD camera."),
        ("Dell XPS 16 Platinum", "Dell", 2299.00, 2499.00, "Seamless glass touchpad with capacitive touch function row, 4K+ OLED infinity edge display."),
        ("Dell XPS 13 Ultrabook", "Dell", 1199.00, 1299.00, "Iconic minimalist CNC aluminum build, gorilla glass 3 palm rest, Intel Core Ultra 7."),
        ("HP Spectre x360 Luxury", "HP", 1499.00, 1649.00, "Gem-cut nocturnal blue chassis, 9MP AI camera with night mode, quad speakers tuned by Poly Studio."),
        ("Alienware m16 R2 Cryo", "Alienware", 1899.00, 2099.00, "Cryo-tech cooling system, stealth mode hotkey, QHD+ 240Hz ComfortView Plus display."),
        ("ROG Zephyrus G16 OLED", "ASUS", 2399.00, 2599.00, "Slash lighting array lid, ROG Nebula Display with G-SYNC, CNC aluminum unibody chassis."),
        ("Framework Laptop 16 DIY", "Framework", 1599.00, 1799.00, "Fully modular, upgradable graphics module, hot-swappable expansion cards and customizable keyboard spacers."),
        ("TUF Gaming A15 Rugged", "ASUS", 999.00, 1149.00, "AMD Ryzen 7 8845HS, RTX 4060, anti-dust cooling tunnels, dual Dolby Atmos speakers."),
        ("LG Gram Pro 17 SuperSlim", "LG", 1799.00, 1999.00, "World's lightest 17-inch laptop with discrete RTX 3050, anti-glare IPS display, 77Wh high-capacity battery.")
    ],
    "Smartphones & Tablets": [
        ("Galaxy S24 Ultra AI Titanium", "Samsung", 1299.99, 1399.99, "Built-in S Pen, Titanium frame, 200MP camera with ProVisual AI engine, flat 6.8-inch Dynamic AMOLED."),
        ("iPhone 16 Pro Max Natural Titanium", "Apple", 1199.00, 1299.00, "A18 Pro chip with 6-core GPU, 48MP Fusion camera with 5x telephoto optical zoom, Action button."),
        ("Pixel 9 Pro XL Obsidian", "Google", 1099.00, 1199.00, "Google Tensor G4 chip, Magic Editor AI, Super Actua display, 7 years of OS & security updates."),
        ("OnePlus 12 Flowy Emerald", "OnePlus", 799.99, 899.99, "Snapdragon 8 Gen 3, 4th Gen Hasselblad camera for mobile, 100W SUPERVOOC fast charging."),
        ("Xiaomi 14 Ultra Leica Edition", "Xiaomi", 1299.00, 1450.00, "Quad 50MP Leica optical lenses, 1-inch variable aperture main sensor, ultra-durable Guardian structure."),
        ("iPad Pro 13 Tandem OLED M4", "Apple", 1299.00, 1399.00, "Breakthrough ultra-thin design (5.1mm), Ultra Retina XDR display with tandem OLED, M4 processor."),
        ("Galaxy Tab S9 Ultra AMOLED", "Samsung", 1199.99, 1319.99, "Massive 14.6-inch Dynamic AMOLED 2X, IP68 water resistance on both tablet and included S Pen."),
        ("Nothing Phone (2) Glyph Edition", "Nothing", 599.00, 699.00, "Transparent back casing with customized Glyph LED lighting matrix, Nothing OS 2.5 interface."),
        ("Sony Xperia 1 VI Cinema Edition", "Sony", 1399.00, 1499.00, "Continuous 85-170mm true optical zoom telephoto lens, Bravia AI picture remastering, dedicated shutter button."),
        ("Asus ROG Phone 8 Pro Gaming", "ASUS", 1199.00, 1299.00, "AniMe Vision programmable LED mini-display, AirTrigger ultrasonic buttons, 165Hz Samsung AMOLED."),
        ("Motorola Razr+ Foldable 5G", "Motorola", 999.99, 1099.99, "Largest 4.0-inch external pOLED display, zero-gap teardrop hinge, Dolby Atmos spatial sound."),
        ("Pixel Tablet with Speaker Dock", "Google", 499.00, 549.00, "Hub Mode smart display with magnetic charging speaker dock, Tensor G2, multi-user profiles."),
        ("iPad Air 11 Liquid Retina M2", "Apple", 599.00, 649.00, "Apple M2 silicon, landscape stereo speakers, supports Apple Pencil Pro and Magic Keyboard."),
        ("Vivo X100 Pro Zeiss APO", "Vivo", 999.00, 1099.00, "Zeiss APO floating telephoto camera with Blueprint imaging chip V3, Dimensity 9300 chipset."),
        ("Realme GT 6 AI Flagship Killer", "Realme", 549.00, 629.00, "6000-nit ultra-bright display, 120W SuperVOOC flash charge, Sony LYT-808 OIS main camera."),
        ("Surface Pro 11 Copilot+ PC", "Microsoft", 999.00, 1099.00, "Snapdragon X Elite processor, optional OLED HDR display, flex keyboard with pen storage."),
        ("Honor Magic V2 Ultra-Slim Fold", "Honor", 1499.00, 1699.00, "World-record 9.9mm folded thickness, gearless titanium hinge, 5000mAh silicon-carbon battery."),
        ("Fairphone 5 Modular Sustainable", "Fairphone", 699.00, 749.00, "10-year software support, easily repairable with replaceable modules, 70% fair trade materials."),
        ("Nubia Z60 Ultra Leading Edition", "Nubia", 649.00, 729.00, "Under-display 5th-gen selfie camera with true bezel-less display, custom 35mm optical focal length."),
        ("Blackview Rugged Explorer BV9300", "Blackview", 399.99, 459.99, "15080mAh monster battery, laser rangefinder, IP68/IP69K drop-proof armor construction.")
    ],
    "Audio & Sound": [
        ("AcousticZen ANC Studio Pro", "AcousticZen", 349.99, 399.99, "Reference-grade wireless headphones with adaptive hybrid active noise cancellation and LDAC streaming."),
        ("PulseBeats Pro True Wireless", "PulseBeats", 179.95, 199.95, "IPX7 waterproof earbuds with triple beamforming mic arrays and wireless Qi charging."),
        ("Bose QuietComfort Ultra", "Bose", 429.00, 479.00, "World-class noise cancellation with CustomTune audio calibration and immersive spatial sound."),
        ("Sony WH-1000XM5 Noise Canceling", "Sony", 399.99, 449.99, "Two processors controlling 8 microphones for unprecedented silence, Auto NC Optimizer."),
        ("Sennheiser Momentum 4 Wireless", "Sennheiser", 379.95, 399.95, "Audiophile-inspired 42mm transducer system with 60-hour extraordinary battery endurance."),
        ("AirPods Max Space Gray", "Apple", 549.00, 599.00, "Computational audio with Apple H1 chips in each cup, anodized aluminum earcups, mesh canopy."),
        ("Sonos Ace Wireless Headphones", "Sonos", 449.00, 499.00, "Lossless audio streaming over Bluetooth & USB-C, dynamic head tracking, instant TV audio swap."),
        ("Bang & Olufsen Beoplay H95", "B&O", 999.00, 1199.00, "Custom titanium drivers beneath magnetic lambskin ear cushions, precision mechanical dials."),
        ("JBL PartyBox Stage 320", "JBL", 599.95, 649.95, "Telescopic handle and wide sturdy wheels, 240W RMS explosive audio with synced light shows."),
        ("Marshall Stanmore III Bluetooth", "Marshall", 379.99, 419.99, "Vintage rock-and-roll styling with brass details, two 3/4-inch tweeters and powerful woofer."),
        ("Bowers & Wilkins Px8 Flagship", "Bowers & Wilkins", 699.00, 799.00, "Carbon cone drive units reducing distortion, Nappa leather trim with die-cast aluminum arms."),
        ("Shure SM7B Vocal Dynamic Mic", "Shure", 399.00, 449.00, "Legendary broadcast studio microphone with flat, wide-range frequency response for speech and vocals."),
        ("Audio-Technica ATH-M50xBT2", "Audio-Technica", 199.00, 229.00, "Critically acclaimed M50x sonic signature with dual beamforming mics and multipoint Bluetooth pairing."),
        ("Klipsch The Fives Powered Speakers", "Klipsch", 799.00, 899.00, "Handcrafted real wood finish with HDMI-ARC connection, high-excursion woofers and Tractrix horns."),
        ("Beats Studio Pro Custom Acoustic", "Beats", 349.99, 399.99, "Fully custom acoustic platform with personal spatial audio and lossless audio via USB-C.")
    ],
    "Cameras & Photography": [
        ("Sony Alpha a7 IV Mirrorless", "Sony", 2499.99, 2699.99, "33MP full-frame Exmor R sensor, BIONZ XR engine, 4K 60p 10-bit 4:2:2 video with Real-time Eye AF."),
        ("Canon EOS R5 Mark II", "Canon", 4299.00, 4599.00, "45MP back-illuminated stacked sensor, 8K 60p RAW internal video, Accelerated Capture processor."),
        ("Fujifilm X-T5 Classic Chrome", "Fujifilm", 1699.99, 1899.99, "40.2MP X-Trans CMOS 5 HR sensor, 3-way tilting LCD, dedicated analog dials with film simulations."),
        ("Nikon Z8 Hybrid Professional", "Nikon", 3799.95, 3999.95, "Compact powerhouse with 45.7MP stacked CMOS sensor, blackout-free Real-Live viewfinder, 8K 60p."),
        ("Leica Q3 Summilux 28mm", "Leica", 5995.00, 6495.00, "Full-frame BSI sensor with Triple Resolution Technology (60/36/18MP), fixed Summilux 28mm f/1.7 lens."),
        ("Panasonic Lumix S5 IIX Black", "Panasonic", 2199.99, 2399.99, "Phase Hybrid AF, unlimited video recording with internal active cooling fan, ProRes codec support."),
        ("DJI Osmo Pocket 3 Creator Combo", "DJI", 669.00, 729.00, "1-inch CMOS sensor, 4K 120fps video, 2-inch rotatable OLED touchscreen with 3-axis gimbal stabilization."),
        ("GoPro HERO12 Black Action Cam", "GoPro", 399.99, 449.99, "HyperSmooth 6.0 video stabilization with 360-degree Horizon Lock, 5.3K 60fps HDR video."),
        ("Insta360 X4 8K 360 Action", "Insta360", 499.99, 549.99, "Ultra-crisp 8K 30fps 360-degree video capture with invisible selfie stick effect and removable lens guards."),
        ("Sigma 24-70mm f/2.8 DG DN Art", "Sigma", 1199.00, 1299.00, "Standard zoom lens for full-frame mirrorless mounts with dust and splash-proof brass bayonet mount.")
    ],
    "Gaming & VR": [
        ("Valkyrie Precision Mechanical Keyboard", "Valkyrie", 159.00, 189.00, "Gasket-mounted hot-swappable mechanical keyboard with pre-lubed linear switches and per-key RGB."),
        ("ApexGlide Ultralight Esports Mouse", "ApexGlide", 99.50, 119.50, "49g ultra-lightweight wireless gaming mouse with 30K optical sensor and optical switches."),
        ("PlayStation 5 Pro Console", "Sony", 699.99, 749.99, "PlayStation Spectral Super Resolution (PSSR), advanced ray tracing, 2TB high-speed NVMe internal storage."),
        ("Xbox Series X Carbon Special Edition", "Microsoft", 599.99, 649.99, "12 Teraflops of raw graphical processing power, Quick Resume for multiple titles, 2TB SSD."),
        ("Meta Quest 3 512GB VR Headset", "Meta", 649.99, 699.99, "High-resolution 4K+ Infinite Display with color passthrough mixed reality, pancake optics lenses."),
        ("Steam Deck OLED 1TB Handheld", "Valve", 649.00, 699.00, "HDR OLED screen with 90Hz refresh rate, 50Wh battery, customized AMD 6nm APU."),
        ("ASUS ROG Ally X Handheld Console", "ASUS", 799.99, 849.99, "AMD Ryzen Z1 Extreme, 24GB LPDDR5X RAM, 80Wh massive battery, full Windows 11 compatibility."),
        ("Logitech G Pro X Superlight 2", "Logitech", 159.99, 179.99, "LIGHTFORCE hybrid optical-mechanical switches, HERO 2 sensor with sub-micron tracking."),
        ("Corsair K100 RGB Optical Gaming", "Corsair", 229.99, 249.99, "OPX optical-mechanical key switches with 1.0mm actuation, iCUE control wheel, 44-zone RGB lightedge."),
        ("SteelSeries Arctis Nova Pro Wireless", "SteelSeries", 349.99, 399.99, "Infinity Power System with dual hot-swap batteries, active noise cancellation, GameDAC Gen 2.")
    ],
    "Wearables & Fitness": [
        ("Titanium Smart Watch Series 9", "Titanium", 399.00, 449.00, "Aerospace-grade titanium casing, sapphire crystal face, dual-frequency GPS, ECG, and 100m dive rating."),
        ("Apple Watch Ultra 2 Black Titanium", "Apple", 799.00, 849.00, "Rugged 49mm titanium case, 3000 nits brightest display, dual-frequency GPS, up to 72 hours in Low Power Mode."),
        ("Garmin Fenix 7 Pro Solar Sapphire", "Garmin", 899.99, 999.99, "Power Sapphire solar charging lens, built-in LED flashlight, endurance and hill score metrics."),
        ("Oura Ring Horizon Gen 3", "Oura", 349.00, 399.00, "Sleek biometric smart ring tracking sleep stages, readiness score, daytime HR, and temperature changes."),
        ("Whoop 4.0 Health Monitor", "Whoop", 239.00, 279.00, "Screenless wearable monitoring cardiovascular load, sleep efficiency, recovery rate, and strain coach.")
    ],
    "Home & Kitchen": [
        ("BaristaPro Touch Espresso Machine", "BaristaPro", 799.00, 899.00, "Commercial-grade dual boiler with integrated conical burr grinder and automatic micro-foam steam wand."),
        ("PureAir H13 Medical HEPA Purifier", "PureAir", 199.99, 239.99, "True H13 medical grade filtration with activated carbon honeycomb capturing 99.97% airborne particulates."),
        ("Dyson V15 Detect Absolute", "Dyson", 749.99, 849.99, "Laser reveals invisible dust on hard floors, acoustic piezo sensor counts dust particles in real-time."),
        ("Ninja Foodi Smart XL 6-in-1 Grill", "Ninja", 259.99, 299.99, "Indoor grill and air fryer with smart cook system, 500F cyclonic air for char-grilled flavor."),
        ("Breville Smart Oven Air Fryer Pro", "Breville", 399.95, 449.95, "Element IQ system controlling 6 independent quartz heating elements, 1 cubic foot capacity.")
    ],
    "Clothing & Footwear": [
        ("Aero Comfort Cloud-Foam Sneakers", "Aero", 119.99, 149.99, "Supercritical cloud-foam EVA cushioning with breathable recycled Primeknit upper and continental outsole."),
        ("StormShield All-Weather Parka", "StormShield", 289.00, 349.00, "20,000mm waterproof technical shell parka with 800-fill responsible goose down insulation."),
        ("Arc'teryx Alpha SV Hard Shell", "Arc'teryx", 899.00, 999.00, "GORE-TEX PRO Most Rugged technology, watertight external zippers, engineered for severe alpine conditions."),
        ("Lululemon ABC Classic-Fit Pant", "Lululemon", 128.00, 148.00, "Warpstreme fabric with shape retention, 4-way stretch comfort, hidden zippered passport pocket."),
        ("Patagonia Nano Puff Windproof Jacket", "Patagonia", 239.00, 269.00, "Lightweight 60g PrimaLoft Gold Insulation Eco wrapped in 100% recycled polyester ripstop shell.")
    ]
}

# Real 360 frame URLs (synthetic reliable placeholders)
def generate_360_frames(slug: str) -> list:
    frames = []
    for i in range(1, 37):
        frames.append(f"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80&frame={i:02d}")
    return frames

async def seed_enterprise_db():
    print("================================================================================")
    print("STARTING SMARTCOMMERCE AI ENTERPRISE DATABASE SEED GENERATION (150+ ASSETS)")
    print("================================================================================")
    
    async with AsyncSessionLocal() as db:
        print("[1/5] Purging and initializing PostgreSQL tables...")
        await db.execute(text("TRUNCATE TABLE order_items, orders, user_search_history, inventory_movements, inventory, product_embeddings, product_variants, products, categories, users CASCADE;"))
        await db.commit()

        # 1. Create Seed Accounts
        print("[2/5] Creating seed accounts (Admin, Seller & Customer with Argon2id)...")
        customer_user = User(
            id=uuid.uuid4(),
            email="customer@smartcommerce.dev",
            password_hash=get_password_hash("CustomerPass123!"),
            full_name="Alex Mercer",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        seller_user = User(
            id=uuid.uuid4(),
            email="seller@smartcommerce.dev",
            password_hash=get_password_hash("SellerPass123!"),
            full_name="Marcus Vance",
            role=UserRole.SELLER,
            is_active=True
        )
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@smartcommerce.dev",
            password_hash=get_password_hash("AdminPass123!"),
            full_name="Sarah Connor",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add_all([customer_user, seller_user, admin_user])
        await db.commit()

        # 2. Categories
        print("[3/5] Creating category hierarchies...")
        category_records = {}
        for cat_name in CATEGORIES_SPEC.keys():
            slug = cat_name.lower().replace(" & ", "-").replace(" ", "-")
            cat_obj = Category(id=uuid.uuid4(), name=cat_name, slug=slug)
            db.add(cat_obj)
            category_records[cat_name] = cat_obj
        await db.commit()

        # 3. Products, Variants, Inventory, Embeddings
        print("[4/5] Synthesizing 150+ products, variants, vector embeddings, and inventory...")
        all_products_to_insert = []
        product_embeddings_to_insert = []
        mongo_documents = []

        total_count = 0
        for cat_name, items in CATEGORIES_SPEC.items():
            cat_obj = category_records[cat_name]
            
            # Multiply or generate variations to reach 150+ realistic products
            multiplier = 2 if len(items) >= 20 else 3
            
            for base_item in items:
                for v_idx in range(multiplier):
                    total_count += 1
                    title, brand, base_price, compare_price, desc = base_item
                    
                    if v_idx > 0:
                        title_variant = f"{title} (Edition {v_idx + 1})"
                        slug_variant = f"{title.lower().replace(' ', '-').replace('/', '-')}-v{v_idx + 1}-{total_count}"
                        price_variant = round(base_price * (1 + 0.05 * v_idx), 2)
                    else:
                        title_variant = title
                        slug_variant = f"{title.lower().replace(' ', '-').replace('/', '-')}-{total_count}"
                        price_variant = base_price

                    prod_id = uuid.uuid4()
                    sku = f"SKU-{total_count:04d}-{brand[:3].upper()}"

                    # 384-dim Vector Embedding
                    text_for_embedding = f"{title_variant} {brand} {cat_name} {desc}"
                    if embed_model is not None:
                        try:
                            vec = embed_model.encode(text_for_embedding).tolist()
                        except Exception:
                            vec = generate_fallback_embedding(text_for_embedding)
                    else:
                        vec = generate_fallback_embedding(text_for_embedding)

                    # Product model
                    p = Product(
                        id=prod_id,
                        sku=sku,
                        title=title_variant,
                        slug=slug_variant,
                        category_id=cat_obj.id,
                        brand=brand,
                        base_price=price_variant,
                        compare_at_price=compare_price,
                        has_360_view=True,
                        has_video=True,
                        is_active=True,
                        rating_avg=round(random.uniform(4.2, 5.0), 2),
                        review_count=random.randint(15, 840)
                    )
                    db.add(p)
                    await db.flush()

                    # Embedding model
                    pe = ProductEmbedding(
                        product_id=prod_id,
                        embedding=vec
                    )
                    db.add(pe)

                    # Product Variant
                    variant_id = uuid.uuid4()
                    v_sku = f"{sku}-BASE"
                    variant = ProductVariant(
                        id=variant_id,
                        product_id=prod_id,
                        sku=v_sku,
                        title=f"{title_variant} - Standard",
                        price_override=price_variant,
                        attributes={"edition": f"Standard v{v_idx+1}", "color": "Signature"}
                    )
                    db.add(variant)
                    await db.flush()

                    # Inventory Balance (5% intentionally out-of-stock to test in-stock alternatives)
                    is_out_of_stock = (total_count % 18 == 0)
                    on_hand_qty = 0 if is_out_of_stock else random.randint(12, 150)
                    inv = Inventory(
                        id=uuid.uuid4(),
                        variant_id=variant_id,
                        on_hand=on_hand_qty,
                        reserved=0,
                        safety_stock=2
                    )
                    db.add(inv)

                    # Initial restock movement
                    if on_hand_qty > 0:
                        mov = InventoryMovement(
                            id=uuid.uuid4(),
                            variant_id=variant_id,
                            change_qty=on_hand_qty,
                            movement_type=MovementType.RESTOCK,
                            reference_id="SEED-INITIAL-STOCK"
                        )
                        db.add(mov)

                    # MongoDB Multimedia Document via Deterministic Synthesis Engine
                    media_doc = synthesize_product_multimedia(
                        product_id=str(prod_id),
                        sku=sku,
                        title=title_variant,
                        category_name=cat_name,
                        brand=brand
                    )
                    media_doc["full_description"] = desc
                    mongo_documents.append(media_doc)

        await db.commit()
        print(f"[4/5] Successfully inserted {total_count} products and variants into PostgreSQL.")

    # 4. Insert into MongoDB
    print("[5/5] Storing multimedia & 360-degree assets into MongoDB collection 'product_multimedia'...")
    mongo_db = get_mongo_db() if callable(get_mongo_db) else get_mongo_db
    await mongo_db.product_multimedia.delete_many({})
    await mongo_db.product_metadata.delete_many({})
    
    if mongo_documents:
        await mongo_db.product_multimedia.insert_many(mongo_documents)
        # Also mirror to product_metadata for backward compatibility
        await mongo_db.product_metadata.insert_many(mongo_documents)
    
    print(f"[5/5] Stored {len(mongo_documents)} rich multimedia documents into MongoDB.")
    print("================================================================================")
    print("SEEDING COMPLETE: SMARTCOMMERCE AI IS FULLY POPULATED AND READY!")
    print("================================================================================")

if __name__ == "__main__":
    asyncio.run(seed_enterprise_db())
