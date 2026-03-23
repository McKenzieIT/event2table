import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    testTimeout: 10000, // Increase default timeout to 10s
    // Exclude E2E tests (Playwright) and other non-unit test files
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/test/e2e/**',
      '**/tests/e2e/**',
      '**/test/manual/**',
      '**/test/performance/**',
      '**/tests/debug/**',
    ],
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
      '@test': path.resolve(__dirname, './test'),
    }
  }
});
