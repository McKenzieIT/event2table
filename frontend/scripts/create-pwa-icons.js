#!/usr/bin/env node
/**
 * Create simple PWA icons using Node.js canvas
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create a simple SVG icon
function createSVGIcon(size, text) {
  const svg = `
<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="#0f172a"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${size * 0.4}"
        fill="white" text-anchor="middle" dominant-baseline="middle" dy=".3em">${text}</text>
</svg>
  `.trim();
  return svg;
}

function createPNGFromSVG(svg, outputPath) {
  // For now, save as SVG (browsers can convert)
  // In production, you'd use sharp or canvas library
  const pngPath = outputPath.replace('.svg', '.png');

  // Use a simple approach: create a minimal valid PNG
  // This is a 1x1 blue PNG (base64 encoded)
  const minimalPNG = Buffer.from(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
    'base64'
  );

  // Copy the minimal PNG (we'll replace with proper icons later)
  fs.writeFileSync(pngPath, minimalPNG);
  console.log(`✅ Created ${pngPath}`);

  // Also save SVG for reference
  fs.writeFileSync(outputPath, svg);
  console.log(`✅ Created ${outputPath}`);
}

function main() {
  const iconsDir = path.join(__dirname, '..', 'public', 'icons');
  fs.mkdirSync(iconsDir, { recursive: true });

  // Create 192x192 icon
  const svg192 = createSVGIcon(192, 'E2T');
  createPNGFromSVG(svg192, path.join(iconsDir, 'icon-192x192.svg'));

  // Create 512x512 icon
  const svg512 = createSVGIcon(512, 'E2T');
  createPNGFromSVG(svg512, path.join(iconsDir, 'icon-512x512.svg'));

  console.log('✅ PWA icons created successfully');
  console.log('⚠️  Note: Using placeholder icons. Replace with proper PNG files for production.');
}

main();
