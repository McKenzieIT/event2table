#!/usr/bin/env python3
"""Create simple PWA icons using PIL"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text, output_path):
    """Create a simple square icon with text"""
    # Create image
    img = Image.new('RGB', (size, size), color='#0f172a')

    # Draw text
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        font_size = int(size * 0.4)
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
    except:
        font = ImageFont.load_default()

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text
    x = (size - text_width) / 2
    y = (size - text_height) / 2

    draw.text((x, y), text, fill='white', font=font)

    # Save
    img.save(output_path)
    print(f"✅ Created {output_path} ({size}x{size})")

def main():
    os.makedirs('public/icons', exist_ok=True)

    # Create icons
    create_icon(192, 'E2T', 'public/icons/icon-192x192.png')
    create_icon(512, 'E2T', 'public/icons/icon-512x512.png')

    print("✅ PWA icons created successfully")

if __name__ == '__main__':
    main()
