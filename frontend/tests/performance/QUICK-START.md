# Frontend Performance Testing - Quick Start Guide

**DWD Generator - event2table Project**

This guide provides quick instructions for running performance tests on the frontend.

---

## Prerequisites

### Required Tools

```bash
# Node.js (v18 or higher)
node --version

# npm (v9 or higher)
npm --version

# Google Chrome (for DevTools testing)
# Install from: https://www.google.com/chrome/
```

### Install Dependencies

```bash
cd /Users/mckenzie/Documents/event2table/frontend

# Install npm dependencies
npm install

# Install Lighthouse CLI (optional, for automated testing)
npm install -g lighthouse

# Install Playwright browsers (for E2E performance tests)
npx playwright install
```

---

## Quick Performance Test (5 minutes)

### 1. Start Development Server

```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev
```

Expected output:
```
  VITE v7.3.1  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
```

**Target**: Server should start in < 5 seconds

### 2. Measure Initial Load Performance

**Method 1: Browser DevTools**
1. Open Chrome: http://localhost:5173
2. Press F12 (DevTools)
3. Go to "Performance" tab
4. Click "Refresh" button (reload page with recording)
5. Wait for page to load
6. Stop recording
7. Look for metrics:
   - **FCP** (First Contentful Paint): Target < 1.5s
   - **LCP** (Largest Contentful Paint): Target < 2.5s
   - **TTI** (Time to Interactive): Target < 3.5s

**Method 2: Lighthouse CLI**
```bash
# In another terminal
lighthouse http://localhost:5173 --view
```

Look for:
- Performance score: Target > 90
- FCP: < 1.5s (green)
- LCP: < 2.5s (green)
- TTI: < 3.5s (green)

### 3. Test Canvas Performance

**Manual FPS Test**:
1. Open http://localhost:5173
2. Navigate to "Field Builder" page
3. Open Chrome DevTools → Console
4. Paste this code:

```javascript
// Measure FPS
let frameCount = 0;
let startTime = performance.now();

function measureFPS() {
  frameCount++;
  const currentTime = performance.now();

  if (currentTime >= startTime + 1000) {
    const fps = Math.round((frameCount * 1000) / (currentTime - startTime));
    console.log(`FPS: ${fps}`);
    frameCount = 0;
    startTime = currentTime;
  }

  requestAnimationFrame(measureFPS);
}

measureFPS();
```

5. Add 10 nodes to canvas
6. Check console for FPS
7. **Target**: 60 FPS (or close to it)

### 4. Test Bundle Size

```bash
# Build production bundle
npm run build

# Check bundle sizes
ls -lh dist/assets/*.js
```

**Target**: Largest bundle < 500 KB

---

## Automated Performance Tests

### Run All Tests

```bash
cd /Users/mckenzie/Documents/event2table/frontend

# Make test script executable
chmod +x tests/performance/run-performance-tests.sh

# Run all tests
./tests/performance/run-performance-tests.sh
```

This will:
1. Measure dev server startup time
2. Measure production build time
3. Analyze bundle sizes
4. Run Lighthouse tests
5. Generate performance report

Results are saved to: `tests/performance/results/`

### Run Playwright Canvas Tests

```bash
cd /Users/mckenzie/Documents/event2table/frontend

# Start dev server first
npm run dev &

# In another terminal, run canvas performance tests
npx playwright test tests/performance/canvas-performance.spec.ts

# View results
npx playwright show-report
```

---

## Manual Performance Testing Checklist

### Initial Load Performance

- [ ] **FCP < 1.5s**: First Contentful Paint
  - Test: Chrome DevTools → Performance → Reload
  - Measure: Time to first content appears
  - Target: < 1500ms

- [ ] **LCP < 2.5s**: Largest Contentful Paint
  - Test: Chrome DevTools → Performance → Reload
  - Measure: Time to largest element loads
  - Target: < 2500ms

- [ ] **TTI < 3.5s**: Time to Interactive
  - Test: Chrome DevTools → Performance → Reload
  - Measure: Time to page is interactive
  - Target: < 3500ms

### Canvas Rendering Performance

- [ ] **60 FPS with 10 nodes**
  - Test: Add 10 nodes to canvas
  - Measure: Use FPS counter script
  - Target: ≥ 55 FPS

- [ ] **50 FPS with 50 nodes**
  - Test: Add 50 nodes to canvas
  - Measure: Use FPS counter script
  - Target: ≥ 50 FPS

- [ ] **40 FPS with 100 nodes**
  - Test: Add 100 nodes to canvas
  - Measure: Use FPS counter script
  - Target: ≥ 40 FPS

- [ ] **Drag operations < 100ms**
  - Test: Drag a node around
  - Measure: Chrome DevTools → Performance
  - Target: Input delay < 100ms

- [ ] **Zoom/Pan < 50ms**
  - Test: Zoom and pan canvas
  - Measure: Chrome DevTools → Performance
  - Target: Input delay < 50ms

### API Response Time

- [ ] **Fetch games list < 200ms**
  - Test: Navigate to games page
  - Measure: Chrome DevTools → Network
  - Target: API response < 200ms

- [ ] **Generate HQL < 500ms**
  - Test: Click "Generate HQL" button
  - Measure: Chrome DevTools → Network
  - Target: API response < 500ms

- [ ] **Save canvas flow < 200ms**
  - Test: Click "Save" button
  - Measure: Chrome DevTools → Network
  - Target: API response < 200ms

### Interaction Performance

- [ ] **Button click < 100ms**
  - Test: Click any button
  - Measure: Visual feedback time
  - Target: < 100ms

- [ ] **Form input < 100ms**
  - Test: Type in input field
  - Measure: Character appears quickly
  - Target: < 100ms delay

- [ ] **Modal open/close < 150ms**
  - Test: Open and close modal
  - Measure: Animation time
  - Target: < 150ms

### Build Performance

- [ ] **Dev server start < 5s**
  - Test: `npm run dev`
  - Measure: Time to "ready in..."
  - Target: < 5000ms

- [ ] **Production build < 60s**
  - Test: `npm run build`
  - Measure: Time to completion
  - Target: < 60000ms

- [ ] **HMR < 200ms**
  - Test: Make a code change
  - Measure: Time to browser update
  - Target: < 200ms

---

## Performance Budgets

### Bundle Size Budget

| Resource Type | Budget | Current | Status |
|--------------|--------|---------|--------|
| JavaScript (total) | 500 KB | TBD | - |
| CSS (total) | 100 KB | TBD | - |
| Images (each) | 200 KB | TBD | - |
| Fonts (each) | 100 KB | TBD | - |

### Performance Metrics Budget

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| First Contentful Paint | < 1.5s | TBD | - |
| Largest Contentful Paint | < 2.5s | TBD | - |
| Time to Interactive | < 3.5s | TBD | - |
| Total Blocking Time | < 200ms | TBD | - |
| Cumulative Layout Shift | < 0.1 | TBD | - |
| First Input Delay | < 100ms | TBD | - |

### Canvas Performance Budget

| Scenario | Target FPS | Current | Status |
|----------|-----------|---------|--------|
| 10 nodes | 60 FPS | TBD | - |
| 50 nodes | 50 FPS | TBD | - |
| 100 nodes | 40 FPS | TBD | - |
| Drag operations | < 100ms | TBD | - |
| Zoom/Pan | < 50ms | TBD | - |

---

## Common Performance Issues

### Issue 1: Low FPS on Canvas

**Symptoms**: FPS drops below 60 when adding nodes

**Diagnosis**:
```javascript
// Check FPS in console
// Check render times in DevTools
// Look for long tasks (> 50ms)
```

**Solutions**:
- Implement React.memo for node components
- Use virtual scrolling for large lists
- Debounce drag events
- Optimize ReactFlow configuration

### Issue 2: Slow Initial Load

**Symptoms**: FCP/LCP exceeds targets

**Diagnosis**:
```javascript
// Run Lighthouse
// Check network waterfall
// Look for large resources
```

**Solutions**:
- Implement code splitting
- Lazy load routes
- Optimize images and fonts
- Add compression

### Issue 3: Large Bundle Size

**Symptoms**: Main bundle > 500 KB

**Diagnosis**:
```bash
# Analyze bundle
npm run build
npx vite-bundle-visualizer
```

**Solutions**:
- Manual chunk splitting
- Tree shaking
- Remove unused dependencies
- Use lighter alternatives

### Issue 4: Memory Leaks

**Symptoms**: Memory keeps increasing

**Diagnosis**:
```javascript
// Chrome DevTools → Memory → Take heap snapshot
// Perform operations
// Take another snapshot
// Compare for detached DOM nodes
```

**Solutions**:
- Clean up event listeners
- Properly unmount components
- Avoid closures in loops
- Use WeakMap/WeakSet

---

## Interpreting Results

### Lighthouse Scores

| Score Range | Rating | Action |
|-------------|--------|--------|
| 90-100 | Excellent | Ready for production |
| 75-89 | Good | Minor optimizations |
| 50-74 | Needs Improvement | Significant optimizations |
| 0-49 | Poor | Major rework needed |

### FPS Ratings

| FPS | Rating | Action |
|-----|--------|--------|
| 60 | Perfect | No action needed |
| 55-59 | Excellent | Monitor |
| 45-54 | Good | Consider optimizations |
| 30-44 | Fair | Optimize soon |
| < 30 | Poor | Critical issue |

### Bundle Size Ratings

| Size | Rating | Action |
|------|--------|--------|
| < 500 KB | Excellent | Good |
| 500 KB - 1 MB | Good | Consider optimization |
| 1-2 MB | Fair | Should optimize |
| > 2 MB | Poor | Must optimize |

---

## Performance Testing Best Practices

### 1. Test on Realistic Hardware

- Don't test only on high-end dev machines
- Test on mid-range laptops (4-8 GB RAM)
- Test on older devices if possible

### 2. Test with Realistic Data

- Test with 1000+ games
- Test with 10000+ events
- Test with 100+ canvas nodes
- Don't test with empty data

### 3. Test Network Conditions

- Fast 4G (baseline)
- Slow 3G (worst case)
- Offline mode (edge case)

### 4. Run Tests Multiple Times

- Performance varies between runs
- Take average of 3-5 runs
- Look for consistent issues

### 5. Monitor Over Time

- Run tests weekly
- Track performance trends
- Catch regressions early

---

## Next Steps

### Immediate (This Week)

1. ✅ Run quick performance tests (5 min)
2. ✅ Run automated test suite (15 min)
3. ✅ Document baseline metrics
4. ⚠️ Identify performance bottlenecks
5. ⚠️ Implement quick wins

### Short-term (Next 2 Weeks)

1. Implement code splitting
2. Add lazy loading
3. Optimize canvas rendering
4. Set up performance monitoring
5. Create performance regression tests

### Long-term (Next Month)

1. Progressive Web App features
2. Advanced caching strategies
3. Server-side rendering consideration
4. Continuous performance monitoring
5. Performance budget enforcement

---

## Resources

### Documentation

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://github.com/GoogleChrome/lighthouse)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Vite Performance](https://vitejs.dev/guide/performance.html)

### Tools

- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Playwright](https://playwright.dev/)
- [Bundle Analyzer](https://www.npmjs.com/package/rollup-plugin-visualizer)

### Project Files

- Performance Report: `tests/performance/frontend-performance-test-report.md`
- Test Scripts: `tests/performance/run-performance-tests.sh`
- Canvas Tests: `tests/performance/canvas-performance.spec.ts`
- Monitor Component: `src/shared/ui/PerformanceMonitor.tsx`

---

## Support

### Questions?

- Review the full performance report
- Check Chrome DevTools documentation
- Run automated tests first
- Document findings with screenshots

### Performance Issues?

1. Collect metrics (Lighthouse, FPS, bundle size)
2. Identify bottleneck (network, rendering, memory)
3. Implement optimization
4. Measure improvement
5. Document results

### Need Help?

- Create detailed GitHub issue with metrics
- Include screenshots of DevTools
- Share test results
- Describe test environment

---

**Last Updated**: 2026-02-10
**Project**: DWD Generator (event2table)
**Frontend**: React + Vite + TypeScript
**Target**: 60 FPS Canvas Rendering
