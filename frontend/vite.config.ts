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
    include: [
      'reactflow'
    ],
    // Exclude Apollo Client from pre-bundling to ensure React hooks are available
    exclude: ['@apollo/client', '@apollo/client/react'],
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
    // 性能优化：启用源映射用于调试
    sourcemap: false,
    // 🔥 性能优化：压缩代码
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        // 🔥 额外优化：移除未使用的代码
        dead_code: true,
        conditionals: true,
        evaluate: true,
        sequences: true,
        unused: true,
      },
      format: {
        // 🔥 优化：移除注释
        comments: false,
      },
      mangle: {
        // 🔥 优化：混淆变量名（减小bundle大小）
        safari10: true,
      },
    },
    rollupOptions: {
      // Externalize canvas-react only as Apollo Client needs proper bundling
      external: [/^@canvas-react\/.*/],
      output: {
        // 🔥 性能优化：更细粒度的代码分割（解决循环依赖）
        manualChunks: (id) => {
          // Node_modules in vendor chunks
          if (id.includes('node_modules')) {
            // React + Apollo together (avoid circular dependency)
            if (id.includes('react') || id.includes('react-dom') ||
                id.includes('react-router-dom') || id.includes('@apollo/client') ||
                id.includes('graphql')) {
              return 'vendor-react-apollo';
            }
            // ReactFlow vendor
            if (id.includes('reactflow') || id.includes('@xyflow/react')) {
              return 'vendor-reactflow';
            }
            // TanStack Query vendor
            if (id.includes('@tanstack/react-query')) {
              return 'vendor-query';
            }
            // CodeMirror editor vendor
            if (id.includes('@codemirror') || id.includes('lezer')) {
              return 'vendor-editor';
            }
            // Radix UI vendor
            if (id.includes('@radix-ui')) {
              return 'vendor-ui';
            }
            // Other vendor
            return 'vendor';
          }
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
        // 🔥 性能优化：紧凑输出和内部导出压缩
        compact: true,
        minifyInternalExports: true,
      }
    },
    // 🔥 性能优化：启用compression
    compression: 'brotli',
    // 🔥 性能优化：降低chunk大小警告限制
    chunkSizeWarningLimit: 800,
  },
  };
});
