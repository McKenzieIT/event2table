import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // 🆕 开发模式：不使用base前缀，直接访问根路径
  // 生产模式：使用 /frontend/dist/ 前缀
  const isDev = mode === 'development';

  return {
    plugins: [react()],
    base: isDev ? '/' : '/frontend/dist/',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@canvas': path.resolve(__dirname, './src/canvas'),
      '@event-builder': path.resolve(__dirname, './src/event-builder'),
      '@analytics': path.resolve(__dirname, './src/analytics'),
      '@canvas-react': path.resolve(__dirname, '../canvas-react/src'),
    },
  },
  // 优化依赖预构建，避免ReactFlow的TDZ错误
  optimizeDeps: {
    exclude: ['reactflow'],  // 排除ReactFlow，使用源码而非预构建
  },
  server: {
    port: 5173,
    host: '0.0.0.0', // 🆕 监听所有网络接口（localhost, 127.0.0.1, 局域网IP）
    strictPort: true, // 如果端口被占用则失败
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    // 性能优化：启用CSS代码分割
    cssCodeSplit: true,
    // 性能优化：设置chunk大小警告限制
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      // Remove reactflow from external so it gets bundled
      // Only exclude canvas-react which is a separate package
      external: [/^@canvas-react\/.*/],
      output: {
        // Disable manual chunks - use Vite's automatic chunking
        // to avoid Temporal Dead Zone (TDZ) errors
      }
    },
  },
  };
});
