"""
BharatKart - Add Images to All Products
Run: python scripts/add_product_images.py
"""

import os
import sys
import django
from pathlib import Path
import random

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from apps.products.models import Product, ProductImage


# ============================================================
# IMAGE URLS BY PRODUCT TYPE
# ============================================================
# Format: {'keyword_in_product_name': ['url1', 'url2', ...]}

IMAGE_LIBRARY = {
    # SMARTPHONES
    'iphone': [

    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80',
    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80',
    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80',
],
  
    'samsung': [
        'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80',
        'https://images.unsplash.com/photo-1567581935884-3349723552ca?w=800&q=80',
        'https://images.unsplash.com/photo-1523206489230-c012c64b2b48?w=800&q=80',
    ],
    'pixel': [
        'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80',
        'https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=800&q=80',
    ],
    'oneplus': [
        'https://images.unsplash.com/photo-1567581935884-3349723552ca?w=800&q=80',
        'https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=800&q=80',
    ],
    'xiaomi': [
        'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=800&q=80',
        'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&q=80',
    ],
    'nothing': [
        'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&q=80',
    ],
    'vivo': [
        'https://images.unsplash.com/photo-1567581935884-3349723552ca?w=800&q=80',
    ],
    'phone': [
        'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80',
    ],
    
    # LAPTOPS
    'macbook': [
        'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80',
        'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&q=80',
    ],
    'dell': [
        'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80',
    ],
    'hp': [
        'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&q=80',
    ],
    'lenovo': [
        'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&q=80',
    ],
    'asus': [
        'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&q=80',
    ],
    'laptop': [
        'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80',
    ],
    
    # AUDIO
    'headphone': [
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
        'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80',
    ],
    'airpods': [
        'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&q=80',
    ],
    'bose': [
        'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80',
    ],
    'sony': [
        'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80',
    ],
    'jbl': [
        'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&q=80',
    ],
    'speaker': [
        'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&q=80',
    ],
    
    # CAMERAS
    'canon': [
        'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&q=80',
    ],
    'nikon': [
        'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80',
    ],
    'camera': [
        'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&q=80',
    ],
    
    # WEARABLES
    'watch': [
        'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&q=80',
        'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80',
    ],
    'garmin': [
        'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80',
    ],
    'fitbit': [
        'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&q=80',
    ],
    
    # GAMING
    'playstation': [
        'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=800&q=80',
    ],
    'xbox': [
        'https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=800&q=80',
    ],
    'nintendo': [
        'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=800&q=80',
    ],
    'rog': [
        'https://images.unsplash.com/photo-1592840496694-26d035b52b48?w=800&q=80',
    ],
    'steam': [
        'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=800&q=80',
    ],
    
    # DRONES
    'dji': [
        'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&q=80',
    ],
    'drone': [
        'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&q=80',
    ],
    
    # FASHION - MEN
    'shirt': [
        'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&q=80',
        'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&q=80',
    ],
    'suit': [
        'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&q=80',
    ],
    'sweater': [
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
    ],
    'jeans': [
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80',
    ],
    'blazer': [
        'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80',
    ],
    
    # FASHION - WOMEN
    'gown': [
        'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&q=80',
    ],
    'dress': [
        'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&q=80',
        'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=800&q=80',
    ],
    'cardigan': [
        'https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=800&q=80',
    ],
    'maxi': [
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80',
    ],
    
    # BAGS
    'tote': [
        'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&q=80',
    ],
    'handbag': [
        'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&q=80',
    ],
    'crossbody': [
        'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800&q=80',
    ],
    'hobo': [
        'https://images.unsplash.com/photo-1591561954557-26941169b49e?w=800&q=80',
    ],
    
    # SHOES
    'nike': [
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',
    ],
    'adidas': [
        'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&q=80',
    ],
    'puma': [
        'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=800&q=80',
    ],
    'shoe': [
        'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&q=80',
    ],
    'loafer': [
        'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=800&q=80',
    ],
    
    # SUNGLASSES
    'sunglasses': [
        'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&q=80',
    ],
    'ray-ban': [
        'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&q=80',
    ],
    
    # WATCHES
    'titan': [
        'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800&q=80',
    ],
    'chronograph': [
        'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=800&q=80',
    ],
    
    # JEWELRY
    'ring': [
        'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&q=80',
    ],
    'earring': [
        'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&q=80',
    ],
    'bracelet': [
        'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&q=80',
    ],
    'pendant': [
        'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&q=80',
    ],
    
    # HOME & FURNITURE
    'sofa': [
        'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80',
    ],
    'bed': [
        'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&q=80',
    ],
    'lamp': [
        'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80',
    ],
    'chandelier': [
        'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&q=80',
    ],
    'rug': [
        'https://images.unsplash.com/photo-1600166898405-da9535204843?w=800&q=80',
    ],
    
    # KITCHEN
    'prestige': [
        'https://images.unsplash.com/photo-1556909212-d5b604d0c90d?w=800&q=80',
    ],
    'air fryer': [
        'https://images.unsplash.com/photo-1585515320310-259814833e62?w=800&q=80',
    ],
    'espresso': [
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80',
    ],
    'kitchen': [
        'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&q=80',
    ],
    
    # BEAUTY - SKINCARE
    'night cream': [
        'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800&q=80',
    ],
    'serum': [
        'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&q=80',
    ],
    'moisturizer': [
        'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800&q=80',
    ],
    'retinol': [
        'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800&q=80',
    ],
    'face oil': [
        'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800&q=80',
    ],
    
    # BEAUTY - MAKEUP
    'lipstick': [
        'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&q=80',
    ],
    'mascara': [
        'https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=800&q=80',
    ],
    'eyeshadow': [
        'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=800&q=80',
    ],
    'foundation': [
        'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&q=80',
    ],
    'nail polish': [
        'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&q=80',
    ],
    
    # BEAUTY - FRAGRANCE
    'perfume': [
        'https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80',
    ],
    'sauvage': [
        'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&q=80',
    ],
    'bleu': [
        'https://images.unsplash.com/photo-1594035910387-fea47794261f?w=800&q=80',
    ],
    'oud': [
        'https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=800&q=80',
    ],
    'fragrance': [
        'https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80',
    ],
    
    # BEAUTY - HAIRCARE
    'hair spa': [
        'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800&q=80',
    ],
    'argan': [
        'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800&q=80',
    ],
    'keratin': [
        'https://images.unsplash.com/photo-1585232004423-244e0e6904e3?w=800&q=80',
    ],
    'hair oil': [
        'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800&q=80',
    ],
    
    # SPORTS
    'training': [
        'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&q=80',
    ],
    'yoga': [
        'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80',
    ],
    'dumbbell': [
        'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80',
    ],
    'cricket': [
        'https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80',
    ],
    
    # BOOKS
    'art of war': [
        'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800&q=80',
    ],
    'atomic': [
        'https://images.unsplash.com/photo-1589998059171-988d887df646?w=800&q=80',
    ],
    'alchemist': [
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800&q=80',
    ],
    'sapiens': [
        'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800&q=80',
    ],
    'book': [
        'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=800&q=80',
    ],
    
    # TOYS
    'lego': [
        'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=800&q=80',
    ],
    'fisher': [
        'https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=800&q=80',
    ],
}


def find_image_urls(product_name):
    """Find matching image URLs for a product - most specific keyword wins"""
    name_lower = product_name.lower()
    matched_urls = []
    
    # Sort keywords by length (longest first) so specific keywords win
    sorted_keywords = sorted(IMAGE_LIBRARY.keys(), key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if keyword in name_lower:
            matched_urls.extend(IMAGE_LIBRARY[keyword])
            break  # Use first (most specific) match only
    
    if not matched_urls:
        matched_urls = ['https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80']
    
    return matched_urls[:3]


def main():
    print("=" * 60)
    print("🖼️  BharatKart - Add Product Images")
    print("=" * 60)
    
    products = Product.objects.all()
    total = products.count()
    
    if total == 0:
        print("❌ No products found. Run seed_products.py first.")
        return
    
    print(f"\n📦 Found {total} products\n")
    
    updated = 0
    skipped = 0
    
    for i, product in enumerate(products, 1):
        # Skip if product already has images
        if product.images.exists():
            skipped += 1
            if i % 20 == 0:
                print(f"  [{i}/{total}] Skipped: {product.name[:40]}")
            continue
        
        # Find image URLs for this product
        urls = find_image_urls(product.name)
        
        # Create images
        for idx, url in enumerate(urls):
            ProductImage.objects.create(
                product=product,
                image_url=url,
                alt_text=product.name,
                is_main=(idx == 0),
            )
        
        updated += 1
        if i % 10 == 0 or i == total:
            print(f"  [{i}/{total}] ✅ {product.name[:40]}")
    
    print("\n" + "=" * 60)
    print(f"✅ DONE!")
    print(f"   Images added: {updated} products")
    print(f"   Skipped (already had images): {skipped} products")
    print("=" * 60)
    print("\n🌐 Visit http://127.0.0.1:8000/products/ to see them!")


if __name__ == '__main__':
    main()