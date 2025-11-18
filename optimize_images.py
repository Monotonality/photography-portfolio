#!/usr/bin/env python3
"""
Image optimization script for photography portfolio
- Converts images to WebP format with high quality (92%)
- Resizes to max 3000px width (preserves aspect ratio)
- Keeps original JPEGs as fallback
"""

from PIL import Image
import os
from pathlib import Path

def optimize_image(input_path, output_path, max_width=3000, quality=92):
    """
    Optimize image: resize if needed and convert to WebP
    
    Args:
        input_path: Path to source image
        output_path: Path to save WebP version
        max_width: Maximum width in pixels (maintains aspect ratio)
        quality: WebP quality (0-100, higher = better quality)
    """
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert RGBA to RGB if needed (WebP supports both, but RGB is smaller)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparency
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if image is larger than max_width
        if img.width > max_width:
            # Calculate new height maintaining aspect ratio
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"  Resized: {input_path.name} from {Image.open(input_path).size} to {img.size}")
        else:
            print(f"  No resize needed: {input_path.name} ({img.size})")
        
        # Save as WebP
        img.save(output_path, 'WEBP', quality=quality, method=6)
        
        # Get file sizes for comparison
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        webp_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        reduction = ((original_size - webp_size) / original_size) * 100
        
        print(f"  [OK] Created: {output_path.name}")
        print(f"    Size: {original_size:.2f}MB -> {webp_size:.2f}MB ({reduction:.1f}% reduction)")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Error processing {input_path.name}: {str(e)}")
        return False

def main():
    photos_dir = Path('dist/assets/PHOTOS')
    
    if not photos_dir.exists():
        print(f"Error: Directory {photos_dir} not found!")
        return
    
    # Get all image files
    image_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    image_files = [f for f in photos_dir.iterdir() 
                   if f.suffix.lower() in image_extensions and not f.name.endswith('.webp')]
    
    if not image_files:
        print("No images found to optimize!")
        return
    
    print(f"Found {len(image_files)} images to optimize...")
    print("=" * 60)
    
    optimized_count = 0
    skipped_count = 0
    
    for img_file in sorted(image_files):
        # Create WebP filename
        webp_path = img_file.with_suffix('.webp')
        
        # Skip if WebP already exists and is newer
        if webp_path.exists():
            if webp_path.stat().st_mtime > img_file.stat().st_mtime:
                print(f"  [SKIP] Skipping {img_file.name} (WebP already exists and is newer)")
                skipped_count += 1
                continue
        
        print(f"\nProcessing: {img_file.name}")
        if optimize_image(img_file, webp_path):
            optimized_count += 1
    
    print("\n" + "=" * 60)
    print(f"Optimization complete!")
    print(f"  [OK] Optimized: {optimized_count} images")
    print(f"  [SKIP] Skipped: {skipped_count} images")
    print(f"\nNext step: Update HTML to use WebP with JPEG fallback")

if __name__ == '__main__':
    main()

