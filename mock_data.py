"""
mock_data.py — Synthetic e-commerce data for VoxCart
10 orders · 20 products · returns policy
All data is self-generated and contains no real customer information.
"""

# ── Orders ────────────────────────────────────────────────────────────────
# status values: "processing" | "shipped" | "out_for_delivery" | "delivered" | "cancelled"

ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_name": "Amit Kumar",
        "customer_email": "amit.kumar@example.com",
        "status": "delivered",
        "items": [
            {"name": "Sony WH-1000XM5 Headphones", "qty": 1, "price": 24990},
            {"name": "boAt Airdopes 141 TWS Earbuds", "qty": 1, "price": 999},
        ],
        "order_date": "2026-05-02",
        "estimated_delivery": "2026-05-07",
        "actual_delivery": "2026-05-06",
        "total_amount": 25989,
        "tracking_number": "TRK-8821001",
        "payment_method": "UPI",
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_name": "Priya Sharma",
        "customer_email": "priya.sharma@example.com",
        "status": "shipped",
        "items": [
            {"name": "Nike Air Max 270 Running Shoes", "qty": 1, "price": 12495},
        ],
        "order_date": "2026-05-14",
        "estimated_delivery": "2026-05-20",
        "actual_delivery": None,
        "total_amount": 12495,
        "tracking_number": "TRK-8821002",
        "payment_method": "Credit Card",
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_name": "Rahul Verma",
        "customer_email": "rahul.verma@example.com",
        "status": "processing",
        "items": [
            {"name": "Samsung 43-inch 4K UHD Smart TV", "qty": 1, "price": 32990},
        ],
        "order_date": "2026-05-17",
        "estimated_delivery": "2026-05-24",
        "actual_delivery": None,
        "total_amount": 32990,
        "tracking_number": None,
        "payment_method": "EMI (HDFC Bank)",
    },
    "ORD-1004": {
        "order_id": "ORD-1004",
        "customer_name": "Neha Singh",
        "customer_email": "neha.singh@example.com",
        "status": "delivered",
        "items": [
            {"name": "Atomic Habits by James Clear", "qty": 1, "price": 399},
            {"name": "Wings of Fire by APJ Abdul Kalam", "qty": 1, "price": 199},
        ],
        "order_date": "2026-05-10",
        "estimated_delivery": "2026-05-13",
        "actual_delivery": "2026-05-12",
        "total_amount": 598,
        "tracking_number": "TRK-8821004",
        "payment_method": "Debit Card",
    },
    "ORD-1005": {
        "order_id": "ORD-1005",
        "customer_name": "Suresh Patel",
        "customer_email": "suresh.patel@example.com",
        "status": "out_for_delivery",
        "items": [
            {"name": "Prestige Stainless Steel Pressure Cooker 5L", "qty": 1, "price": 2299},
            {"name": "Philips HL7756 Mixer Grinder 750W", "qty": 1, "price": 3495},
        ],
        "order_date": "2026-05-13",
        "estimated_delivery": "2026-05-18",
        "actual_delivery": None,
        "total_amount": 5794,
        "tracking_number": "TRK-8821005",
        "payment_method": "Cash on Delivery",
    },
    "ORD-1006": {
        "order_id": "ORD-1006",
        "customer_name": "Kavya Nair",
        "customer_email": "kavya.nair@example.com",
        "status": "cancelled",
        "items": [
            {"name": "OnePlus Nord CE 4 (8GB/128GB)", "qty": 1, "price": 24999},
        ],
        "order_date": "2026-05-08",
        "estimated_delivery": "2026-05-14",
        "actual_delivery": None,
        "total_amount": 24999,
        "tracking_number": None,
        "payment_method": "UPI",
        "cancellation_reason": "Customer requested cancellation before shipment",
        "refund_status": "Refund of ₹24,999 processed on 2026-05-09",
    },
    "ORD-1007": {
        "order_id": "ORD-1007",
        "customer_name": "Arjun Mehta",
        "customer_email": "arjun.mehta@example.com",
        "status": "delivered",
        "items": [
            {"name": "Levi's 511 Slim Fit Jeans", "qty": 1, "price": 3999},
            {"name": "Puma Dry Cell Training T-Shirt", "qty": 2, "price": 2598},
        ],
        "order_date": "2026-05-05",
        "estimated_delivery": "2026-05-10",
        "actual_delivery": "2026-05-09",
        "total_amount": 6597,
        "tracking_number": "TRK-8821007",
        "payment_method": "VoxCart Wallet",
    },
    "ORD-1008": {
        "order_id": "ORD-1008",
        "customer_name": "Deepika Reddy",
        "customer_email": "deepika.reddy@example.com",
        "status": "processing",
        "items": [
            {"name": "Noise ColorFit Pro 4 Smartwatch", "qty": 1, "price": 3499},
        ],
        "order_date": "2026-05-18",
        "estimated_delivery": "2026-05-23",
        "actual_delivery": None,
        "total_amount": 3499,
        "tracking_number": None,
        "payment_method": "Credit Card",
    },
    "ORD-1009": {
        "order_id": "ORD-1009",
        "customer_name": "Vikram Joshi",
        "customer_email": "vikram.joshi@example.com",
        "status": "shipped",
        "items": [
            {"name": "Pigeon Healthifry Digital Air Fryer 4.2L", "qty": 1, "price": 4999},
        ],
        "order_date": "2026-05-15",
        "estimated_delivery": "2026-05-21",
        "actual_delivery": None,
        "total_amount": 4999,
        "tracking_number": "TRK-8821009",
        "payment_method": "Debit Card",
    },
    "ORD-1010": {
        "order_id": "ORD-1010",
        "customer_name": "Sanjay Gupta",
        "customer_email": "sanjay.gupta@example.com",
        "status": "delivered",
        "items": [
            {"name": "Yonex Nanoray 7 Badminton Racket", "qty": 2, "price": 4998},
            {"name": "Cosco Brazil Football Size 5", "qty": 1, "price": 699},
        ],
        "order_date": "2026-05-01",
        "estimated_delivery": "2026-05-06",
        "actual_delivery": "2026-05-05",
        "total_amount": 5697,
        "tracking_number": "TRK-8821010",
        "payment_method": "Net Banking",
    },
}

# ── Products ──────────────────────────────────────────────────────────────
# stock values: "in_stock" | "limited" | "out_of_stock"

PRODUCTS = [
    # ── Electronics ──────────────────────────────────────────────────────
    {
        "product_id": "PRD-001",
        "name": "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
        "category": "Electronics",
        "price": 24990,
        "stock": "in_stock",
        "rating": 4.8,
        "description": (
            "Industry-leading noise cancellation with Auto NC Optimizer. "
            "30-hour battery life, crystal-clear hands-free calling, and "
            "multipoint Bluetooth connection for two devices simultaneously."
        ),
        "key_features": [
            "30-hour battery with quick charge (3 min = 3 hrs)",
            "Auto NC Optimizer adjusts to wearing style and environment",
            "Multipoint connection — connect two devices at once",
            "Speak-to-Chat pauses music when you start talking",
            "Foldable design with premium carrying case",
        ],
        "keywords": ["sony", "headphones", "noise cancelling", "wireless", "xm5", "wh1000"],
    },
    {
        "product_id": "PRD-002",
        "name": "boAt Airdopes 141 TWS Earbuds",
        "category": "Electronics",
        "price": 999,
        "stock": "in_stock",
        "rating": 4.2,
        "description": (
            "True wireless earbuds with 42-hour total playback, ENx technology "
            "for clear calls, and IPX4 water resistance. Instant voice assistant access."
        ),
        "key_features": [
            "42-hour total playback (6 hrs earbuds + 36 hrs case)",
            "ENx technology for clear call quality",
            "IPX4 water and sweat resistant",
            "Instant voice assistant access",
            "Smooth touch controls",
        ],
        "keywords": ["boat", "earbuds", "tws", "wireless", "airdopes", "earphones"],
    },
    {
        "product_id": "PRD-003",
        "name": "Samsung 43-inch 4K UHD Crystal Smart TV",
        "category": "Electronics",
        "price": 32990,
        "stock": "in_stock",
        "rating": 4.5,
        "description": (
            "43-inch 4K UHD display with Crystal Processor 4K, HDR support, "
            "and built-in Alexa. Access 200+ apps including Netflix, Prime Video, and Hotstar."
        ),
        "key_features": [
            "4K Crystal UHD display with HDR10+ support",
            "Crystal Processor 4K for sharper, clearer picture",
            "Built-in Alexa and Google Assistant",
            "Motion Xcelerator for smooth 60fps action",
            "200+ pre-loaded streaming apps",
        ],
        "keywords": ["samsung", "tv", "television", "4k", "smart tv", "43 inch", "uhd"],
    },
    {
        "product_id": "PRD-004",
        "name": "Noise ColorFit Pro 4 GPS Smartwatch",
        "category": "Electronics",
        "price": 3499,
        "stock": "limited",
        "rating": 4.3,
        "description": (
            "1.72-inch HD display smartwatch with built-in GPS, 100+ sport modes, "
            "SpO2 and heart rate monitoring, and 7-day battery life."
        ),
        "key_features": [
            "1.72-inch HD display with 500 nits brightness",
            "Built-in GPS — no phone needed for route tracking",
            "100+ sport modes including cricket and yoga",
            "SpO2, heart rate, and stress monitoring",
            "7-day battery life, 5 ATM water resistant",
        ],
        "keywords": ["noise", "smartwatch", "colorfit", "watch", "gps", "fitness tracker"],
    },
    {
        "product_id": "PRD-005",
        "name": "OnePlus Nord CE 4 (8GB RAM / 128GB Storage)",
        "category": "Electronics",
        "price": 24999,
        "stock": "in_stock",
        "rating": 4.4,
        "description": (
            "Powered by Snapdragon 7s Gen 2, 6.7-inch 120Hz AMOLED display, "
            "50MP Sony camera, and 100W SUPERVOOC fast charging."
        ),
        "key_features": [
            "Snapdragon 7s Gen 2 processor",
            "6.7-inch 120Hz Super AMOLED display",
            "50MP Sony IMX890 main camera",
            "100W SUPERVOOC charging — full charge in 28 minutes",
            "5500 mAh battery",
        ],
        "keywords": ["oneplus", "nord", "smartphone", "phone", "android", "ce4"],
    },
    {
        "product_id": "PRD-006",
        "name": "Logitech MX Master 3S Wireless Mouse",
        "category": "Electronics",
        "price": 8995,
        "stock": "out_of_stock",
        "rating": 4.7,
        "description": (
            "Advanced wireless mouse with 8K DPI MagSpeed electromagnetic scroll, "
            "ergonomic design, and USB-C quick charging. Works on any surface including glass."
        ),
        "key_features": [
            "8000 DPI MagSpeed electromagnetic scrolling",
            "Works on any surface including glass",
            "USB-C rechargeable — 1 minute charge = 3 hours use",
            "Connect up to 3 devices, switch with one click",
            "Quiet clicks — 90% less click noise",
        ],
        "keywords": ["logitech", "mouse", "wireless", "mx master", "ergonomic"],
    },
    # ── Clothing ─────────────────────────────────────────────────────────
    {
        "product_id": "PRD-007",
        "name": "Levi's 511 Slim Fit Men's Jeans",
        "category": "Clothing",
        "price": 3999,
        "stock": "in_stock",
        "rating": 4.4,
        "description": (
            "Classic slim fit jeans in stretch denim for all-day comfort. "
            "Sits below waist with slim fit through thigh and leg opening."
        ),
        "key_features": [
            "Slim fit — sits below waist",
            "Stretch denim for comfort and flexibility",
            "Available in multiple washes: dark indigo, mid-tone, black",
            "Classic 5-pocket styling",
            "Machine washable",
        ],
        "keywords": ["levis", "jeans", "denim", "slim fit", "511", "men"],
    },
    {
        "product_id": "PRD-008",
        "name": "Nike Air Max 270 Men's Running Shoes",
        "category": "Clothing",
        "price": 12495,
        "stock": "limited",
        "rating": 4.6,
        "description": (
            "Inspired by the Air Max 180 and 93, featuring Nike's biggest heel Air unit yet "
            "for unrivalled, all-day comfort."
        ),
        "key_features": [
            "Nike's tallest Air unit in the heel for maximum cushioning",
            "Lightweight mesh upper for breathability",
            "Foam midsole for lightweight cushioning",
            "Rubber outsole for traction",
            "Available in sizes 6–12 UK",
        ],
        "keywords": ["nike", "shoes", "air max", "running shoes", "sneakers", "270"],
    },
    {
        "product_id": "PRD-009",
        "name": "Puma Dry Cell Training T-Shirt",
        "category": "Clothing",
        "price": 1299,
        "stock": "in_stock",
        "rating": 4.2,
        "description": (
            "Moisture-wicking Dry Cell fabric keeps you dry during workouts. "
            "Slim fit, crew neck design suitable for gym, running, and casual wear."
        ),
        "key_features": [
            "Dry Cell moisture-wicking technology",
            "Lightweight 100% polyester",
            "Slim fit, crew neck",
            "Available in 8 colours",
            "Quick-dry fabric",
        ],
        "keywords": ["puma", "t-shirt", "tshirt", "sports", "dry cell", "training", "gym"],
    },
    {
        "product_id": "PRD-010",
        "name": "Fabindia Pure Cotton Straight Kurta",
        "category": "Clothing",
        "price": 1890,
        "stock": "in_stock",
        "rating": 4.3,
        "description": (
            "Handcrafted pure cotton kurta with block print detailing. "
            "Breathable fabric ideal for Indian summers and festive occasions."
        ),
        "key_features": [
            "100% pure cotton — breathable and soft",
            "Traditional block print detailing",
            "Straight fit, mandarin collar",
            "Side slits for ease of movement",
            "Available in S, M, L, XL, XXL",
        ],
        "keywords": ["fabindia", "kurta", "cotton", "ethnic", "indian wear", "traditional"],
    },
    {
        "product_id": "PRD-011",
        "name": "Arrow Regular Fit Full-Sleeve Formal Shirt",
        "category": "Clothing",
        "price": 1799,
        "stock": "in_stock",
        "rating": 4.1,
        "description": (
            "Premium wrinkle-resistant cotton formal shirt. Classic fit with "
            "spread collar, suitable for office and formal occasions."
        ),
        "key_features": [
            "Wrinkle-resistant cotton blend",
            "Regular fit with spread collar",
            "Full-sleeve with adjustable cuffs",
            "Available in white, blue, grey, and check patterns",
            "Machine washable",
        ],
        "keywords": ["arrow", "shirt", "formal", "office", "full sleeve", "men's shirt"],
    },
    # ── Home & Kitchen ────────────────────────────────────────────────────
    {
        "product_id": "PRD-012",
        "name": "Prestige Stainless Steel Pressure Cooker 5 Litre",
        "category": "Home & Kitchen",
        "price": 2299,
        "stock": "in_stock",
        "rating": 4.6,
        "description": (
            "ISI-certified stainless steel pressure cooker with gasket release system "
            "for safe cooking. Induction and gas compatible."
        ),
        "key_features": [
            "Food-grade stainless steel — no aluminium",
            "Gasket release system for safe pressure release",
            "Induction and gas stove compatible",
            "5-year warranty on body",
            "ISI certified",
        ],
        "keywords": ["prestige", "pressure cooker", "cooker", "stainless steel", "5 litre", "kitchen"],
    },
    {
        "product_id": "PRD-013",
        "name": "Philips HL7756/00 Mixer Grinder 750W",
        "category": "Home & Kitchen",
        "price": 3495,
        "stock": "in_stock",
        "rating": 4.4,
        "description": (
            "750W mixer grinder with 3 stainless steel jars including a chutney jar. "
            "Speed control with pulse function and 2-year warranty."
        ),
        "key_features": [
            "750W copper motor for powerful grinding",
            "3 jars: 1.5L liquidising, 1L grinding, 0.3L chutney",
            "3-speed control with pulse function",
            "Stainless steel blades and jars",
            "2-year warranty",
        ],
        "keywords": ["philips", "mixer grinder", "mixer", "grinder", "blender", "kitchen appliance"],
    },
    {
        "product_id": "PRD-014",
        "name": "Milton Thermosteel Flip Lid Flask 1 Litre",
        "category": "Home & Kitchen",
        "price": 899,
        "stock": "in_stock",
        "rating": 4.5,
        "description": (
            "Double-walled stainless steel vacuum flask that keeps beverages hot for "
            "24 hours and cold for 48 hours."
        ),
        "key_features": [
            "Keeps hot for 24 hours, cold for 48 hours",
            "Double-wall stainless steel vacuum insulation",
            "Food-grade inner wall",
            "Leak-proof flip lid",
            "BPA free",
        ],
        "keywords": ["milton", "flask", "bottle", "thermos", "water bottle", "hot cold"],
    },
    {
        "product_id": "PRD-015",
        "name": "Bajaj Highspeed 1200mm Ceiling Fan",
        "category": "Home & Kitchen",
        "price": 2250,
        "stock": "in_stock",
        "rating": 4.2,
        "description": (
            "Energy-efficient 1200mm ceiling fan with double ball bearings for "
            "silent and smooth operation. 5-year warranty."
        ),
        "key_features": [
            "1200mm sweep, 380 RPM",
            "Energy-efficient — saves up to 30% power",
            "Double ball bearing for silent operation",
            "Rust and corrosion resistant blades",
            "5-year warranty",
        ],
        "keywords": ["bajaj", "ceiling fan", "fan", "1200mm", "electric fan"],
    },
    {
        "product_id": "PRD-016",
        "name": "Pigeon Healthifry Digital Air Fryer 4.2 Litre",
        "category": "Home & Kitchen",
        "price": 4999,
        "stock": "limited",
        "rating": 4.3,
        "description": (
            "Digital air fryer with 8 preset cooking modes and 360° rapid air circulation. "
            "Cook with up to 80% less oil for healthier meals."
        ),
        "key_features": [
            "4.2L capacity — ideal for 3-4 people",
            "8 preset cooking programs",
            "360° rapid air circulation",
            "Up to 80% less oil than traditional frying",
            "Digital touch panel with timer",
        ],
        "keywords": ["pigeon", "air fryer", "fryer", "healthifry", "oil-free cooking", "kitchen"],
    },
    # ── Books ─────────────────────────────────────────────────────────────
    {
        "product_id": "PRD-017",
        "name": "Atomic Habits by James Clear",
        "category": "Books",
        "price": 399,
        "stock": "in_stock",
        "rating": 4.9,
        "description": (
            "A revolutionary guide to building good habits and breaking bad ones. "
            "James Clear presents a proven framework for improving every day."
        ),
        "key_features": [
            "Bestseller — over 15 million copies sold",
            "Practical framework: Make it obvious, attractive, easy, and satisfying",
            "Paperback, 320 pages",
            "Suitable for students and professionals",
            "ISBN: 978-1847941831",
        ],
        "keywords": ["atomic habits", "james clear", "book", "self help", "habits", "productivity"],
    },
    {
        "product_id": "PRD-018",
        "name": "Wings of Fire: An Autobiography by APJ Abdul Kalam",
        "category": "Books",
        "price": 199,
        "stock": "in_stock",
        "rating": 4.8,
        "description": (
            "The inspiring life story of India's Missile Man and former President Dr. APJ Abdul Kalam. "
            "A must-read for every Indian student and professional."
        ),
        "key_features": [
            "Autobiography of former President of India",
            "Describes journey from Rameswaram to ISRO and Rashtrapati Bhavan",
            "Paperback, 196 pages",
            "Over 2 million copies sold in India",
            "Translated into 13 languages",
        ],
        "keywords": ["wings of fire", "kalam", "apj", "autobiography", "book", "inspiration"],
    },
    # ── Sports ────────────────────────────────────────────────────────────
    {
        "product_id": "PRD-019",
        "name": "Yonex Nanoray 7 Badminton Racket",
        "category": "Sports",
        "price": 2499,
        "stock": "in_stock",
        "rating": 4.5,
        "description": (
            "Lightweight graphite badminton racket designed for offensive play. "
            "Ultra slim shaft reduces air resistance for faster swings."
        ),
        "key_features": [
            "Isometric head shape for larger sweet spot",
            "Ultra-slim shaft for faster swing speed",
            "Built-in T-joint for greater durability",
            "Weight: 85g (unstrung), 4U (average)",
            "Comes with full-length cover",
        ],
        "keywords": ["yonex", "badminton", "racket", "nanoray", "sports", "badminton racket"],
    },
    {
        "product_id": "PRD-020",
        "name": "Cosco Brazil Football Size 5",
        "category": "Sports",
        "price": 699,
        "stock": "in_stock",
        "rating": 4.1,
        "description": (
            "32-panel machine-stitched football with nylon-wound butyl bladder "
            "for consistent bounce. Suitable for practice and recreational play."
        ),
        "key_features": [
            "Size 5 — standard match size",
            "32-panel machine-stitched construction",
            "Nylon-wound butyl bladder for consistent bounce",
            "PVC outer cover — durable on all surfaces",
            "Suitable for grass, artificial turf, and concrete",
        ],
        "keywords": ["cosco", "football", "soccer ball", "ball", "sports", "size 5"],
    },
]

# ── Returns Policy ────────────────────────────────────────────────────────

RETURNS_POLICY = {
    "standard_window_days": 30,
    "categories": {
        "Electronics": {
            "window_days": 15,
            "notes": "Must include all original accessories, manuals, and box. Item should be in original condition with no physical damage.",
        },
        "Clothing": {
            "window_days": 30,
            "notes": "Must be unworn with original tags still attached. Washed or altered items cannot be returned.",
        },
        "Home & Kitchen": {
            "window_days": 30,
            "notes": "Must be unused and in original packaging. Appliances must not have been installed.",
        },
        "Books": {
            "window_days": 10,
            "notes": "No highlighting, torn pages, or writing allowed. Sealed books must remain sealed.",
        },
        "Sports": {
            "window_days": 30,
            "notes": "Must be unused and in original packaging with all accessories.",
        },
    },
    "non_returnable_items": [
        "Digital downloads and software",
        "Perishable goods",
        "Personalized or custom-made items",
        "Hygiene products once opened (innerwear, swimwear)",
        "Hazardous materials",
    ],
    "eligibility_conditions": [
        "Item must be in original, unused condition",
        "Original packaging, tags, and accessories must be intact",
        "Purchase receipt or order ID is required",
        "Return request must be raised within the applicable return window",
        "Items showing signs of use, physical damage, or tampering are not eligible",
    ],
    "how_to_return": [
        "Step 1: Log in to VoxCart and go to 'My Orders'",
        "Step 2: Select the item and click 'Return or Exchange'",
        "Step 3: Choose reason and confirm pickup address",
        "Step 4: Our courier partner will collect the item from your doorstep",
        "Step 5: Refund processed within 5–7 business days after pickup",
    ],
    "refund_timeline": {
        "VoxCart Wallet": "2–3 business days",
        "UPI / Net Banking": "5–7 business days",
        "Credit / Debit Card": "5–7 business days",
        "Cash on Delivery": "5–7 business days (bank transfer)",
        "EMI": "EMI cancellation processed within 7–10 business days",
    },
    "exchange_policy": (
        "Exchanges are available within 7 days of delivery for size or colour issues "
        "on Clothing and Sports items. Electronics can only be exchanged for the same "
        "model if the item is defective on arrival."
    ),
    "damaged_or_wrong_item": (
        "If you received a damaged, defective, or wrong item, raise a complaint within "
        "48 hours of delivery with photos. We will arrange a free replacement or full refund "
        "at no cost to you, regardless of the return window."
    ),
    "customer_support": {
        "phone": "1800-572-5678 (toll-free, Mon–Sat, 9 AM – 9 PM)",
        "email": "support@voxcart.in",
        "chat": "Available on voxcart.in (24/7)",
    },
}
