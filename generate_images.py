#!/usr/bin/env python3
"""
Generate cartoon-style product images using OpenAI's image generation API.

Images are saved to media/generated/<slug>.png. The build engine automatically
uses these if they exist, falling back to the original cover_image in each YAML.

Usage:
    python generate_images.py                   # Generate missing images for all products
    python generate_images.py m8-fish-eye-lens  # Generate for a specific product
    python generate_images.py --force           # Regenerate all images
    python generate_images.py --list            # List products and image status

Requires:
    OPENAI_API_KEY environment variable set.
    pip install openai
"""

import argparse
import base64
import glob
import io
import os
import sys

from PIL import Image as PILImage
import yaml

PRODUCTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products")
MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
GENERATED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated")


def find_products():
    """Find all product YAML files."""
    pattern = os.path.join(PRODUCTS_DIR, "**", "*.yaml")
    files = glob.glob(pattern, recursive=True)
    seen = {}
    for f in sorted(set(files)):
        name = os.path.splitext(os.path.basename(f))[0]
        seen[name] = f
    return dict(sorted(seen.items()))


def generated_image_path(slug):
    """Return the expected path for a generated image."""
    return os.path.join(GENERATED_DIR, f"{slug}.png")


def generate_image(product_name, source_image_path, output_path):
    """Transform a product photo into a cartoon-style illustration using OpenAI's API."""
    from openai import OpenAI

    client = OpenAI()

    prompt = (
        f"Transform this product photo of an OpenMV {product_name} into a clean "
        f"cartoon-style vector illustration. Keep the exact same product, angle, "
        f"and composition. Pure white background. No text, labels, or watermarks. "
        f"Subtle shadows. Professional product illustration style. "
        f"The product should fill most of the frame with minimal white space around it."
    )

    with open(source_image_path, "rb") as img_file:
        response = client.images.edit(
            model="gpt-image-1.5",
            image=img_file,
            prompt=prompt,
            size="1024x1024",
        )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    image_bytes = base64.b64decode(response.data[0].b64_json)

    # Auto-crop whitespace and add a small margin
    img = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
    from PIL import ImageChops
    bg = PILImage.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    diff = diff.convert("L")
    diff = PILImage.eval(diff, lambda x: 255 if x > 20 else 0)
    bbox = diff.getbbox()
    if bbox:
        # Crop to content, add 12.5% margin, then pad to square
        cropped = img.crop(bbox)
        cw, ch = cropped.size
        margin_x = int(cw * 0.125)
        margin_y = int(ch * 0.125)
        padded_w = cw + 2 * margin_x
        padded_h = ch + 2 * margin_y
        side = max(padded_w, padded_h)
        result = PILImage.new(img.mode, (side, side), (255, 255, 255))
        offset_x = (side - cw) // 2
        offset_y = (side - ch) // 2
        result.paste(cropped, (offset_x, offset_y))
        img = result

    img.save(output_path)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate product images via OpenAI")
    parser.add_argument("products", nargs="*", help="Product slugs to generate (omit for all)")
    parser.add_argument("--force", action="store_true", help="Regenerate existing images")
    parser.add_argument("--list", action="store_true", help="List products and image status")
    args = parser.parse_args()

    products = find_products()

    if args.list:
        for slug in products:
            img_path = generated_image_path(slug)
            status = "exists" if os.path.exists(img_path) else "missing"
            print(f"  {slug:45s} [{status}]")
        return

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Get your API key from https://platform.openai.com/api-keys")
        sys.exit(1)

    targets = args.products if args.products else list(products.keys())
    generated = 0
    skipped = 0
    errors = []

    for slug in targets:
        if slug not in products:
            print(f"Error: Unknown product '{slug}'")
            errors.append(slug)
            continue

        img_path = generated_image_path(slug)

        if os.path.exists(img_path) and not args.force:
            skipped += 1
            continue

        yaml_path = products[slug]
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        product_name = data["meta"]["product_name"]
        cover_image = data["meta"].get("cover_image")
        if not cover_image:
            print(f"Skipping {slug}: no cover_image in YAML")
            skipped += 1
            continue

        source_path = os.path.join(MEDIA_DIR, cover_image)
        if not os.path.exists(source_path):
            print(f"Skipping {slug}: source image not found: {source_path}")
            skipped += 1
            continue

        print(f"Generating: {product_name} ...", end=" ", flush=True)
        try:
            generate_image(product_name, source_path, img_path)
            print("done")
            generated += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors.append(slug)

    print(f"\nGenerated {generated}, skipped {skipped}, errors {len(errors)}")
    if errors:
        print(f"Failed: {', '.join(errors)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
