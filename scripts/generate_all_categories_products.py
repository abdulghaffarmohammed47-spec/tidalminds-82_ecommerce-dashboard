import json

# 16 Broad Categories
categories = [
    'Electronics', 'Laptops', 'Audio', 'Displays', 'Peripherals', 
    'Smart Devices', 'Fashion', 'Home & Kitchen', 'Grocery', 
    'Beauty', 'Sports & Fitness', 'Automotive', 'Toys & Games', 
    'Baby Care', 'Health & Wellness', 'Office & Industrial'
]

# 52 Products (3-4 per category) with authentic, verified high-resolution product photography
products = [
    # --- 1. Laptops ---
    {
        "id": 1,
        "category": "Laptops",
        "title": "QuantumBook Ultra 14 Lightweight Laptop",
        "description": "AMD Ryzen 7 7840U, 16GB LPDDR5, 1TB NVMe, 2.8K 90Hz Display, 18hr Battery. Secondary accessible M.2 PCIe 4.0 SSD expansion slot.",
        "price": 74999,
        "rating": 4.8,
        "reviews": 512,
        "image": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&auto=format&fit=crop&q=80",
        "specs": {"CPU": "AMD Ryzen 7 7840U (8C/16T)", "RAM": "16GB LPDDR5", "Storage": "1TB NVMe (expandable)", "Weight": "1.18 kg", "Display": "14\" 2.8K 90Hz OLED"}
    },
    {
        "id": 2,
        "category": "Laptops",
        "title": "ZenBook Pro 16X OLED 16\" Creator Laptop",
        "description": "Core i9-13900H, RTX 4070, 32GB LPDDR5X, 2TB SSD, 3.2K 120Hz Touch OLED. Dual Thunderbolt 4 ports with dual 4K external display support.",
        "price": 149990,
        "rating": 4.9,
        "reviews": 342,
        "image": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80",
        "specs": {"CPU": "Intel Core i9-13900H", "GPU": "NVIDIA RTX 4070 8GB", "RAM": "32GB LPDDR5X", "Storage": "2TB NVMe Gen4", "Display": "16.0\" 3.2K 120Hz OLED HDR"}
    },
    {
        "id": 3,
        "category": "Laptops",
        "title": "ThinkPad X1 Carbon Gen 12 Ultrabook",
        "description": "Intel Core Ultra 7 155H, 32GB LPDDR5X, 1TB SSD, 14\" 2.8K OLED 120Hz, Carbon-Fiber Chassis, MIL-STD 810H tested, legendary ThinkPad keyboard.",
        "price": 134999,
        "rating": 4.7,
        "reviews": 218,
        "image": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
        "specs": {"CPU": "Intel Core Ultra 7 155H", "RAM": "32GB", "Storage": "1TB SSD", "Battery": "Up to 15 hours", "Weight": "1.09 kg"}
    },
    {
        "id": 4,
        "category": "Laptops",
        "title": "ROG Strix SCAR 16 RTX 4080 Gaming Laptop",
        "description": "Intel i9-14900HX, NVIDIA RTX 4080 12GB, 32GB DDR5, 2TB PCIe 4.0, 16\" QHD+ 240Hz Mini-LED Nebula HDR display with G-Sync.",
        "price": 219999,
        "rating": 4.9,
        "reviews": 165,
        "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80",
        "specs": {"CPU": "Intel Core i9-14900HX", "GPU": "RTX 4080 175W TGP", "Display": "16\" QHD+ 240Hz Mini-LED", "Cooling": "Conductonaut Extreme Liquid Metal"}
    },

    # --- 2. Displays ---
    {
        "id": 5,
        "category": "Displays",
        "title": "ProView 34\" Curved WQHD 165Hz Ultrawide Monitor",
        "description": "1000R deep curvature, 3440x1440 resolution, 98% DCI-P3 wide color gamut, USB-C 90W Power Delivery, integrated KVM switch.",
        "price": 45999,
        "rating": 4.8,
        "reviews": 284,
        "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
        "specs": {"Panel": "Fast VA Quantum Dot 1ms", "Resolution": "3440 x 1440 WQHD", "Refresh Rate": "165Hz", "Ports": "USB-C 90W, 2x HDMI 2.0, DP 1.4"}
    },
    {
        "id": 6,
        "category": "Displays",
        "title": "UltraSharp 32\" 4K IPS Black Studio Display",
        "description": "IPS Black technology with 2000:1 contrast ratio, 4K 3840x2160, 98% DCI-P3, factory color calibrated Delta E < 2, Thunderbolt 4 Daisy Chain.",
        "price": 72499,
        "rating": 4.9,
        "reviews": 190,
        "image": "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=600&auto=format&fit=crop&q=80",
        "specs": {"Panel": "IPS Black 4K", "Contrast": "2000:1", "Color": "1.07 Billion (10-bit)", "Hub": "Thunderbolt 4, RJ45 Ethernet, USB-C"}
    },
    {
        "id": 7,
        "category": "Displays",
        "title": "Odyssey OLED G9 49\" Curved 240Hz Dual QHD",
        "description": "0.03ms response time, 5120x1440 Dual QHD 32:9 super ultrawide, Neo Quantum Processor Pro, DisplayHDR True Black 400, Gaming Hub.",
        "price": 129999,
        "rating": 4.9,
        "reviews": 140,
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
        "specs": {"Aspect Ratio": "32:9 Super Ultrawide", "Panel": "QD-OLED 0.03ms", "Refresh": "240Hz", "Curvature": "1800R"}
    },

    # --- 3. Audio ---
    {
        "id": 8,
        "category": "Audio",
        "title": "AeroSound X9 ANC Wireless Studio Headphones",
        "description": "Active Noise Cancellation, 45mm Beryllium drivers, 55hr battery life, Multipoint Bluetooth 5.3, LDAC lossless codec, memory foam pads.",
        "price": 19999,
        "rating": 4.9,
        "reviews": 894,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
        "specs": {"Drivers": "45mm Custom Beryllium", "ANC": "Hybrid dual-feedforward (-42dB)", "Battery": "55 hours", "Codec": "LDAC, AAC, SBC"}
    },
    {
        "id": 9,
        "category": "Audio",
        "title": "SonicPro Master True Wireless Earbuds",
        "description": "Dual coaxial planar dynamic acoustic architecture, spatial audio with dynamic head tracking, IPX7 waterproof, wireless charging case.",
        "price": 9999,
        "rating": 4.7,
        "reviews": 612,
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
        "specs": {"Driver": "11mm Dynamic + 6mm Planar", "Noise Reduction": "-48dB Deep ANC", "Battery": "38 hours total with case"}
    },
    {
        "id": 10,
        "category": "Audio",
        "title": "StudioCraft 5\" Bi-Amped Powered Reference Monitors",
        "description": "Pair of active studio monitors, 5\" woven Kevlar woofer, 1\" silk dome tweeter, Class A/B bi-amp 70W RMS, acoustic space tuning switches.",
        "price": 24999,
        "rating": 4.8,
        "reviews": 310,
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
        "specs": {"Power": "70W RMS per speaker", "Frequency Response": "52Hz - 22kHz", "Inputs": "XLR Balanced, 1/4\" TRS, RCA"}
    },

    # --- 4. Peripherals ---
    {
        "id": 11,
        "category": "Peripherals",
        "title": "CyberKey Mechanical RGB Hot-Swappable Keyboard",
        "description": "Gateron Pro Yellow linear switches, gasket mount, PBT double-shot keycaps, tri-mode wireless (2.4G/BT/USB-C), south-facing RGB.",
        "price": 6499,
        "rating": 4.8,
        "reviews": 620,
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
        "specs": {"Layout": "75% Compact (82 keys)", "Switches": "Pre-lubed Gateron Yellow", "Mount": "Poron Gasket with FR4 Plate"}
    },
    {
        "id": 12,
        "category": "Peripherals",
        "title": "LuminaDesk Asymmetric Monitor Bar Lamp with Dial",
        "description": "Asymmetric forward-beam optical design (zero screen reflection), 2.4G wireless desktop rotary dial, auto-dimming ambient sensor.",
        "price": 3299,
        "rating": 4.8,
        "reviews": 310,
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
        "specs": {"Color Temp": "2700K - 6500K Stepless", "CRI": "Ra95 Natural spectrum", "Controller": "2.4G Wireless Dial"}
    },
    {
        "id": 13,
        "category": "Peripherals",
        "title": "MasterGrip Pro Wireless Ergonomic Laser Mouse",
        "description": "8000 DPI Darkfield sensor tracks on glass, MagSpeed electromagnetic scroll wheel, USB-C fast charge, Easy-Switch across 3 computers.",
        "price": 7999,
        "rating": 4.9,
        "reviews": 845,
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&auto=format&fit=crop&q=80",
        "specs": {"Sensor": "8000 DPI Darkfield", "Battery": "Up to 70 days on full charge", "Buttons": "7 customizable buttons"}
    },

    # --- 5. Smart Devices ---
    {
        "id": 14,
        "category": "Smart Devices",
        "title": "NovaWatch Ultra Dual-Band GPS Titanium Smartwatch",
        "description": "Aerospace grade-4 titanium casing, sapphire crystal, 100m water resistance, ECG heart sensor, dual-frequency multi-GNSS, 14-day battery.",
        "price": 24999,
        "rating": 4.8,
        "reviews": 380,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
        "specs": {"Display": "1.43\" AMOLED 1000 nits", "Casing": "Grade-4 Titanium", "Sensors": "ECG, SpO2, Optical Heart, Temp", "Battery": "14 days"}
    },
    {
        "id": 15,
        "category": "Smart Devices",
        "title": "SmartHub 10.1\" Touch Display with Auto-Framing",
        "description": "Motorized 10.1\" HD screen that automatically turns to follow you during video calls, built-in Zigbee smart home hub, premium stereo sound.",
        "price": 18999,
        "rating": 4.7,
        "reviews": 290,
        "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
        "specs": {"Screen": "10.1\" HD Touchscreen", "Camera": "13MP with auto-framing", "Smart Hub": "Zigbee + Matter + Thread support"}
    },
    {
        "id": 16,
        "category": "Smart Devices",
        "title": "AuraGlow Smart Multi-Color Atmospheric LED Bar",
        "description": "RGBWW color blending, 16 million colors, screen audio sync for gaming/movies, Matter compatible, Apple HomeKit & Alexa enabled.",
        "price": 4999,
        "rating": 4.6,
        "reviews": 412,
        "image": "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=600&auto=format&fit=crop&q=80",
        "specs": {"Brightness": "800 Lumens", "Connectivity": "Wi-Fi + Bluetooth", "Features": "Music Sync, App Control"}
    },

    # --- 6. Electronics ---
    {
        "id": 17,
        "category": "Electronics",
        "title": "WaveCast 4K HDMI Zero-Latency Wireless Transmitter",
        "description": "Zero-latency (<1ms) wireless 4K 60Hz HDMI transmission up to 100ft line-of-sight, dual-band 60GHz uncompressed video, plug-and-play.",
        "price": 18499,
        "rating": 4.7,
        "reviews": 145,
        "image": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80",
        "specs": {"Latency": "< 1ms", "Resolution": "Up to 4K 60Hz HDR", "Range": "30 meters (100 ft)"}
    },
    {
        "id": 18,
        "category": "Electronics",
        "title": "PowerMax 24000mAh 140W Fast GaN Power Bank",
        "description": "Three-port smart output (2x USB-C PD 3.1 140W + 1x USB-A), digital smart display shows real-time wattage, charges a 16\" MacBook Pro to 50% in 28 mins.",
        "price": 9499,
        "rating": 4.9,
        "reviews": 570,
        "image": "https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?w=600&auto=format&fit=crop&q=80",
        "specs": {"Capacity": "24,000 mAh (86.4Wh)", "Total Output": "140W Max", "Display": "Real-Time OLED Telemetry"}
    },
    {
        "id": 19,
        "category": "Electronics",
        "title": "Alpha 4K 60P Full-Frame Creator Mirrorless Camera",
        "description": "33MP BSI full-frame Exmor R sensor, BIONZ XR processing, 4K 60p 10-bit 4:2:2 video, 759-point fast hybrid AF with real-time eye tracking.",
        "price": 189990,
        "rating": 4.9,
        "reviews": 230,
        "image": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80",
        "specs": {"Sensor": "33MP Full-Frame CMOS", "Video": "4K 60p 10-Bit All-Intra", "Stabilization": "5-Axis In-Body Image Stabilization (5.5 stops)"}
    },

    # --- 7. Home & Kitchen ---
    {
        "id": 20,
        "category": "Home & Kitchen",
        "title": "KitchenMaster Dual-Zone Rapid Air Fryer 9L",
        "description": "Two independent 4.5L cooking zones, sync cook feature, 8 smart presets, rapid 360° cyclonic heat air circulation, non-stick dishwasher safe baskets.",
        "price": 8999,
        "rating": 4.7,
        "reviews": 472,
        "image": "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80",
        "specs": {"Capacity": "9 Liters (Dual 4.5L)", "Power": "1800W", "Temp Range": "40°C to 200°C"}
    },
    {
        "id": 21,
        "category": "Home & Kitchen",
        "title": "IronClad Smart Biometric Heavy-Duty Security Safe",
        "description": "Solid steel pry-resistant construction, 0.2s semiconductor fingerprint scanner, digital keypad, interior LED light, motorized locking bolts.",
        "price": 16999,
        "rating": 4.7,
        "reviews": 185,
        "image": "https://images.unsplash.com/photo-1582139329536-e7284fece509?w=600&auto=format&fit=crop&q=80",
        "specs": {"Locking": "Biometric + Digital Pin + Backup Key", "Steel": "4mm body, 8mm solid door", "Capacity": "45 Liters"}
    },
    {
        "id": 22,
        "category": "Home & Kitchen",
        "title": "RoboClean Laser LiDAR Robotic Vacuum & Mop",
        "description": "5000Pa cyclone suction, LDS LiDAR 3D room navigation, auto-lift vibrating mop, auto-empty dust station holds up to 60 days of debris.",
        "price": 34999,
        "rating": 4.7,
        "reviews": 280,
        "image": "https://images.unsplash.com/photo-1518640467707-6811f4a6ab73?w=600&auto=format&fit=crop&q=80",
        "specs": {"Suction": "5000Pa", "Navigation": "Precision Laser LiDAR", "Battery": "5200mAh (up to 180 mins)", "Auto-Empty": "60-day dock"}
    },
    {
        "id": 23,
        "category": "Home & Kitchen",
        "title": "UltraBreeze Ionizing Bladeless Room Tower Fan",
        "description": "Air multiplier aerodynamic airflow, built-in plasma ionizer, 10 speed settings, ultra-quiet 24dB acoustic sleep profile, magnetic remote.",
        "price": 14999,
        "rating": 4.6,
        "reviews": 260,
        "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&auto=format&fit=crop&q=80",
        "specs": {"Airflow": "500 L/s", "Noise": "24dB to 52dB", "Oscillation": "90 degrees", "Air Purification": "Plasma Ionizer"}
    },

    # --- 8. Beauty ---
    {
        "id": 24,
        "category": "Beauty",
        "title": "SilkGlow Pure Hyaluronic Acid & Niacinamide Serum 50ml",
        "description": "Multi-molecular weight hyaluronic acid complex, 5% niacinamide, peptide infusion for intense barrier restoration and deep radiance.",
        "price": 1299,
        "rating": 4.8,
        "reviews": 840,
        "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80",
        "specs": {"Key Actives": "Triple Hyaluronic Acid + 5% Niacinamide", "Skin Type": "All skin types", "Volume": "50 ml"}
    },
    {
        "id": 25,
        "category": "Beauty",
        "title": "Botanical Renewal Retinol & Squalane Night Cream",
        "description": "Encapsulated 0.3% pure retinol with plant-derived squalane and ceramides to visibly reduce fine lines and support cell renewal overnight.",
        "price": 1799,
        "rating": 4.7,
        "reviews": 420,
        "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
        "specs": {"Actives": "0.3% Encapsulated Retinol + Squalane", "Volume": "50g", "Usage": "Nightly treatment"}
    },
    {
        "id": 26,
        "category": "Beauty",
        "title": "AeroStyler Intelligent Ionic Multi-Styler Dryer",
        "description": "Coanda aerodynamic airflow styling system, high-speed 110,000 RPM brushless motor, intelligent thermal heat control prevents damage.",
        "price": 31999,
        "rating": 4.9,
        "reviews": 510,
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=80",
        "specs": {"Motor": "110,000 RPM Brushless", "Attachments": "6 magnetic styling heads", "Heat Settings": "4 temperatures + Cold Shot"}
    },

    # --- 9. Sports & Fitness ---
    {
        "id": 27,
        "category": "Sports & Fitness",
        "title": "FitPulse Motorized Folding Smart Treadmill",
        "description": "3.0 HP continuous quiet brushless motor, 15% automatic incline, anti-shock 5-layer belt, interactive coaching display, Bluetooth audio.",
        "price": 52999,
        "rating": 4.6,
        "reviews": 140,
        "image": "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=600&auto=format&fit=crop&q=80",
        "specs": {"Motor": "3.0 HP Brushless", "Speed": "0.8 - 18 km/h", "Running Area": "135 x 48 cm", "Weight Capacity": "130 kg"}
    },
    {
        "id": 28,
        "category": "Sports & Fitness",
        "title": "HydroPeak Pro 1L Smart UV-C Insulated Bottle",
        "description": "Double-wall vacuum insulation, UV-C automatic sanitizing cap destroys 99.9% bio-contaminants, 24hr cold retention, rechargeable battery.",
        "price": 2499,
        "rating": 4.5,
        "reviews": 210,
        "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80",
        "specs": {"Capacity": "1000 ml", "Steel": "18/8 Pro-Grade Stainless", "Self-Cleaning": "UV-C LED every 2 hours"}
    },
    {
        "id": 29,
        "category": "Sports & Fitness",
        "title": "X-Grip Adjustable Quick-Lock Smart Dumbbell Pair 24kg",
        "description": "Turn of a dial weight selection from 2.5kg to 24kg per dumbbell, laser-cut steel weight plates, anti-slip knurled grip handle.",
        "price": 17999,
        "rating": 4.9,
        "reviews": 412,
        "image": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80",
        "specs": {"Weight Range": "2.5kg to 24kg per dumbbell", "Settings": "15 increments", "Plates": "Heavy-duty laser cut steel"}
    },
    {
        "id": 30,
        "category": "Sports & Fitness",
        "title": "YogiMat Premium Non-Slip Natural Tree Rubber Yoga Mat",
        "description": "Eco-friendly sustainably harvested natural tree rubber base with ultra-absorbent polyurethane top layer, laser-etched alignment lines.",
        "price": 3499,
        "rating": 4.8,
        "reviews": 320,
        "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&auto=format&fit=crop&q=80",
        "specs": {"Dimensions": "185 cm x 68 cm x 4.5 mm", "Material": "Natural Tree Rubber + PU", "Weight": "2.6 kg"}
    },

    # --- 10. Automotive ---
    {
        "id": 31,
        "category": "Automotive",
        "title": "DashPro 4K Ultra HD Dual Lens Smart Car Dashcam",
        "description": "Front 4K + Rear 1080P Sony STARVIS sensor, built-in GPS tracking, 24-hour parking surveillance, Wi-Fi 6 cloud backup, G-sensor emergency lock.",
        "price": 13999,
        "rating": 4.7,
        "reviews": 410,
        "image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&auto=format&fit=crop&q=80",
        "specs": {"Resolution": "Front 4K 30fps / Rear 1080P", "Sensor": "Sony STARVIS 2 Night Vision", "FOV": "160° ultra-wide"}
    },
    {
        "id": 32,
        "category": "Automotive",
        "title": "MasterCraft 128-Piece Precision Tool & Socket Kit",
        "description": "Chrome vanadium forged steel with heat-treated anti-corrosion finish, 72-tooth reversible quick-release ratchet wrench, blow-molded case.",
        "price": 5499,
        "rating": 4.8,
        "reviews": 390,
        "image": "https://images.unsplash.com/photo-1581235720704-06d3acfcb36f?w=600&auto=format&fit=crop&q=80",
        "specs": {"Pieces": "128 tools", "Steel": "Chrome Vanadium (Cr-V)", "Ratchet": "72-tooth reversible"}
    },
    {
        "id": 33,
        "category": "Automotive",
        "title": "VoltBoost 2000A Emergency Car Battery Jump Starter",
        "description": "Safely jump starts gas engines up to 8.0L and diesel engines up to 6.0L on a single charge. Spark-proof technology, integrated 400-lumen LED flashlight.",
        "price": 6999,
        "rating": 4.8,
        "reviews": 340,
        "image": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=600&auto=format&fit=crop&q=80",
        "specs": {"Peak Amps": "2000A", "Engine Rating": "Up to 8.0L Gas / 6.0L Diesel", "Battery": "Power bank with USB-C"}
    },

    # --- 11. Grocery ---
    {
        "id": 34,
        "category": "Grocery",
        "title": "Gourmet Roast Ethiopian Single-Origin Whole Bean Coffee 1kg",
        "description": "100% Arabica Yirgacheffe specialty beans, medium roast with jasmine, blueberry and citrus notes, artisanal batch roasted in oxygen-free bags.",
        "price": 1899,
        "rating": 4.9,
        "reviews": 950,
        "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&auto=format&fit=crop&q=80",
        "specs": {"Origin": "Yirgacheffe, Ethiopia", "Roast Level": "Medium Light", "Processing": "Natural Sun-Dried", "Weight": "1000g"}
    },
    {
        "id": 35,
        "category": "Grocery",
        "title": "Organic Valley Extra Virgin Cold-Pressed Olive Oil 1L",
        "description": "First cold-pressed Koroneiki olives, acidity strictly below 0.3%, rich in polyphenols and natural antioxidants, bottled in UV-shield dark glass.",
        "price": 1499,
        "rating": 4.9,
        "reviews": 620,
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
        "specs": {"Acidity": "< 0.3%", "Press Method": "Mechanical Cold Extraction (< 27°C)", "Volume": "1000 ml"}
    },
    {
        "id": 36,
        "category": "Grocery",
        "title": "Artisanal Pure Raw Manuka Honey MGO 550+ 500g",
        "description": "Certified high-potency authentic New Zealand raw Manuka honey, minimum MGO 550+ (UMF 15+), raw unpasteurized for immune and digestive wellness.",
        "price": 4299,
        "rating": 4.9,
        "reviews": 310,
        "image": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=600&auto=format&fit=crop&q=80",
        "specs": {"MGO Rating": "550+ mg/kg", "Origin": "New Zealand", "Weight": "500g raw unheated"}
    },

    # --- 12. Fashion ---
    {
        "id": 37,
        "category": "Fashion",
        "title": "Jordan Heritage Men's Classic Leather High-Top Sneakers",
        "description": "Full-grain tumbled genuine leather, encapsulated Air-Sole cushioning unit in heel, solid rubber traction cupsole with deep flex grooves.",
        "price": 11499,
        "rating": 4.8,
        "reviews": 730,
        "image": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600&auto=format&fit=crop&q=80",
        "specs": {"Upper": "100% Genuine Full-Grain Leather", "Sole": "Rubber Cupsole with pivot circle", "Closure": "Lace-Up"}
    },
    {
        "id": 38,
        "category": "Fashion",
        "title": "Heritage Selvedge Raw Denim Classic 5-Pocket Jeans",
        "description": "14.5oz Japanese shuttle-loom selvedge denim, 100% ring-spun cotton, copper hardware rivets, classic straight fit that molds to your body.",
        "price": 5999,
        "rating": 4.7,
        "reviews": 380,
        "image": "https://images.unsplash.com/photo-1542272604-780c96856592?w=600&auto=format&fit=crop&q=80",
        "specs": {"Material": "14.5oz Japanese Selvedge Cotton", "Fit": "Regular Straight Leg", "Hardware": "Solid Copper Rivets"}
    },
    {
        "id": 39,
        "category": "Fashion",
        "title": "Promaster Eco-Drive Titanium Diver's Watch 200M",
        "description": "Solar powered Eco-Drive movement (never needs a battery), Super Titanium Duratect casing, unidirectional rotating bezel, luminous markers.",
        "price": 28999,
        "rating": 4.9,
        "reviews": 295,
        "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=600&auto=format&fit=crop&q=80",
        "specs": {"Movement": "Eco-Drive Solar Quartz", "Case": "Super Titanium", "Water Resistance": "ISO 6425 Diver 200m"}
    },

    # --- 13. Toys & Games ---
    {
        "id": 40,
        "category": "Toys & Games",
        "title": "TitanFlight AI Obstacle Avoidance 4K Camera Drone",
        "description": "3-axis mechanical gimbal, 4K HDR 60fps video, 360° omnidirectional laser obstacle sensing, 35-minute flight time, 10km video transmission.",
        "price": 42999,
        "rating": 4.7,
        "reviews": 195,
        "image": "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=600&auto=format&fit=crop&q=80",
        "specs": {"Camera": "4K HDR 60fps, 1/1.3\" CMOS", "Range": "10 km OcuSync", "Weight": "249 grams", "Flight Time": "35 mins"}
    },
    {
        "id": 41,
        "category": "Toys & Games",
        "title": "NASA Apollo Saturn V Detailed Architecture 1969-Pc Set",
        "description": "Meter-high (1:110 scale) model of the historic NASA Apollo Saturn V, features 3 removable rocket stages, lunar lander, and 3 astronaut microfigures.",
        "price": 14999,
        "rating": 4.9,
        "reviews": 540,
        "image": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=600&auto=format&fit=crop&q=80",
        "specs": {"Pieces": "1,969 building blocks", "Height": "100 cm (39 inches)", "Scale": "1:110 Historic Replica"}
    },
    {
        "id": 42,
        "category": "Toys & Games",
        "title": "OLED Handheld Gaming Console with Vibrant 7\" Screen",
        "description": "7-inch OLED multi-touch display, wide adjustable stand, enhanced audio in handheld and tabletop modes, 64GB internal storage, LAN port dock.",
        "price": 29999,
        "rating": 4.8,
        "reviews": 810,
        "image": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=600&auto=format&fit=crop&q=80",
        "specs": {"Display": "7.0\" OLED 1280x720", "Modes": "TV, Tabletop, Handheld", "Battery": "4.5 to 9 hours"}
    },

    # --- 14. Baby Care ---
    {
        "id": 43,
        "category": "Baby Care",
        "title": "BabyComfort 3-in-1 Modular Smart Reclining Stroller",
        "description": "Aircraft-grade lightweight aluminum frame, one-hand folding mechanism, UPF 50+ canopy, puncture-proof all-terrain wheels, magnetic harness.",
        "price": 28499,
        "rating": 4.8,
        "reviews": 312,
        "image": "https://images.unsplash.com/photo-1591088398332-8a7791972843?w=600&auto=format&fit=crop&q=80",
        "specs": {"Frame": "Aero-grade aluminum", "Weight Capacity": "Up to 22 kg", "Harness": "5-point magnetic lock"}
    },
    {
        "id": 44,
        "category": "Baby Care",
        "title": "SmartView HD Wi-Fi Baby Monitor with Breathing Sensor",
        "description": "1080p HD overhead camera, sleep analytics, background audio monitoring, real-time breathing motion tracking with zero wearables required.",
        "price": 17499,
        "rating": 4.8,
        "reviews": 240,
        "image": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600&auto=format&fit=crop&q=80",
        "specs": {"Resolution": "1080p HD with Night Vision", "Sensors": "Temp, Humidity, Breathing Motion", "Audio": "Two-Way Talk"}
    },
    {
        "id": 45,
        "category": "Baby Care",
        "title": "All-in-One 4-Stage Convertible Car Seat 0-10 Years",
        "description": "Grows with child from infant rear-facing (1.8-18kg) to forward-facing (10-30kg) and booster (18-54kg). Steel-reinforced frame, Simply Safe Adjust.",
        "price": 21999,
        "rating": 4.9,
        "reviews": 460,
        "image": "https://images.unsplash.com/photo-1544126592-807ade215a0b?w=600&auto=format&fit=crop&q=80",
        "specs": {"Lifespan": "10 Years 4-in-1", "Safety": "Side-impact tested, LATCH equipped", "Weight": "10.5 kg"}
    },

    # --- 15. Health & Wellness ---
    {
        "id": 46,
        "category": "Health & Wellness",
        "title": "VelocityX Pro Deep Tissue Percussion Massage Gun",
        "description": "QuietGlide high-torque 60W brushless motor, 16mm amplitude, 5 calibrated speed modes, 6 swappable therapeutic attachments, 6hr battery.",
        "price": 7999,
        "rating": 4.8,
        "reviews": 530,
        "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80",
        "specs": {"Stall Force": "25 kg (55 lbs)", "Amplitude": "16 mm depth", "Battery Life": "6 hours continuous", "Motor": "60W Brushless"}
    },
    {
        "id": 47,
        "category": "Health & Wellness",
        "title": "CardioCheck Clinical Bluetooth Arm Blood Pressure Monitor",
        "description": "Clinically validated dual-sensor accuracy, Easy-Wrap ComFit cuff, irregular heartbeat detector, stores 200 readings for 2 users, Bluetooth sync.",
        "price": 4499,
        "rating": 4.8,
        "reviews": 680,
        "image": "https://images.unsplash.com/photo-1584362917165-526a968579e8?w=600&auto=format&fit=crop&q=80",
        "specs": {"Accuracy": "Pressure: ±3 mmHg", "Cuff Size": "9\" to 17\" arm circumference", "Memory": "2 users x 100 readings"}
    },
    {
        "id": 48,
        "category": "Health & Wellness",
        "title": "Prestige AI Sonic Electric Toothbrush with SenseIQ",
        "description": "SenseIQ technology senses pressure, motion, and coverage up to 100 times per second, adapts intensity automatically, USB-C travel charging case.",
        "price": 15999,
        "rating": 4.9,
        "reviews": 312,
        "image": "https://images.unsplash.com/photo-1559591937-e10b1a03e1c9?w=600&auto=format&fit=crop&q=80",
        "specs": {"Speed": "62,000 brush movements/min", "Battery": "14 days", "AI Sensor": "Real-time feedback via Bluetooth"}
    },

    # --- 16. Office & Industrial ---
    {
        "id": 49,
        "category": "Office & Industrial",
        "title": "Ergonomic Pro Mesh High-Back Executive Chair",
        "description": "Dynamic 3D lumbar support, multi-angle 135° recline with synchronous tilt mechanism, 4D adjustable armrests, BIFMA certified Class-4 gas lift.",
        "price": 21999,
        "rating": 4.8,
        "reviews": 580,
        "image": "https://images.unsplash.com/photo-1580481077195-c3a821a506cb?w=600&auto=format&fit=crop&q=80",
        "specs": {"Material": "Breathable Korean Mesh", "Gas Lift": "Class 4 Heavy-Duty", "Weight Rating": "150 kg", "Recline": "90° - 135°"}
    },
    {
        "id": 50,
        "category": "Office & Industrial",
        "title": "Aeron Kinetic Ergonomic Graphite Desk Chair",
        "description": "Pellicle breathable elastomeric suspension, PostureFit SL adjustable sacral and lumbar pads, forward tilt mechanism, fully adjustable arms.",
        "price": 89999,
        "rating": 4.9,
        "reviews": 415,
        "image": "https://images.unsplash.com/photo-1505797149-43b0069ec26b?w=600&auto=format&fit=crop&q=80",
        "specs": {"Suspension": "8Z Pellicle Elastomeric", "Support": "Dual PostureFit SL", "Warranty": "12-Year 3-Shift Certified"}
    },
    {
        "id": 51,
        "category": "Office & Industrial",
        "title": "Dual-Motor Electric Height Adjustable Standing Desk 60x30",
        "description": "Heavy-duty 3-stage dual electric motors, digital LED memory keypad with 4 presets, anti-collision sensor, solid walnut finish tabletop.",
        "price": 32999,
        "rating": 4.8,
        "reviews": 330,
        "image": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&auto=format&fit=crop&q=80",
        "specs": {"Height Range": "62 cm to 128 cm", "Weight Capacity": "140 kg (308 lbs)", "Motors": "Dual Whisper-Quiet < 45dB"}
    },
    {
        "id": 52,
        "category": "Office & Industrial",
        "title": "AutoMax 100M Micro-Cut Heavy Duty Document Shredder",
        "description": "Shreds up to 100 sheets automatically or 10 sheets manually into 4x10mm micro-cut particles (Security Level P-4), silent operation, 23L pull-out bin.",
        "price": 14499,
        "rating": 4.7,
        "reviews": 180,
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
        "specs": {"Cut Type": "Micro-Cut 4x10mm (P-4)", "Auto Capacity": "100 Sheets", "Bin Size": "23 Liters"}
    }
]

print(f"Total Products: {len(products)}")
cat_counts = {}
for p in products:
    cat_counts[p['category']] = cat_counts.get(p['category'], 0) + 1

print("\nProducts per Category:")
for cat, cnt in sorted(cat_counts.items()):
    print(f"  {cat:<22}: {cnt} items")

# Check all categories are present
for c in categories:
    assert c in cat_counts, f"Missing category: {c}"
print("\nALL 16 Categories successfully covered!")
