import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // 🆕 开发模式：不使用base前缀，直接访问根路径
  // 生产模式：使用 /frontend/dist/ 前缀
  const isDev = mode === 'development';

  return {
    plugins: [react()],
    base: '/',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@canvas': path.resolve(__dirname, './src/canvas'),
      '@features': path.resolve(__dirname, './src/features'),
      '@event-builder': path.resolve(__dirname, './src/event-builder'),
      '@analytics': path.resolve(__dirname, './src/analytics'),
      '@canvas-react': path.resolve(__dirname, '../canvas-react/src'),
    },
  },
  // 优化依赖预构建，强制预构建ReactFlow以避免TDZ错误
  optimizeDeps: {
    include: ['reactflow'],  // 强制预构建ReactFlow，确保模块正确加载
  },
  server: {
    port: 5173,
    host: '0.0.0.0', // 🆕 监听所有网络接口（localhost, 127.0.0.1, 局域网IP）
    strictPort: true, // 如果端口被占用则失败
    // 🆕 API代理：将 /api、/event_node_builder 和 /common-params 请求转发到Flask后端
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      },
      '/event_node_builder': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      },
      '/common-params': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      },
      '/hql-preview-v2': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
      }
    }
  },
    build: {
    outDir: 'dist',
    emptyOutDir: true,
    // 性能优化：启用CSS代码分割
    cssCodeSplit: true,
    // 性能优化：设置chunk大小警告限制
    chunkSizeWarningLimit: 1000,
    // 🔥 性能优化：启用源映射用于调试
    sourcemap: false,
    // 🔥 性能优化：压缩代码
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      // Remove reactflow from external so it gets bundled
      // Only exclude canvas-react which is a separate package
      external: [/^@canvas-react\/.*/],
      output: {
        // 🔥 性能优化：更细粒度的代码分割
        manualChunks: {
          'reactflow-vendor': ['reactflow'],
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'query-vendor': ['@tanstack/react-query'],
        },
        // 🔥 性能优化：设置chunk大小限制，强制分割大包
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          if (/\.css$/i.test(assetInfo.name)) {
            return 'assets/css/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      }
    },
  },
  };
});
