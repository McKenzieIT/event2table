/**
 * Performance Configuration for Event2Table
 * Centralized configuration for code splitting, lazy loading, and preloading strategies
 */

export interface CodeSplitConfig {
  chunkSize: number;
  maxChunks: number;
  minChunks: number;
  vendorChunks: boolean;
  commonChunks: boolean;
}

export interface LazyLoadConfig {
  routeChunks: boolean;
  componentChunks: boolean;
  imageLazyLoad: boolean;
  intersectionObserver: boolean;
  rootMargin: string;
  threshold: number;
}

export interface PreloadConfig {
  criticalCSS: boolean;
  fontPreload: string[];
  scriptPreload: string[];
  resourceHints: {
    preload: string[];
    prefetch: string[];
    preconnect: string[];
  };
}

export interface PerformanceConfig {
  codeSplit: CodeSplitConfig;
  lazyLoad: LazyLoadConfig;
  preload: PreloadConfig;
}

/**
 * Default performance configuration optimized for Event2Table
 */
export const performanceConfig: PerformanceConfig = {
  codeSplit: {
    chunkSize: 244 * 1024, // 244KB - optimal chunk size for caching
    maxChunks: 30,
    minChunks: 2,
    vendorChunks: true,
    commonChunks: true,
  },
  
  lazyLoad: {
    routeChunks: true,
    componentChunks: true,
    imageLazyLoad: true,
    intersectionObserver: true,
    rootMargin: '50px',
    threshold: 0.01,
  },
  
  preload: {
    criticalCSS: true,
    fontPreload: [
      '/fonts/inter-var.woff2',
      '/fonts/inter-regular.woff2',
    ],
    scriptPreload: [
      '/js/vendor.js',
      '/js/main.js',
    ],
    resourceHints: {
      preload: [
        '/api/graphql',
      ],
      prefetch: [
        '/api/events',
        '/api/tables',
      ],
      preconnect: [
        'https://api.event2table.com',
        'https://cdn.event2table.com',
      ],
    },
  },
};

/**
 * Get configuration for specific environment
 */
export const getPerformanceConfig = (env: 'development' | 'production' | 'test' = 'production'): PerformanceConfig => {
  const config = { ...performanceConfig };
  
  if (env === 'development') {
    // Disable optimizations in development for faster builds
    config.codeSplit.chunkSize = 1024 * 1024; // 1MB chunks in dev
    config.lazyLoad.imageLazyLoad = false;
  }
  
  if (env === 'test') {
    // Minimal optimizations for testing
    config.codeSplit.vendorChunks = false;
    config.lazyLoad.routeChunks = false;
  }
  
  return config;
};

/**
 * Route-based code splitting configuration
 */
export const routeChunks = {
  dashboard: () => import('../pages/Dashboard'),
  events: () => import('../pages/Events'),
  tables: () => import('../pages/Tables'),
  settings: () => import('../pages/Settings'),
  analytics: () => import('../pages/Analytics'),
};

/**
 * Component-based lazy loading configuration
 */
export const componentChunks = {
  Chart: () => import('../components/Chart'),
  Table: () => import('../components/Table'),
  Form: () => import('../components/Form'),
  Modal: () => import('../components/Modal'),
  Notification: () => import('../components/Notification'),
};
