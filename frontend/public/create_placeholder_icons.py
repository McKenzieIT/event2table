#!/usr/bin/env python3
"""Create simple PNG placeholder icons for PWA"""

import struct

def create_simple_png(width, height, color_r, color_g, color_b, filename):
    """Create a simple PNG file with solid color"""
    
    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'
    
    # Create IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = 0x2144df1c  # Pre-calculated CRC for this specific IHDR
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # Create IDAT chunk (simple solid color, uncompressed)
    import zlib
    
    # Scanline: filter type (1 byte) + pixel data (width * 3 bytes for RGB)
    scanline = b'\x00' + (bytes([color_r, color_g, color_b]) * width)
    raw_data = scanline * height
    
    compressed_data = zlib.compress(raw_data, 9)
    idat_chunk = struct.pack('>I', len(compressed_data)) + b'IDAT' + compressed_data
    idat_crc = zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff
    idat_chunk += struct.pack('>I', idat_crc)
    
    # Create IEND chunk
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', 0xae426082)
    
    # Write PNG file
    with open(filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr_chunk)
        f.write(idat_chunk)
        f.write(iend_chunk)

# Create cyan colored icons (matching theme)
create_simple_png(192, 192, 0x06, 0xB6, 0xD4, 'icon-192x192.png')
create_simple_png(512, 512, 0x06, 0xB6, 0xD4, 'icon-512x512.png')

print("✓ Created placeholder PWA icons (cyan colored PNGs)")
