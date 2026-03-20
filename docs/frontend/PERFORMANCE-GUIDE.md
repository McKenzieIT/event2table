# Performance Optimization Guide for Event2Table

## Overview

This guide provides comprehensive performance optimization strategies and best practices for Event2Table frontend application. It covers code splitting, lazy loading, caching, and runtime optimizations to improve application loading speed and user experience.

## Table of Contents

1. [Performance Configuration](#performance-configuration)
2. [Code Splitting](#code-splitting)
3. [Lazy Loading](#lazy-loading)
4. [Performance Utilities](#performance-utilities)
5. [Performance Hooks](#performance-hooks)
6. [Performance Metrics](#performance-metrics)
7. [Best Practices](#best-practices)
8. [Usage Examples](#usage-examples)

---

## Performance Configuration

### Location
`frontend/src/config/performanceConfig.ts`

### Overview
Centralized configuration for all performance-related settings including code splitting, lazy loading, and preloading strategies.

### Configuration Options

#### Code Splitting Configuration
```typescript
{
  chunkSize: 244 * 1024,      // 244KB - optimal for browser caching
  maxChunks: 30,               // Maximum number of chunks
  minChunks: 2,                // Minimum number of chunks
  vendorChunks: true,          // Separate vendor libraries
  commonChunks: true,          // Extract common code
}
```

#### Lazy Loading Configuration
```typescript
{
  routeChunks: true,           // Enable route-based code splitting
  componentChunks: true,       // Enable component-based lazy loading
  imageLazyLoad: true,         // Enable image lazy loading
  intersectionObserver: true,  // Use Intersection Observer API
  rootMargin: '50px',          // Margin for lazy loading
  threshold: 0.01,             // Visibility threshold
}
```

#### Preload Configuration
```typescript
{
  criticalCSS: true,           // Inline critical CSS
  fontPreload: [...],          // Preload fonts
  scriptPreload: [...],        // Preload critical scripts
  resourceHints: {
    preload: [...],            // Preload critical resources
    prefetch: [...],           // Prefetch likely resources
    preconnect: [...]          // Preconnect to origins
  }
}
```

### Environment-Specific Configuration

```typescript
import { getPerformanceConfig } from '@/config/performanceConfig';

// Get config for current environment
const config = getPerformanceConfig('production');

// Development: Larger chunks, disabled optimizations
const devConfig = getPerformanceConfig('development');

// Test: Minimal optimizations
const testConfig = getPerformanceConfig('test');
```

---

## Code Splitting

### Route-Based Code Splitting

Split your application routes into separate chunks that are loaded on-demand.

```typescript
import { routeChunks } from '@/config/performanceConfig';

// Define routes with lazy loading
const routes = [
  {
    path: '/dashboard',
    component: lazy(routeChunks.dashboard),
  },
  {
    path: '/events',
    component: lazy(routeChunks.events),
  },
  {
    path: '/tables',
    component: lazy(routeChunks.tables),
  },
];

// Wrap with Suspense for loading state
function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        {routes.map(route => (
          <Route
            key={route.path}
            path={route.path}
            element={<route.component />}
          />
        ))}
      </Routes>
    </Suspense>
  );
}
```

### Component-Based Lazy Loading

Lazy load heavy components that are not immediately visible.

```typescript
import { componentChunks } from '@/config/performanceConfig';

// Lazy load heavy components
const Chart = lazy(componentChunks.Chart);
const Table = lazy(componentChunks.Table);
const Modal = lazy(componentChunks.Modal);

function Dashboard() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div>
      <Suspense fallback={<div>Loading chart...</div>}>
        <Chart data={data} />
      </Suspense>

      {showModal && (
        <Suspense fallback={<div>Loading modal...</div>}>
          <Modal onClose={() => setShowModal(false)}>
            <Content />
          </Modal>
        </Suspense>
      )}
    </div>
  );
}
```

---

## Lazy Loading

### Image Lazy Loading

Automatically load images when they enter the viewport.

```typescript
import { useLazyLoad } from '@/shared/hooks/usePerformance';

function ProductImage({ src, alt }: { src: string; alt: string }) {
  const { imgRef, isLoaded, isLoading } = useLazyLoad(src);

  return (
    <div className="image-container">
      {isLoading && <div className="skeleton" />}
      <img
        ref={imgRef}
        alt={alt}
        className={isLoaded ? 'loaded' : 'loading'}
        style={{ opacity: isLoaded ? 1 : 0 }}
      />
    </div>
  );
}
```

### Component Lazy Loading Hook

Load components on-demand with a custom hook.

```typescript
import { useLazyLoadComponent } from '@/shared/hooks/usePerformance';

function LazyComponentWrapper() {
  const HeavyComponent = useLazyLoadComponent(
    () => import('./HeavyComponent'),
    () => <LoadingSpinner />
  );

  if (!HeavyComponent) {
    return <LoadingSpinner />;
  }

  return <HeavyComponent />;
}
```

---

## Performance Utilities

### Debounce

Delay function execution until after a specified wait time.

```typescript
import { debounce } from '@/shared/utils/performanceUtils';

// Debounce search input
const handleSearch = debounce((query: string) => {
  fetch(`/api/search?q=${query}`);
}, 300);

// Usage
searchInput.addEventListener('input', (e) => {
  handleSearch(e.target.value);
});
```

### Throttle

Limit function execution to once per specified time period.

```typescript
import { throttle } from '@/shared/utils/performanceUtils';

// Throttle scroll handler
const handleScroll = throttle(() => {
  const scrollTop = window.pageYOffset;
  updateHeaderPosition(scrollTop);
}, 100);

// Usage
window.addEventListener('scroll', handleScroll);
```

### Virtual Scroll

Render only visible items for large lists.

```typescript
import { calculateVirtualScroll } from '@/shared/utils/performanceUtils';

function VirtualList({ items }: { items: any[] }) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerHeight = 600;
  const itemHeight = 50;

  const { visibleStart, visibleEnd, offsetY, totalHeight } = calculateVirtualScroll(
    scrollTop,
    {
      containerHeight,
      itemHeight,
      totalItems: items.length,
      overscan: 3,
    }
  );

  const visibleItems = items.slice(visibleStart, visibleEnd);

  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div key={visibleStart + index} style={{ height: itemHeight }}>
              {item.content}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Performance Monitoring

Monitor Core Web Vitals and performance metrics.

```typescript
import { PerformanceMonitor } from '@/shared/utils/performanceUtils';

// Initialize performance monitor
const monitor = new PerformanceMonitor();

// Get metrics
const metrics = monitor.getMetrics();
console.log('FCP:', metrics.fcp);
console.log('LCP:', metrics.lcp);
console.log('FID:', metrics.fid);
console.log('CLS:', metrics.cls);

// Get performance score
const score = monitor.getScore();
console.log('Performance Score:', score);

// Cleanup when done
monitor.destroy();
```

---

## Performance Hooks

### useDebounce

Debounce value changes in React components.

```typescript
import { useDebounce } from '@/shared/hooks/usePerformance';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      fetchSearchResults(debouncedQuery);
    }
  }, [debouncedQuery]);

  return (
    <input
      type="text"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

### useThrottle

Throttle value changes in React components.

```typescript
import { useThrottle } from '@/shared/hooks/usePerformance';

function ScrollIndicator() {
  const [scrollY, setScrollY] = useState(0);
  const throttledScrollY = useThrottle(scrollY, 100);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="progress-bar">
      <div
        className="progress"
        style={{ width: `${throttledScrollY}%` }}
      />
    </div>
  );
}
```

### useLazyLoad

Lazy load images in React components.

```typescript
import { useLazyLoad } from '@/shared/hooks/usePerformance';

function ImageGallery({ images }: { images: string[] }) {
  return (
    <div className="gallery">
      {images.map((src, index) => (
        <LazyImage key={index} src={src} alt={`Image ${index}`} />
      ))}
    </div>
  );
}

function LazyImage({ src, alt }: { src: string; alt: string }) {
  const { imgRef, isLoaded, isLoading } = useLazyLoad(src);

  return (
    <div className="image-wrapper">
      {isLoading && <div className="placeholder" />}
      <img
        ref={imgRef}
        alt={alt}
        className={isLoaded ? 'fade-in' : ''}
        loading="lazy"
      />
    </div>
  );
}
```

### usePerformanceMonitor

Monitor performance metrics in React components.

```typescript
import { usePerformanceMonitor } from '@/shared/hooks/usePerformance';

function PerformanceDashboard() {
  const { metrics, score } = usePerformanceMonitor();

  return (
    <div className="performance-dashboard">
      <h2>Performance Metrics</h2>
      <div className="metric">
        <span>FCP:</span>
        <span>{metrics.fcp?.toFixed(0)}ms</span>
      </div>
      <div className="metric">
        <span>LCP:</span>
        <span>{metrics.lcp?.toFixed(0)}ms</span>
      </div>
      <div className="metric">
        <span>FID:</span>
        <span>{metrics.fid?.toFixed(0)}ms</span>
      </div>
      <div className="metric">
        <span>CLS:</span>
        <span>{metrics.cls?.toFixed(3)}</span>
      </div>
      <div className="score">
        <span>Performance Score:</span>
        <span className={score >= 90 ? 'good' : 'warning'}>
          {score}/100
        </span>
      </div>
    </div>
  );
}
```

### useVirtualScroll

Implement virtual scrolling for large lists.

```typescript
import { useVirtualScroll } from '@/shared/hooks/usePerformance';

function LargeDataList({ data }: { data: any[] }) {
  const {
    containerRef,
    visibleItems,
    offsetY,
    totalHeight,
    handleScroll,
    startIndex,
  } = useVirtualScroll(data, 50, 600, 3);

  return (
    <div
      ref={containerRef}
      className="virtual-list"
      style={{ height: 600, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div
              key={startIndex + index}
              className="list-item"
              style={{ height: 50 }}
            >
              {item.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Performance Metrics

### Core Web Vitals

#### First Contentful Paint (FCP)
- **Target:** < 1.8 seconds
- **Definition:** Time when the first text or image is painted
- **Impact:** Perceived loading speed

#### Largest Contentful Paint (LCP)
- **Target:** < 2.5 seconds
- **Definition:** Time when the largest content element is painted
- **Impact:** Perceived loading speed and main content visibility

#### First Input Delay (FID)
- **Target:** < 100 milliseconds
- **Definition:** Time from user interaction to browser response
- **Impact:** Interactivity and perceived responsiveness

#### Cumulative Layout Shift (CLS)
- **Target:** < 0.1
- **Definition:** Measure of unexpected layout shifts
- **Impact:** Visual stability and user experience

### Additional Metrics

#### Time to First Byte (TTFB)
- **Target:** < 600 milliseconds
- **Definition:** Time from request to first byte of response
- **Impact:** Server response time

#### DOM Content Loaded
- **Target:** < 1.5 seconds
- **Definition:** Time when DOM is fully parsed
- **Impact:** Initial render readiness

#### Load Complete
- **Target:** < 3 seconds
- **Definition:** Time when all resources are loaded
- **Impact:** Full functionality availability

---

## Best Practices

### 1. Code Splitting

- **Split by route:** Separate chunks for each major route
- **Split by feature:** Group related functionality together
- **Vendor chunks:** Extract third-party libraries
- **Common chunks:** Extract shared code between routes

### 2. Lazy Loading

- **Lazy load images below the fold:** Use Intersection Observer
- **Lazy load heavy components:** Load only when needed
- **Provide loading states:** Show skeletons or spinners
- **Preload critical resources:** Load important resources early

### 3. Performance Optimization

- **Debounce user input:** Search, resize, scroll events
- **Throttle frequent events:** Scroll, mousemove, resize
- **Use virtual scrolling:** For lists with 100+ items
- **Memoize expensive computations:** Use useMemo and useCallback

### 4. Resource Optimization

- **Optimize images:** Use WebP format, compress images
- **Minify code:** Remove whitespace and comments
- **Enable compression:** Use gzip or brotli
- **Use CDN:** Serve static assets from CDN

### 5. Caching Strategy

- **Cache static assets:** Long cache headers for static files
- **Cache API responses:** Use service workers or HTTP cache
- **Implement cache invalidation:** Version your assets
- **Use localStorage:** Cache user preferences

### 6. Bundle Optimization

- **Tree shaking:** Remove unused code
- **Code splitting:** Split bundles into smaller chunks
- **Analyze bundle size:** Use webpack-bundle-analyzer
- **Remove dependencies:** Eliminate unused dependencies

### 7. Runtime Performance

- **Avoid layout thrashing:** Batch DOM reads and writes
- **Use requestAnimationFrame:** For animations
- **Optimize re-renders:** Use React.memo and useMemo
- **Web Workers:** Offload heavy computations

---

## Usage Examples

### Example 1: Optimized Search Component

```typescript
import { useState } from 'react';
import { useDebounce } from '@/shared/hooks/usePerformance';

function OptimizedSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery.length > 2) {
      fetchSearchResults(debouncedQuery).then(setResults);
    }
  }, [debouncedQuery]);

  return (
    <div className="search-container">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {results.length > 0 && (
        <ul className="search-results">
          {results.map((result) => (
            <li key={result.id}>{result.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Example 2: Virtualized Data Table

```typescript
import { useVirtualScroll } from '@/shared/hooks/usePerformance';

function VirtualizedTable({ data }: { data: any[] }) {
  const {
    containerRef,
    visibleItems,
    offsetY,
    totalHeight,
    handleScroll,
  } = useVirtualScroll(data, 40, 500, 5);

  return (
    <div className="table-container">
      <div className="table-header">
        <div className="cell">ID</div>
        <div className="cell">Name</div>
        <div className="cell">Value</div>
      </div>
      <div
        ref={containerRef}
        className="table-body"
        style={{ height: 500, overflow: 'auto' }}
        onScroll={handleScroll}
      >
        <div style={{ height: totalHeight, position: 'relative' }}>
          <div style={{ transform: `translateY(${offsetY}px)` }}>
            {visibleItems.map((row) => (
              <div key={row.id} className="table-row" style={{ height: 40 }}>
                <div className="cell">{row.id}</div>
                <div className="cell">{row.name}</div>
                <div className="cell">{row.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Example 3: Lazy Loaded Image Gallery

```typescript
import { useLazyLoad } from '@/shared/hooks/usePerformance';

function LazyImageGallery({ images }: { images: string[] }) {
  return (
    <div className="gallery">
      {images.map((src, index) => (
        <LazyImage
          key={index}
          src={src}
          alt={`Gallery image ${index + 1}`}
        />
      ))}
    </div>
  );
}

function LazyImage({ src, alt }: { src: string; alt: string }) {
  const { imgRef, isLoaded, isLoading } = useLazyLoad(src, {
    rootMargin: '100px',
    threshold: 0.01,
  });

  return (
    <div className="gallery-item">
      {isLoading && (
        <div className="skeleton">
          <div className="skeleton-pulse" />
        </div>
      )}
      <img
        ref={imgRef}
        alt={alt}
        className={`gallery-image ${isLoaded ? 'loaded' : ''}`}
        loading="lazy"
      />
    </div>
  );
}
```

### Example 4: Performance Monitoring Dashboard

```typescript
import { usePerformanceMonitor } from '@/shared/hooks/usePerformance';

function PerformanceMonitorDashboard() {
  const { metrics, score } = usePerformanceMonitor();

  const getMetricStatus = (value: number | undefined, target: number) => {
    if (!value) return 'pending';
    return value <= target ? 'good' : 'needs-improvement';
  };

  return (
    <div className="performance-dashboard">
      <h2>Performance Monitor</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>First Contentful Paint</h3>
          <div className="metric-value">
            {metrics.fcp?.toFixed(0)}ms
          </div>
          <div className={`metric-status ${getMetricStatus(metrics.fcp, 1800)}`}>
            Target: < 1.8s
          </div>
        </div>

        <div className="metric-card">
          <h3>Largest Contentful Paint</h3>
          <div className="metric-value">
            {metrics.lcp?.toFixed(0)}ms
          </div>
          <div className={`metric-status ${getMetricStatus(metrics.lcp, 2500)}`}>
            Target: < 2.5s
          </div>
        </div>

        <div className="metric-card">
          <h3>First Input Delay</h3>
          <div className="metric-value">
            {metrics.fid?.toFixed(0)}ms
          </div>
          <div className={`metric-status ${getMetricStatus(metrics.fid, 100)}`}>
            Target: < 100ms
          </div>
        </div>

        <div className="metric-card">
          <h3>Cumulative Layout Shift</h3>
          <div className="metric-value">
            {metrics.cls?.toFixed(3)}
          </div>
          <div className={`metric-status ${getMetricStatus(metrics.cls || 0, 0.1)}`}>
            Target: < 0.1
          </div>
        </div>
      </div>

      <div className="performance-score">
        <h3>Overall Performance Score</h3>
        <div className={`score-value ${score >= 90 ? 'good' : score >= 50 ? 'warning' : 'poor'}`}>
          {score}/100
        </div>
      </div>
    </div>
  );
}
```

---

## Troubleshooting

### Common Performance Issues

#### 1. Large Bundle Size
- **Problem:** Initial load is slow
- **Solution:** Implement code splitting and lazy loading
- **Tools:** webpack-bundle-analyzer

#### 2. Slow First Contentful Paint
- **Problem:** Users see blank screen for too long
- **Solution:** Inline critical CSS, preload critical resources
- **Tools:** Lighthouse, Chrome DevTools

#### 3. High Cumulative Layout Shift
- **Problem:** Elements shift around during loading
- **Solution:** Reserve space for images and dynamic content
- **Tools:** Chrome DevTools Layout Shift Regions

#### 4. Slow Interactivity
- **Problem:** App feels unresponsive
- **Solution:** Debounce/throttle events, use Web Workers
- **Tools:** Chrome DevTools Performance tab

---

## Additional Resources

- [Web.dev Performance](https://web.dev/performance/)
- [MDN Web Performance](https://developer.mozilla.org/en-US/docs/Web/Performance)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)

---

## Conclusion

Performance optimization is an ongoing process. Regular monitoring and optimization are essential to maintain a fast and responsive user experience. Use the tools and techniques provided in this guide to continuously improve Event2Table's performance.

For questions or suggestions, please contact the development team.
