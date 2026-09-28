"""
Fix product images that were saved to the wrong field.
Run: python fix_product_images.py
"""

import os
import sys
import django
from pathlib import Path
from urllib.parse import unquote

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from apps.products.models import ProductImage


def decode_image_path(raw_path):
    """Decode a broken image path back to a URL"""
    if not raw_path:
        return None

    decoded = unquote(str(raw_path))

    # Remove /media/ prefix
    if '/media/' in decoded:
        decoded = decoded.split('/media/', 1)[1]

    # Fix missing slash: https:/ → https://
    if decoded.startswith('https:/') and not decoded.startswith('https://'):
        decoded = 'https://' + decoded[7:]
    elif decoded.startswith('http:/') and not decoded.startswith('http://'):
        decoded = 'http://' + decoded[6:]

    # Only return if it's a real URL
    if decoded.startswith(('http://', 'https://')):
        return decoded

    return None


def main():
    print("=" * 60)
    print(" Fixing Product Images")
    print("=" * 60)

    broken = ProductImage.objects.filter(image_url__isnull=True).exclude(image='')
    total = broken.count()

    print(f"\n Found {total} images in wrong field\n")

    fixed = 0
    deleted = 0

    for img in broken:
        decoded = decode_image_path(img.image)

        if decoded:
            img.image_url = decoded
            img.image = None
            img.save(update_fields=['image_url', 'image'])
            fixed += 1
            if fixed % 20 == 0:
                print(f"  [{fixed}/{total}] Fixed: {decoded[:70]}...")
        else:
            img.delete()
            deleted += 1

    print("\n" + "=" * 60)
    print(" DONE!")
    print(f"   Fixed: {fixed} images")
    print(f"   Deleted (unrecoverable): {deleted} images")
    print("=" * 60)

    # Verify
    remaining = ProductImage.objects.filter(image_url__isnull=True).exclude(image='').count()
    print(f"\n   Remaining broken: {remaining}")


if __name__ == '__main__':
    main()