#!/usr/bin/env python3
"""
OpenMV Datasheet Build System.

Usage:
    python build.py                    # Build all datasheets
    python build.py openmv-cam-h7      # Build a specific product
    python build.py --list             # List available products
"""

import argparse
import os
import sys
import glob
import yaml

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.engine import DatasheetBuilder


PRODUCTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products")
MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
GENERATED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def find_products():
    """Find all product YAML files, including subdirectories."""
    pattern = os.path.join(PRODUCTS_DIR, "**", "*.yaml")
    files = glob.glob(pattern, recursive=True)
    # Also check top-level for any remaining files
    files += glob.glob(os.path.join(PRODUCTS_DIR, "*.yaml"))
    # Deduplicate and sort
    seen = {}
    for f in sorted(set(files)):
        name = os.path.splitext(os.path.basename(f))[0]
        seen[name] = f
    return dict(sorted(seen.items()))


def build_product(name, yaml_path, output_dir=OUTPUT_DIR):
    """Build a single product datasheet."""
    print(f"Building: {name}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Mirror the products/ subdirectory structure in output/
    yaml_dir = os.path.dirname(yaml_path)
    rel = os.path.relpath(yaml_dir, PRODUCTS_DIR)
    if rel and rel != ".":
        product_output_dir = os.path.join(output_dir, rel)
    else:
        product_output_dir = output_dir

    builder = DatasheetBuilder(data, media_dir=MEDIA_DIR, output_dir=product_output_dir,
                               slug=name, generated_dir=GENERATED_DIR)
    output_path = builder.build()

    print(f"  -> {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Build OpenMV datasheets")
    parser.add_argument("products", nargs="*", help="Product names to build (omit for all)")
    parser.add_argument("--list", action="store_true", help="List available products")
    parser.add_argument("--output", default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    output_dir = args.output

    products = find_products()

    if args.list:
        print("Available products:")
        for name in products:
            print(f"  {name}")
        return

    if not products:
        print("No product YAML files found in products/")
        sys.exit(1)

    targets = args.products if args.products else list(products.keys())
    built = []
    errors = []

    for name in targets:
        if name not in products:
            print(f"Error: Unknown product '{name}'")
            print(f"Available: {', '.join(products.keys())}")
            errors.append(name)
            continue
        try:
            path = build_product(name, products[name], output_dir)
            built.append(path)
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            errors.append(name)

    print(f"\nBuilt {len(built)} datasheet(s), {len(errors)} error(s)")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
