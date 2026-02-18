import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'dist/']
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@canvas': path.resolve(__dirname, './src/canvas'),
      '@features': path.resolve(__dirname, './src/features'),
      '@event-builder': path.resolve(__dirname, './src/event-builder'),
      '@analytics': path.resolve(__dirname, './src/analytics'),
      '@canvas-react': path.resolve(__dirname, '../canvas-react/src'),
      '@types': path.resolve(__dirname, './src/types'),
    }
  }
});
