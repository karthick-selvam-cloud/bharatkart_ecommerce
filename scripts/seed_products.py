"""
BharatKart Product Seeding Script
Creates 100+ luxury products across all categories with images.

Run: python scripts/seed_products.py
"""

import os
import sys
import django
import random
from decimal import Decimal
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.utils.text import slugify
from apps.products.models import Category, Brand, Product, ProductImage
from apps.accounts.models import User, SellerProfile


# ============================================================
# IMAGE SOURCES (Unsplash - free, no API key required)
# ============================================================
def unsplash_img(photo_id, width=800):
    """Generate an Unsplash image URL"""
    return f"https://images.unsplash.com/{photo_id}?w={width}&q=80&auto=format&fit=crop"


# Real Unsplash photo IDs mapped to product categories
IMAGE_LIBRARY = {
    # ELECTRONICS
    'smartphone': [
        'photo-1511707171634-5f897ff02aa9',
        'photo-1592750475338-74b7b21085ab',
        'photo-1580910051074-3eb694886505',
        'photo-1567581935884-3349723552ca',
        'photo-1512499617640-c74ae3a79d37',
        'photo-1523206489230-c012c64b2b48',
        'photo-1601784551446-20c9e07cdbdb',
        'photo-1585060544812-6b45742d762f',
    ],
    'laptop': [
        'photo-1496181133206-80ce9b88a853',
        'photo-1517336714731-489689fd1ca8',
        'photo-1611186871348-b1ce696e52c9',
        'photo-1541807084-5c52b6b3adef',
        'photo-1588872657578-7efd1f1555ed',
        'photo-1531297484001-80022131f5a1',
    ],
    'headphone': [
        'photo-1505740420928-5e560c06d30e',
        'photo-1484704849700-f032a568e944',
        'photo-1583394838336-acd977736f90',
        'photo-1546435770-a3e426bf472b',
        'photo-1590658268037-6bf12165a8df',
        'photo-1613040809024-b4ef7ba99bc3',
    ],
    'camera': [
        'photo-1502920917128-1aa500764cbd',
        'photo-1516035069371-29a1b244cc32',
        'photo-1606986628253-05620e9b5c6d',
        'photo-1500634245200-e5245c7574ef',
        'photo-1495707902641-75cac588d2e9',
    ],
    'smartwatch': [
        'photo-1546868871-7041f2a55e12',
        'photo-1523275335684-37898b6baf30',
        'photo-1434493789847-2f02dc6ca35d',
        'photo-1579586337278-3befd40fd17a',
        'photo-1508685096489-7aacd43bd3b1',
    ],
    'speaker': [
        'photo-1608043152269-423dbba4e7e1',
        'photo-1545454675-3531b543be5d',
        'photo-1589003077984-894e133dabab',
        'photo-1558756520-22cfe5d382ca',
    ],
    'tablet': [
        'photo-1561154464-82e9adf32764',
        'photo-1544244015-0df4b3ffc6b0',
        'photo-1585790050230-5dd28404ccb9',
    ],
    'gaming': [
        'photo-1606144042614-b2417e99c4e3',
        'photo-1493711662062-fa541adb3fc8',
        'photo-1552820728-8b83bb6b773f',
        'photo-1592840496694-26d035b52b48',
    ],
    'drone': [
        'photo-1473968512647-3e447244af8f',
        'photo-1507582020474-9a35b7d455d9',
        'photo-1579829366248-204fe8413f31',
    ],

    # FASHION
    'mens_shirt': [
        'photo-1602810318383-e386cc2a3ccf',
        'photo-1596755094514-f87e34085b2c',
        'photo-1620012253295-c15cc3e65df4',
        'photo-1603252109303-2751441dd157',
    ],
    'mens_suit': [
        'photo-1594938298603-c8148c4dae35',
        'photo-1507679799987-c73779587ccf',
        'photo-1617137968427-85924c800a22',
    ],
    'womens_dress': [
        'photo-1595777457583-95e059d581b8',
        'photo-1572804013309-59a88b7e92f1',
        'photo-1594633312681-425c7b97ccd1',
        'photo-1585487000160-6ebcfceb0d03',
        'photo-1539008835657-9e8e9680c956',
    ],
    'womens_handbag': [
        'photo-1584917865442-de89df76afd3',
        'photo-1548036328-c9fa89d128fa',
        'photo-1566150905458-1bf1fc113f0d',
        'photo-1591561954557-26941169b49e',
    ],
    'shoes': [
        'photo-1549298916-b41d501d3772',
        'photo-1595950653106-6c9ebd614d3a',
        'photo-1600185365483-26d7a4cc7519',
        'photo-1460353581641-37baddab0fa2',
        'photo-1560769629-975ec94e6a86',
    ],
    'sunglasses': [
        'photo-1511499767150-a48a237f0083',
        'photo-1572635196237-14b3f281503f',
        'photo-1577803645773-f96470509666',
    ],
    'watches': [
        'photo-1524592094714-0f0654e20314',
        'photo-1523170335258-f5ed11844a49',
        'photo-1547996160-81dfa63595aa',
        'photo-1622434641406-a158123450f9',
    ],
    'jewelry': [
        'photo-1515562141207-7a88fb7ce338',
        'photo-1605100804763-247f67b3557e',
        'photo-1573408301185-9146fe634ad0',
        'photo-1611591437281-460bfbe1220a',
    ],

    # HOME & LIVING
    'sofa': [
        'photo-1555041469-a586c61ea9bc',
        'photo-1567016432779-094069958ea5',
        'photo-1540574163026-643ea20ade25',
    ],
    'bed': [
        'photo-1505693416388-ac5ce068fe85',
        'photo-1522771739844-6a9f6d5f14af',
        'photo-1616627561950-9f746e330187',
    ],
    'lamp': [
        'photo-1507473885765-e6ed057f782c',
        'photo-1513506003901-1e6a229e2d15',
        'photo-1540932239986-30128078f3c5',
    ],
    'kitchen': [
        'photo-1556909212-d5b604d0c90d',
        'photo-1556909114-f6e7ad7d3136',
        'photo-1600585152220-90363fe7e115',
    ],
    'decor': [
        'photo-1616486338812-3dadae4b4ace',
        'photo-1615529182904-14819c35db37',
        'photo-1567538096630-e0c55bd6374c',
    ],
    'rugs': [
        'photo-1600166898405-da9535204843',
        'photo-1584100936595-c0654b55a2e2',
    ],

    # BEAUTY
    'skincare': [
        'photo-1556228720-195a672e8a03',
        'photo-1570172619644-dfd03ed5d881',
        'photo-1620916566398-39f1143ab7be',
        'photo-1598440947619-2c35fc9aa908',
        'photo-1608248543803-ba4f8c70ae0b',
    ],
    'makeup': [
        'photo-1596462502278-27bfdc403348',
        'photo-1512496015851-a90fb38ba796',
        'photo-1522335789203-aabd1fc54bc9',
        'photo-1586495777744-4413f21062fa',
    ],
    'fragrance': [
        'photo-1541643600914-78b084683601',
        'photo-1592945403244-b3fbafd7f539',
        'photo-1594035910387-fea47794261f',
        'photo-1587017539504-67cfbddac569',
    ],
    'haircare': [
        'photo-1522338242992-e1a54906a8da',
        'photo-1608248543803-ba4f8c70ae0b',
        'photo-1585232004423-244e0e6904e3',
    ],

    # SPORTS
    'sports': [
        'photo-1461896836934-ffe607ba8211',
        'photo-1517649763962-0c623066013b',
        'photo-1571019613454-1cb2f99b2d8b',
        'photo-1517836357463-d25dfeac3438',
    ],

    # BOOKS
    'books': [
        'photo-1544947950-fa07a98d237f',
        'photo-1512820790803-83ca734da794',
        'photo-1495446815901-a7297e633e8d',
        'photo-1543002588-bfa74002ed7e',
    ],

    # TOYS
    'toys': [
        'photo-1558060370-d644479cb6f7',
        'photo-1587654780291-39c9404d746b',
    ],
}


# ============================================================
# CATEGORY DEFINITIONS
# ============================================================
CATEGORIES = [
    # (name, slug, parent_slug, description)
    ('Electronics', 'electronics', None, 'Latest technology and premium gadgets'),
    ('Fashion', 'fashion', None, 'Timeless style and designer wear'),
    ('Home & Living', 'home-kitchen', None, 'Elegant interiors and modern comforts'),
    ('Beauty', 'beauty', None, 'Premium skincare, makeup and fragrance'),
    ('Sports', 'sports', None, 'Athletic gear and fitness essentials'),
    ('Books', 'books', None, 'Curated reads for the discerning mind'),
    ('Toys', 'toys', None, 'Delightful toys for young minds'),
    
    # Subcategories
    ('Smartphones', 'smartphones', 'electronics', 'Latest flagship phones'),
    ('Laptops', 'laptops', 'electronics', 'Powerful computing machines'),
    ('Audio', 'audio', 'electronics', 'Premium sound systems'),
    ('Cameras', 'cameras', 'electronics', 'Capture the moment'),
    ('Wearables', 'wearables', 'electronics', 'Smart watches and fitness bands'),
    ('Gaming', 'gaming', 'electronics', 'Ultimate gaming experience'),
    ('Drones', 'drones', 'electronics', 'Aerial photography'),
    
    ('Men\'s Fashion', 'mens-fashion', 'fashion', 'Refined menswear'),
    ('Women\'s Fashion', 'womens-fashion', 'fashion', 'Elegant womenswear'),
    ('Footwear', 'footwear', 'fashion', 'Step into luxury'),
    ('Accessories', 'accessories', 'fashion', 'Fine finishing touches'),
    ('Jewelry', 'jewelry', 'fashion', 'Timeless adornments'),
    
    ('Furniture', 'furniture', 'home-kitchen', 'Statement pieces'),
    ('Lighting', 'lighting', 'home-kitchen', 'Illuminating design'),
    ('Kitchenware', 'kitchenware', 'home-kitchen', 'Culinary excellence'),
    ('Home Decor', 'home-decor', 'home-kitchen', 'Artful accents'),
    
    ('Skincare', 'skincare', 'beauty', 'Radiant complexion'),
    ('Makeup', 'makeup', 'beauty', 'Artistry essentials'),
    ('Fragrance', 'fragrance', 'beauty', 'Signature scents'),
    ('Haircare', 'haircare', 'beauty', 'Luxurious hair rituals'),
]


# ============================================================
# BRAND DEFINITIONS
# ============================================================
BRANDS = [
    ('Apple', 'apple', 'Electronics'),
    ('Samsung', 'samsung', 'Electronics'),
    ('Sony', 'sony', 'Electronics'),
    ('LG', 'lg', 'Electronics'),
    ('Dell', 'dell', 'Electronics'),
    ('HP', 'hp', 'Electronics'),
    ('Lenovo', 'lenovo', 'Electronics'),
    ('Asus', 'asus', 'Electronics'),
    ('Bose', 'bose', 'Electronics'),
    ('JBL', 'jbl', 'Electronics'),
    ('Canon', 'canon', 'Electronics'),
    ('Nikon', 'nikon', 'Electronics'),
    ('Nike', 'nike', 'Fashion'),
    ('Adidas', 'adidas', 'Fashion'),
    ('Puma', 'puma', 'Fashion'),
    ('Levi\'s', 'levis', 'Fashion'),
    ('Zara', 'zara', 'Fashion'),
    ('H&M', 'hm', 'Fashion'),
    ('Gucci', 'gucci', 'Fashion'),
    ('Ray-Ban', 'rayban', 'Fashion'),
    ('Titan', 'titan', 'Fashion'),
    ('IKEA', 'ikea', 'Home & Living'),
    ('Urban Ladder', 'urban-ladder', 'Home & Living'),
    ('Philips', 'philips', 'Home & Living'),
    ('Prestige', 'prestige', 'Home & Living'),
    ('Loreal', 'loreal', 'Beauty'),
    ('Maybelline', 'maybelline', 'Beauty'),
    ('Nivea', 'nivea', 'Beauty'),
    ('Forest Essentials', 'forest-essentials', 'Beauty'),
    ('Dior', 'dior', 'Beauty'),
    ('Chanel', 'chanel', 'Beauty'),
    ('Penguin', 'penguin', 'Books'),
    ('HarperCollins', 'harpercollins', 'Books'),
    ('Lego', 'lego', 'Toys'),
    ('Fisher-Price', 'fisher-price', 'Toys'),
]


# ============================================================
# PRODUCT DATA
# ============================================================
PRODUCTS = [
    # ============ ELECTRONICS - SMARTPHONES (8) ============
    {'name': 'Apple iPhone 15 Pro Max', 'cat': 'smartphones', 'brand': 'apple', 'img': 'smartphone', 'price': 159900, 'mrp': 179900, 'featured': True, 'bestseller': True, 'desc': 'Titanium design with A17 Pro chip, 48MP camera system, and all-day battery life.'},
    {'name': 'Samsung Galaxy S24 Ultra', 'cat': 'smartphones', 'brand': 'samsung', 'img': 'smartphone', 'price': 129999, 'mrp': 144999, 'featured': True, 'bestseller': True, 'desc': '200MP camera with S Pen, Snapdragon 8 Gen 3, and Galaxy AI features.'},
    {'name': 'Google Pixel 8 Pro', 'cat': 'smartphones', 'brand': 'apple', 'img': 'smartphone', 'price': 106999, 'mrp': 119999, 'featured': True, 'desc': 'Google Tensor G3, 50MP triple camera, and 7 years of OS updates.'},
    {'name': 'OnePlus 12 5G', 'cat': 'smartphones', 'brand': 'samsung', 'img': 'smartphone', 'price': 64999, 'mrp': 69999, 'desc': 'Snapdragon 8 Gen 3, 100W fast charging, Hasselblad camera.'},
    {'name': 'Xiaomi 14 Ultra', 'cat': 'smartphones', 'brand': 'samsung', 'img': 'smartphone', 'price': 99999, 'mrp': 109999, 'desc': 'Leica quad camera, Snapdragon 8 Gen 3, WQHD+ AMOLED display.'},
    {'name': 'Nothing Phone (2a)', 'cat': 'smartphones', 'brand': 'samsung', 'img': 'smartphone', 'price': 25999, 'mrp': 29999, 'desc': 'Glyph Interface, Dimensity 7200 Pro, and clean Nothing OS.'},
    {'name': 'iPhone 14 Pro', 'cat': 'smartphones', 'brand': 'apple', 'img': 'smartphone', 'price': 119900, 'mrp': 129900, 'desc': 'A16 Bionic, Dynamic Island, always-on display, 48MP camera.'},
    {'name': 'Vivo X100 Pro', 'cat': 'smartphones', 'brand': 'samsung', 'img': 'smartphone', 'price': 89999, 'mrp': 99999, 'desc': 'ZEISS camera system, Dimensity 9300, 100W fast charging.'},

    # ============ ELECTRONICS - LAPTOPS (6) ============
    {'name': 'MacBook Pro 16" M3 Max', 'cat': 'laptops', 'brand': 'apple', 'img': 'laptop', 'price': 349900, 'mrp': 399900, 'featured': True, 'bestseller': True, 'desc': 'M3 Max chip with 16-core CPU, 40-core GPU, and up to 128GB unified memory.'},
    {'name': 'Dell XPS 15', 'cat': 'laptops', 'brand': 'dell', 'img': 'laptop', 'price': 199990, 'mrp': 224990, 'featured': True, 'desc': '13th Gen Intel Core i9, NVIDIA RTX 4070, 3.5K OLED display.'},
    {'name': 'HP Spectre x360', 'cat': 'laptops', 'brand': 'hp', 'img': 'laptop', 'price': 179990, 'mrp': 199990, 'desc': '2-in-1 convertible with Intel Evo platform and OLED touchscreen.'},
    {'name': 'Lenovo ThinkPad X1 Carbon', 'cat': 'laptops', 'brand': 'lenovo', 'img': 'laptop', 'price': 189990, 'mrp': 214990, 'desc': 'Ultralight business laptop with military-grade durability.'},
    {'name': 'Asus ROG Zephyrus G16', 'cat': 'laptops', 'brand': 'asus', 'img': 'gaming', 'price': 219990, 'mrp': 249990, 'bestseller': True, 'desc': 'Intel Core i9, RTX 4090, 240Hz OLED gaming display.'},
    {'name': 'MacBook Air 15" M3', 'cat': 'laptops', 'brand': 'apple', 'img': 'laptop', 'price': 134900, 'mrp': 149900, 'desc': 'M3 chip, 15.3" Liquid Retina display, up to 18 hours battery life.'},

    # ============ ELECTRONICS - AUDIO (7) ============
    {'name': 'Sony WH-1000XM5', 'cat': 'audio', 'brand': 'sony', 'img': 'headphone', 'price': 29990, 'mrp': 34990, 'featured': True, 'bestseller': True, 'desc': 'Industry-leading noise cancellation with 30-hour battery life.'},
    {'name': 'Bose QuietComfort Ultra', 'cat': 'audio', 'brand': 'bose', 'img': 'headphone', 'price': 39900, 'mrp': 44900, 'featured': True, 'desc': 'Immersive spatial audio with world-class noise cancellation.'},
    {'name': 'AirPods Pro 2nd Gen', 'cat': 'audio', 'brand': 'apple', 'img': 'headphone', 'price': 24900, 'mrp': 26900, 'bestseller': True, 'desc': 'Adaptive Audio, USB-C, up to 2x more noise cancellation.'},
    {'name': 'JBL Flip 6', 'cat': 'audio', 'brand': 'jbl', 'img': 'speaker', 'price': 9999, 'mrp': 12999, 'desc': 'Portable Bluetooth speaker with IP67 waterproof and 12-hour playtime.'},
    {'name': 'Sennheiser Momentum 4', 'cat': 'audio', 'brand': 'sony', 'img': 'headphone', 'price': 34990, 'mrp': 39990, 'desc': 'Audiophile sound with adaptive noise cancellation and 60-hour battery.'},
    {'name': 'Marshall Emberton II', 'cat': 'audio', 'brand': 'jbl', 'img': 'speaker', 'price': 14999, 'mrp': 17999, 'desc': 'Iconic Marshall design with True Stereophonic sound.'},
    {'name': 'Sonos Era 300', 'cat': 'audio', 'brand': 'sony', 'img': 'speaker', 'price': 49999, 'mrp': 54999, 'desc': 'Spatial audio smart speaker with Dolby Atmos support.'},

    # ============ ELECTRONICS - CAMERAS (5) ============
    {'name': 'Canon EOS R5', 'cat': 'cameras', 'brand': 'canon', 'img': 'camera', 'price': 289990, 'mrp': 319990, 'featured': True, 'desc': '45MP full-frame mirrorless with 8K video and dual card slots.'},
    {'name': 'Sony Alpha A7 IV', 'cat': 'cameras', 'brand': 'sony', 'img': 'camera', 'price': 249990, 'mrp': 279990, 'featured': True, 'bestseller': True, 'desc': '33MP full-frame with real-time Eye AF and 4K 60p video.'},
    {'name': 'Nikon Z8', 'cat': 'cameras', 'brand': 'nikon', 'img': 'camera', 'price': 349990, 'mrp': 399990, 'desc': '45.7MP FX-format mirrorless with 8K video and advanced AF.'},
    {'name': 'Fujifilm X-T5', 'cat': 'cameras', 'brand': 'canon', 'img': 'camera', 'price': 169990, 'mrp': 189990, 'desc': '40MP APS-C sensor with classic dial controls and film simulations.'},
    {'name': 'Canon EOS R50', 'cat': 'cameras', 'brand': 'canon', 'img': 'camera', 'price': 74990, 'mrp': 84990, 'desc': 'Compact mirrorless ideal for creators and vloggers.'},

    # ============ ELECTRONICS - WEARABLES (6) ============
    {'name': 'Apple Watch Ultra 2', 'cat': 'wearables', 'brand': 'apple', 'img': 'smartwatch', 'price': 89900, 'mrp': 99900, 'featured': True, 'bestseller': True, 'desc': 'Titanium case, 3000 nits display, 72-hour battery, and precision GPS.'},
    {'name': 'Samsung Galaxy Watch 6 Classic', 'cat': 'wearables', 'brand': 'samsung', 'img': 'smartwatch', 'price': 36999, 'mrp': 42999, 'desc': 'Rotating bezel, sleep coaching, and advanced health monitoring.'},
    {'name': 'Garmin Fenix 7X Pro', 'cat': 'wearables', 'brand': 'samsung', 'img': 'smartwatch', 'price': 89990, 'mrp': 99990, 'desc': 'Multisport GPS watch with solar charging and topo maps.'},
    {'name': 'Apple Watch Series 9', 'cat': 'wearables', 'brand': 'apple', 'img': 'smartwatch', 'price': 41900, 'mrp': 45900, 'bestseller': True, 'desc': 'S9 chip with double-tap gesture and 2000 nits display.'},
    {'name': 'Fitbit Charge 6', 'cat': 'wearables', 'brand': 'samsung', 'img': 'smartwatch', 'price': 14999, 'mrp': 17999, 'desc': 'Fitness tracker with built-in GPS and heart rate monitoring.'},
    {'name': 'Titan Smart Pro', 'cat': 'wearables', 'brand': 'titan', 'img': 'smartwatch', 'price': 9999, 'mrp': 12999, 'desc': 'Elegant smartwatch with AMOLED display and 7-day battery.'},

    # ============ ELECTRONICS - GAMING (5) ============
    {'name': 'PlayStation 5 Slim', 'cat': 'gaming', 'brand': 'sony', 'img': 'gaming', 'price': 54990, 'mrp': 59990, 'featured': True, 'bestseller': True, 'desc': 'Next-gen gaming with 1TB SSD and 4K 120Hz support.'},
    {'name': 'Xbox Series X', 'cat': 'gaming', 'brand': 'sony', 'img': 'gaming', 'price': 49990, 'mrp': 54990, 'featured': True, 'desc': 'Most powerful Xbox with 4K gaming and 1TB custom SSD.'},
    {'name': 'Nintendo Switch OLED', 'cat': 'gaming', 'brand': 'sony', 'img': 'gaming', 'price': 32999, 'mrp': 36999, 'desc': '7-inch OLED screen with enhanced audio and 64GB storage.'},
    {'name': 'ASUS ROG Ally', 'cat': 'gaming', 'brand': 'asus', 'img': 'gaming', 'price': 69990, 'mrp': 74990, 'desc': 'Handheld gaming PC with AMD Ryzen Z1 Extreme.'},
    {'name': 'Steam Deck OLED', 'cat': 'gaming', 'brand': 'asus', 'img': 'gaming', 'price': 54990, 'mrp': 59990, 'desc': 'Handheld PC gaming with vibrant HDR OLED display.'},

    # ============ ELECTRONICS - DRONES (3) ============
    {'name': 'DJI Mavic 3 Pro', 'cat': 'drones', 'brand': 'samsung', 'img': 'drone', 'price': 199990, 'mrp': 219990, 'featured': True, 'desc': 'Triple-camera system with 4/3 CMOS Hasselblad sensor.'},
    {'name': 'DJI Air 3', 'cat': 'drones', 'brand': 'samsung', 'img': 'drone', 'price': 99990, 'mrp': 109990, 'desc': 'Dual primary cameras with 46-minute flight time.'},
    {'name': 'DJI Mini 4 Pro', 'cat': 'drones', 'brand': 'samsung', 'img': 'drone', 'price': 79990, 'mrp': 89990, 'bestseller': True, 'desc': 'Ultra-light drone under 249g with 4K HDR video.'},

    # ============ FASHION - MEN (6) ============
    {'name': 'Premium Italian Linen Shirt', 'cat': 'mens-fashion', 'brand': 'zara', 'img': 'mens_shirt', 'price': 4999, 'mrp': 7999, 'featured': True, 'desc': 'Handcrafted linen shirt with mother-of-pearl buttons.'},
    {'name': 'Charcoal Wool Blend Suit', 'cat': 'mens-fashion', 'brand': 'gucci', 'img': 'mens_suit', 'price': 45999, 'mrp': 59999, 'featured': True, 'bestseller': True, 'desc': 'Tailored fit suit in premium Italian wool blend.'},
    {'name': 'Classic Oxford Cotton Shirt', 'cat': 'mens-fashion', 'brand': 'levis', 'img': 'mens_shirt', 'price': 2499, 'mrp': 3999, 'desc': 'Timeless Oxford shirt in breathable cotton.'},
    {'name': 'Cashmere Crew Neck Sweater', 'cat': 'mens-fashion', 'brand': 'zara', 'img': 'mens_shirt', 'price': 8999, 'mrp': 12999, 'desc': '100% pure cashmere sweater with ribbed trim.'},
    {'name': 'Slim Fit Denim Jeans', 'cat': 'mens-fashion', 'brand': 'levis', 'img': 'mens_shirt', 'price': 3499, 'mrp': 4999, 'bestseller': True, 'desc': 'Premium stretch denim with classic 5-pocket styling.'},
    {'name': 'Merino Wool Blazer', 'cat': 'mens-fashion', 'brand': 'gucci', 'img': 'mens_suit', 'price': 24999, 'mrp': 34999, 'desc': 'Half-canvas construction merino wool blazer.'},

    # ============ FASHION - WOMEN (6) ============
    {'name': 'Silk Evening Gown', 'cat': 'womens-fashion', 'brand': 'gucci', 'img': 'womens_dress', 'price': 34999, 'mrp': 45999, 'featured': True, 'desc': 'Floor-length silk gown with hand-embroidered details.'},
    {'name': 'Floral Midi Wrap Dress', 'cat': 'womens-fashion', 'brand': 'zara', 'img': 'womens_dress', 'price': 3999, 'mrp': 5999, 'featured': True, 'bestseller': True, 'desc': 'Flowing wrap dress in soft floral print.'},
    {'name': 'Designer Trench Coat', 'cat': 'womens-fashion', 'brand': 'zara', 'img': 'womens_dress', 'price': 12999, 'mrp': 17999, 'desc': 'Classic double-breasted trench coat in water-resistant fabric.'},
    {'name': 'Cashmere Wrap Cardigan', 'cat': 'womens-fashion', 'brand': 'hm', 'img': 'womens_dress', 'price': 7999, 'mrp': 10999, 'desc': 'Luxuriously soft cashmere cardigan with belt tie.'},
    {'name': 'Boho Maxi Dress', 'cat': 'womens-fashion', 'brand': 'hm', 'img': 'womens_dress', 'price': 2999, 'mrp': 4499, 'desc': 'Free-spirited maxi dress with tiered skirt.'},
    {'name': 'Velvet Cocktail Dress', 'cat': 'womens-fashion', 'brand': 'gucci', 'img': 'womens_dress', 'price': 15999, 'mrp': 21999, 'bestseller': True, 'desc': 'Elegant velvet dress with sweetheart neckline.'},

    # ============ FASHION - HANDBAGS (4) ============
    {'name': 'Italian Leather Tote Bag', 'cat': 'accessories', 'brand': 'gucci', 'img': 'womens_handbag', 'price': 45999, 'mrp': 55999, 'featured': True, 'bestseller': True, 'desc': 'Full-grain Italian leather tote with suede lining.'},
    {'name': 'Quilted Chain Shoulder Bag', 'cat': 'accessories', 'brand': 'gucci', 'img': 'womens_handbag', 'price': 89990, 'mrp': 109990, 'featured': True, 'desc': 'Iconic quilted leather with gold chain strap.'},
    {'name': 'Mini Crossbody Bag', 'cat': 'accessories', 'brand': 'zara', 'img': 'womens_handbag', 'price': 4999, 'mrp': 7999, 'desc': 'Compact crossbody in textured faux leather.'},
    {'name': 'Woven Leather Hobo Bag', 'cat': 'accessories', 'brand': 'hm', 'img': 'womens_handbag', 'price': 8999, 'mrp': 12999, 'desc': 'Slouchy woven leather hobo bag.'},

    # ============ FASHION - SHOES (6) ============
    {'name': 'Nike Air Max 270', 'cat': 'footwear', 'brand': 'nike', 'img': 'shoes', 'price': 12999, 'mrp': 16999, 'featured': True, 'bestseller': True, 'desc': 'Max Air unit for all-day comfort and street-ready style.'},
    {'name': 'Adidas Ultraboost 22', 'cat': 'footwear', 'brand': 'adidas', 'img': 'shoes', 'price': 17999, 'mrp': 21999, 'featured': True, 'desc': 'Responsive Boost midsole with Primeknit+ upper.'},
    {'name': 'Puma RS-X Sneakers', 'cat': 'footwear', 'brand': 'puma', 'img': 'shoes', 'price': 8999, 'mrp': 11999, 'desc': 'Retro-inspired chunky sneaker with bold colorways.'},
    {'name': 'Gucci Leather Loafers', 'cat': 'footwear', 'brand': 'gucci', 'img': 'shoes', 'price': 64990, 'mrp': 79990, 'bestseller': True, 'desc': 'Classic horsebit leather loafers handmade in Italy.'},
    {'name': 'Nike Dunk Low Retro', 'cat': 'footwear', 'brand': 'nike', 'img': 'shoes', 'price': 9999, 'mrp': 12999, 'bestseller': True, 'desc': 'Iconic basketball silhouette with premium leather.'},
    {'name': 'Adidas Stan Smith', 'cat': 'footwear', 'brand': 'adidas', 'img': 'shoes', 'price': 7999, 'mrp': 9999, 'desc': 'Timeless tennis-inspired sneaker in premium leather.'},

    # ============ FASHION - SUNGLASSES (4) ============
    {'name': 'Ray-Ban Aviator Classic', 'cat': 'accessories', 'brand': 'rayban', 'img': 'sunglasses', 'price': 9990, 'mrp': 12990, 'featured': True, 'bestseller': True, 'desc': 'Iconic aviator with G-15 polarized lenses.'},
    {'name': 'Ray-Ban Wayfarer', 'cat': 'accessories', 'brand': 'rayban', 'img': 'sunglasses', 'price': 8990, 'mrp': 11990, 'bestseller': True, 'desc': 'Timeless acetate frame with crystal lenses.'},
    {'name': 'Gucci Oversized Square', 'cat': 'accessories', 'brand': 'gucci', 'img': 'sunglasses', 'price': 34990, 'mrp': 42990, 'desc': 'Oversized square frame with GG logo temples.'},
    {'name': 'Prada Cat-Eye Sunglasses', 'cat': 'accessories', 'brand': 'gucci', 'img': 'sunglasses', 'price': 28990, 'mrp': 35990, 'desc': 'Elegant cat-eye frame with gradient lenses.'},

    # ============ FASHION - WATCHES (5) ============
    {'name': 'Titan Neo Analog Watch', 'cat': 'accessories', 'brand': 'titan', 'img': 'watches', 'price': 5999, 'mrp': 7999, 'featured': True, 'desc': 'Classic analog watch with sapphire crystal glass.'},
    {'name': 'Titan Raga Women\'s Watch', 'cat': 'accessories', 'brand': 'titan', 'img': 'watches', 'price': 8999, 'mrp': 11999, 'bestseller': True, 'desc': 'Elegant women\'s watch with rose gold finish.'},
    {'name': 'Titan Edge Ultra Slim', 'cat': 'accessories', 'brand': 'titan', 'img': 'watches', 'price': 12999, 'mrp': 16999, 'featured': True, 'desc': 'One of the world\'s slimmest watches at 3.6mm.'},
    {'name': 'Titan Automatics', 'cat': 'accessories', 'brand': 'titan', 'img': 'watches', 'price': 24999, 'mrp': 29999, 'desc': 'Self-winding automatic movement with exhibition caseback.'},
    {'name': 'Titan Maritime Chronograph', 'cat': 'accessories', 'brand': 'titan', 'img': 'watches', 'price': 18999, 'mrp': 22999, 'desc': 'Sporty chronograph with 100m water resistance.'},

    # ============ FASHION - JEWELRY (4) ============
    {'name': 'Diamond Solitaire Ring', 'cat': 'jewelry', 'brand': 'titan', 'img': 'jewelry', 'price': 89990, 'mrp': 109990, 'featured': True, 'bestseller': True, 'desc': 'Certified 0.5 carat diamond in 18K white gold.'},
    {'name': 'Pearl Drop Earrings', 'cat': 'jewelry', 'brand': 'titan', 'img': 'jewelry', 'price': 15999, 'mrp': 19999, 'desc': 'South Sea pearls with diamond accents.'},
    {'name': 'Gold Tennis Bracelet', 'cat': 'jewelry', 'brand': 'titan', 'img': 'jewelry', 'price': 45999, 'mrp': 55999, 'featured': True, 'desc': '18K gold tennis bracelet with brilliant-cut diamonds.'},
    {'name': 'Emerald Pendant Necklace', 'cat': 'jewelry', 'brand': 'titan', 'img': 'jewelry', 'price': 34999, 'mrp': 42999, 'desc': 'Colombian emerald pendant with diamond halo.'},

    # ============ HOME & LIVING - FURNITURE (4) ============
    {'name': 'Velvet Chesterfield Sofa', 'cat': 'furniture', 'brand': 'urban-ladder', 'img': 'sofa', 'price': 89990, 'mrp': 109990, 'featured': True, 'bestseller': True, 'desc': 'Hand-tufted velvet sofa with solid wood frame.'},
    {'name': 'Scandinavian 3-Seater Sofa', 'cat': 'furniture', 'brand': 'ikea', 'img': 'sofa', 'price': 49990, 'mrp': 59990, 'featured': True, 'desc': 'Minimalist linen sofa with clean lines.'},
    {'name': 'King Size Platform Bed', 'cat': 'furniture', 'brand': 'urban-ladder', 'img': 'bed', 'price': 69990, 'mrp': 84990, 'featured': True, 'desc': 'Solid oak platform bed with upholstered headboard.'},
    {'name': 'Queen Storage Bed', 'cat': 'furniture', 'brand': 'ikea', 'img': 'bed', 'price': 45990, 'mrp': 55990, 'desc': 'Bed with built-in storage drawers and hydraulic lift.'},

    # ============ HOME & LIVING - LIGHTING (4) ============
    {'name': 'Modern Arc Floor Lamp', 'cat': 'lighting', 'brand': 'philips', 'img': 'lamp', 'price': 12999, 'mrp': 16999, 'featured': True, 'desc': 'Contemporary arc lamp with marble base and brass finish.'},
    {'name': 'Crystal Chandelier', 'cat': 'lighting', 'brand': 'philips', 'img': 'lamp', 'price': 34999, 'mrp': 42999, 'featured': True, 'bestseller': True, 'desc': 'Stunning crystal chandelier with 12 lights.'},
    {'name': 'Smart LED Table Lamp', 'cat': 'lighting', 'brand': 'philips', 'img': 'lamp', 'price': 4999, 'mrp': 6999, 'desc': 'Wi-Fi enabled with adjustable color temperature.'},
    {'name': 'Vintage Brass Pendant', 'cat': 'lighting', 'brand': 'philips', 'img': 'lamp', 'price': 8999, 'mrp': 11999, 'desc': 'Industrial-style brass pendant light.'},

    # ============ HOME & LIVING - KITCHEN (4) ============
    {'name': 'Prestige Smart Kitchen Set', 'cat': 'kitchenware', 'brand': 'prestige', 'img': 'kitchen', 'price': 15999, 'mrp': 19999, 'featured': True, 'desc': 'Premium 15-piece cookware set with non-stick coating.'},
    {'name': 'Philips Air Fryer XXL', 'cat': 'kitchenware', 'brand': 'philips', 'img': 'kitchen', 'price': 14999, 'mrp': 18999, 'bestseller': True, 'desc': 'Rapid Air technology with 90% less oil.'},
    {'name': 'Italian Espresso Machine', 'cat': 'kitchenware', 'brand': 'philips', 'img': 'kitchen', 'price': 45999, 'mrp': 55999, 'featured': True, 'desc': 'Professional-grade espresso maker with milk frother.'},
    {'name': 'Cast Iron Dutch Oven', 'cat': 'kitchenware', 'brand': 'prestige', 'img': 'kitchen', 'price': 8999, 'mrp': 11999, 'desc': 'Enameled cast iron Dutch oven for slow cooking.'},

    # ============ HOME & LIVING - DECOR (4) ============
    {'name': 'Handwoven Persian Rug', 'cat': 'home-decor', 'brand': 'urban-ladder', 'img': 'rugs', 'price': 24999, 'mrp': 29999, 'featured': True, 'desc': 'Hand-knotted Persian rug in silk and wool.'},
    {'name': 'Marble Coffee Table', 'cat': 'home-decor', 'brand': 'urban-ladder', 'img': 'decor', 'price': 34999, 'mrp': 42999, 'featured': True, 'bestseller': True, 'desc': 'Italian Carrara marble top with brass base.'},
    {'name': 'Art Deco Vase Set', 'cat': 'home-decor', 'brand': 'ikea', 'img': 'decor', 'price': 4999, 'mrp': 6999, 'desc': 'Set of 3 ceramic vases in matte finish.'},
    {'name': 'Abstract Wall Art', 'cat': 'home-decor', 'brand': 'urban-ladder', 'img': 'decor', 'price': 12999, 'mrp': 16999, 'desc': 'Framed abstract canvas painting for modern interiors.'},

    # ============ BEAUTY - SKINCARE (5) ============
    {'name': 'Forest Essentials Night Cream', 'cat': 'skincare', 'brand': 'forest-essentials', 'img': 'skincare', 'price': 2999, 'mrp': 3499, 'featured': True, 'bestseller': True, 'desc': 'Ayurvedic night cream with saffron and sweet lime.'},
    {'name': 'Vitamin C Brightening Serum', 'cat': 'skincare', 'brand': 'loreal', 'img': 'skincare', 'price': 1999, 'mrp': 2499, 'featured': True, 'desc': '20% Vitamin C serum with hyaluronic acid.'},
    {'name': 'Hydrating Face Moisturizer', 'cat': 'skincare', 'brand': 'nivea', 'img': 'skincare', 'price': 899, 'mrp': 1199, 'bestseller': True, 'desc': '48-hour hydration with hyaluronic acid and vitamin E.'},
    {'name': 'Retinol Anti-Aging Cream', 'cat': 'skincare', 'brand': 'loreal', 'img': 'skincare', 'price': 2499, 'mrp': 2999, 'desc': 'Advanced retinol formula to reduce fine lines.'},
    {'name': 'Luxury Rose Face Oil', 'cat': 'skincare', 'brand': 'forest-essentials', 'img': 'skincare', 'price': 1899, 'mrp': 2499, 'desc': 'Pure rose oil for radiant, hydrated skin.'},

    # ============ BEAUTY - MAKEUP (5) ============
    {'name': 'Dior Iconic Lipstick', 'cat': 'makeup', 'brand': 'dior', 'img': 'makeup', 'price': 3499, 'mrp': 3999, 'featured': True, 'bestseller': True, 'desc': 'Iconic long-wear lipstick in legendary red shade.'},
    {'name': 'Maybelline Mascara Set', 'cat': 'makeup', 'brand': 'maybelline', 'img': 'makeup', 'price': 899, 'mrp': 1199, 'bestseller': True, 'desc': 'Volumizing mascara for dramatic lashes.'},
    {'name': 'MAC Eyeshadow Palette', 'cat': 'makeup', 'brand': 'loreal', 'img': 'makeup', 'price': 4499, 'mrp': 5499, 'desc': '12-shade palette with matte and shimmer finishes.'},
    {'name': 'Liquid Foundation SPF 30', 'cat': 'makeup', 'brand': 'loreal', 'img': 'makeup', 'price': 1499, 'mrp': 1899, 'desc': 'Full coverage foundation with SPF 30 protection.'},
    {'name': 'Chanel Nail Polish', 'cat': 'makeup', 'brand': 'chanel', 'img': 'makeup', 'price': 2499, 'mrp': 2999, 'featured': True, 'desc': 'Long-wear nail polish in signature Chanel shades.'},

    # ============ BEAUTY - FRAGRANCE (5) ============
    {'name': 'Chanel No. 5 Perfume', 'cat': 'fragrance', 'brand': 'chanel', 'img': 'fragrance', 'price': 12999, 'mrp': 15999, 'featured': True, 'bestseller': True, 'desc': 'Iconic floral bouquet fragrance for women.'},
    {'name': 'Dior Sauvage Eau de Parfum', 'cat': 'fragrance', 'brand': 'dior', 'img': 'fragrance', 'price': 10999, 'mrp': 12999, 'featured': True, 'bestseller': True, 'desc': 'Fresh, spicy fragrance with bergamot and pepper.'},
    {'name': 'Bleu de Chanel Parfum', 'cat': 'fragrance', 'brand': 'chanel', 'img': 'fragrance', 'price': 11999, 'mrp': 14999, 'desc': 'Woody aromatic fragrance for the modern man.'},
    {'name': 'Luxury Oud Perfume Oil', 'cat': 'fragrance', 'brand': 'dior', 'img': 'fragrance', 'price': 8999, 'mrp': 10999, 'desc': 'Pure oud oil with notes of rose and amber.'},
    {'name': 'Rose Garden Eau de Toilette', 'cat': 'fragrance', 'brand': 'loreal', 'img': 'fragrance', 'price': 4999, 'mrp': 6499, 'desc': 'Delicate rose fragrance with peony and white musk.'},

    # ============ BEAUTY - HAIRCARE (4) ============
    {'name': 'Luxury Hair Spa Kit', 'cat': 'haircare', 'brand': 'loreal', 'img': 'haircare', 'price': 3499, 'mrp': 4499, 'featured': True, 'desc': 'Complete hair spa kit with shampoo, mask and serum.'},
    {'name': 'Argan Oil Hair Serum', 'cat': 'haircare', 'brand': 'loreal', 'img': 'haircare', 'price': 999, 'mrp': 1299, 'bestseller': True, 'desc': 'Pure Moroccan argan oil for silky smooth hair.'},
    {'name': 'Keratin Repair Shampoo', 'cat': 'haircare', 'brand': 'loreal', 'img': 'haircare', 'price': 1299, 'mrp': 1699, 'desc': 'Professional keratin treatment shampoo.'},
    {'name': 'Ayurvedic Hair Oil', 'cat': 'haircare', 'brand': 'forest-essentials', 'img': 'haircare', 'price': 799, 'mrp': 999, 'desc': 'Traditional Ayurvedic blend for strong, healthy hair.'},

    # ============ SPORTS (5) ============
    {'name': 'Nike Pro Training Kit', 'cat': 'sports', 'brand': 'nike', 'img': 'sports', 'price': 5999, 'mrp': 7999, 'featured': True, 'desc': 'Complete training kit with dri-fit technology.'},
    {'name': 'Adidas Yoga Mat Premium', 'cat': 'sports', 'brand': 'adidas', 'img': 'sports', 'price': 2999, 'mrp': 3999, 'bestseller': True, 'desc': 'Extra thick yoga mat with superior grip.'},
    {'name': 'Puma Running Shoes Pro', 'cat': 'sports', 'brand': 'puma', 'img': 'sports', 'price': 8999, 'mrp': 11999, 'desc': 'Lightweight running shoes with responsive cushioning.'},
    {'name': 'Adjustable Dumbbell Set', 'cat': 'sports', 'brand': 'nike', 'img': 'sports', 'price': 14999, 'mrp': 18999, 'desc': '20kg adjustable dumbbell set for home gym.'},
    {'name': 'Premium Cricket Bat', 'cat': 'sports', 'brand': 'adidas', 'img': 'sports', 'price': 12999, 'mrp': 15999, 'featured': True, 'desc': 'English willow cricket bat for professional play.'},

    # ============ BOOKS (4) ============
    {'name': 'The Art of War', 'cat': 'books', 'brand': 'penguin', 'img': 'books', 'price': 399, 'mrp': 599, 'bestseller': True, 'desc': 'Sun Tzu\'s timeless treatise on strategy and leadership.'},
    {'name': 'Atomic Habits', 'cat': 'books', 'brand': 'penguin', 'img': 'books', 'price': 599, 'mrp': 799, 'featured': True, 'bestseller': True, 'desc': 'James Clear\'s guide to building good habits.'},
    {'name': 'The Alchemist', 'cat': 'books', 'brand': 'harpercollins', 'img': 'books', 'price': 349, 'mrp': 499, 'desc': 'Paulo Coelho\'s philosophical novel about following dreams.'},
    {'name': 'Sapiens: A Brief History', 'cat': 'books', 'brand': 'harpercollins', 'img': 'books', 'price': 699, 'mrp': 899, 'featured': True, 'desc': 'Yuval Noah Harari\'s history of humankind.'},

    # ============ TOYS (3) ============
    {'name': 'LEGO Creator Expert Set', 'cat': 'toys', 'brand': 'lego', 'img': 'toys', 'price': 19999, 'mrp': 24999, 'featured': True, 'bestseller': True, 'desc': 'Advanced LEGO building set for collectors.'},
    {'name': 'Fisher-Price Learning Toy', 'cat': 'toys', 'brand': 'fisher-price', 'img': 'toys', 'price': 2999, 'mrp': 3999, 'desc': 'Educational toy for toddlers with sounds and lights.'},
    {'name': 'LEGO Technic Supercar', 'cat': 'toys', 'brand': 'lego', 'img': 'toys', 'price': 29999, 'mrp': 35999, 'featured': True, 'desc': 'Detailed LEGO Technic supercar model kit.'},
]


# ============================================================
# MAIN SEEDING FUNCTION
# ============================================================
def main():
    print("=" * 60)
    print("🚀 BharatKart Product Seeding")
    print("=" * 60)

    # ---- 1. Create/get a seller ----
    seller_user, created = User.objects.get_or_create(
        email='seller@bharatkart.com',
        defaults={
            'username': 'bharatkart_seller',
            'first_name': 'Rajesh',
            'last_name': 'Kumar',
            'role': 'seller',
            'is_active': True,
        }
    )
    if created:
        seller_user.set_password('seller@123')
        seller_user.save()
        print(f"✅ Created seller user: {seller_user.email}")

    seller, created = SellerProfile.objects.get_or_create(
        user=seller_user,
        defaults={
            'store_name': 'BharatKart Official Store',
            'store_description': 'Premium products from India\'s finest brands',
            'gst_number': 'GSTIN123456789',
            'pan_number': 'ABCDE1234F',
            'is_verified': True,
        }
    )
    if created:
        print(f"✅ Created seller profile: {seller.store_name}")

    # ---- 2. Create categories ----
    print("\n📁 Creating categories...")
    cat_map = {}
    for name, slug, parent_slug, description in CATEGORIES:
        parent = cat_map.get(parent_slug) if parent_slug else None
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description,
                'parent': parent,
                'is_active': True,
            }
        )
        cat_map[slug] = category
        if created:
            print(f"  ✅ {name}")

    # ---- 3. Create brands ----
    print("\n🏷️  Creating brands...")
    brand_map = {}
    for name, slug, _ in BRANDS:
        brand, created = Brand.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'is_active': True}
        )
        brand_map[slug] = brand
        if created:
            print(f"  ✅ {name}")

    # ---- 4. Create products ----
    print(f"\n📦 Creating products ({len(PRODUCTS)} total)...")
    created_count = 0
    updated_count = 0

    for i, p in enumerate(PRODUCTS, 1):
        try:
            category = cat_map.get(p['cat'])
            brand = brand_map.get(p['brand'])

            if not category:
                print(f"  ⚠️  Skipping {p['name']} — category '{p['cat']}' not found")
                continue

            # Get image URL
            img_key = p.get('img', 'smartphone')
            img_list = IMAGE_LIBRARY.get(img_key, IMAGE_LIBRARY['smartphone'])
            main_image_url = unsplash_img(random.choice(img_list))

            # Create/get product
            product, created = Product.objects.update_or_create(
                slug=slugify(p['name']),
                defaults={
                    'name': p['name'],
                    'category': category,
                    'brand': brand,
                    'description': p['desc'],
                    'short_description': p['desc'][:200],
                    'price': Decimal(str(p['price'])),
                    'mrp': Decimal(str(p['mrp'])),
                    'stock': random.randint(10, 100),
                    'is_active': True,
                    'is_featured': p.get('featured', False),
                    'is_bestseller': p.get('bestseller', False),
                    'gst_rate': '18',
                    'average_rating': Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                    'total_ratings': random.randint(10, 500),
                }
            )

            # Skip if we've already added images (avoid duplicates on re-run)
            if not created and product.images.exists():
                updated_count += 1
                continue

            # Create image records using URL (stored as text in a custom field or download)
            # Since we use ImageField, we store the URL in a special way
            # For simplicity, we use Django's ImageField with a URL download

            # Alternative: Store URL as a remote image
            for img_idx, alt_key in enumerate([img_key, img_key, img_key]):
                img_id = random.choice(IMAGE_LIBRARY.get(alt_key, IMAGE_LIBRARY['smartphone']))
                url = unsplash_img(img_id)

                ProductImage.objects.create(
                    product=product,
                    image=url if isinstance(url, str) else url,  # URL will be stored as text path
                    alt_text=product.name,
                    is_main=(img_idx == 0)
                )

            created_count += 1
            if i % 20 == 0:
                print(f"  ✅ Created {i} products...")

        except Exception as e:
            print(f"  ❌ Error creating {p['name']}: {e}")

    print("\n" + "=" * 60)
    print(f"✅ SEEDING COMPLETE!")
    print(f"   Categories: {len(cat_map)}")
    print(f"   Brands: {len(brand_map)}")
    print(f"   Products created: {created_count}")
    print(f"   Products updated: {updated_count}")
    print("=" * 60)
    print("\nVisit http://localhost:8000 to see your products!")
    print("\nTo test different categories:")
    print("  → http://localhost:8000/products/")
    print("  → http://localhost:8000/products/?category=electronics")
    print("  → http://localhost:8000/products/?category=fashion")
    print("  → http://localhost:8000/products/?category=home-kitchen")
    print("  → http://localhost:8000/products/?category=beauty")
    print("  → http://localhost:8000/products/?sort=discount  (Luxury Sale)")


if __name__ == '__main__':
    main()