# Event2Table Performance Testing - Implementation Guide

## 📋 Executive Summary

This guide provides step-by-step instructions for implementing comprehensive performance testing for the Event2Table application using Chrome DevTools Protocol (CDP).

## 🎯 Objectives

1. **Identify Performance Bottlenecks**: Measure real-world performance metrics across all pages
2. **Generate Actionable Recommendations**: Provide specific optimization strategies
3. **Track Performance Over Time**: Enable continuous monitoring and trend analysis
4. **Ensure User Experience**: Maintain Web Vitals compliance

## 📊 Pages Identified for Testing

### Critical Priority (Must Pass)
- **Dashboard** (`#/`) - Main entry point
- **Canvas** (`#/canvas`) - Complex flow builder
- **EventNodeBuilder** (`#/event-node-builder`) - Interactive builder

### High Priority (Should Pass)
- **Games** (`#/games`) - Data management
- **Events** (`#/events`) - Data listing
- **Parameters** (`#/parameters`) - Data listing
- **Generate** (`#/generate`) - Core functionality

### Medium Priority (Nice to Have)
- **FieldBuilder** (`#/field-builder`) - Tool
- **Categories** (`#/categories`) - Management
- **Flows** (`#/flows`) - Listing
- **HqlManage** (`#/hql-manage`) - Management

### Low Priority (Optional)
- **ParameterAnalysis** (`#/parameter-analysis`) - Analytics
- **ParameterNetwork** (`#/parameter-network`) - Visualization

## 🔧 Setup Instructions

### Step 1: Verify Prerequisites

```bash
# Check Node.js version (must be >= 14)
node --version

# Check if Chrome/Chromium is installed
which google-chrome
# or
which chromium-browser

# Verify frontend server is running
curl -s http://localhost:5173 > /dev/null && echo "✅ Frontend OK"

# Verify backend server is running
curl -s http://127.0.0.1:5001 > /dev/null && echo "✅ Backend OK"
```

### Step 2: Install Dependencies

```bash
cd /Users/mckenzie/Documents/event2table/frontend/tests/performance
npm install
```

Required packages:
- `chrome-launcher` (v1.1.2) - Launches headless Chrome
- `chrome-remote-interface` (v0.33.0) - CDP client library

### Step 3: Start Development Servers

```bash
# Terminal 1: Start backend
cd /Users/mckenzie/Documents/event2table
python web_app.py

# Terminal 2: Start frontend
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev

# Terminal 3: Run performance tests
cd /Users/mckenzie/Documents/event2table/frontend/tests/performance
node event2table-performance-test.js
```

## 🚀 Running Tests

### Option 1: Run All Tests (Recommended)

```bash
node event2table-performance-test.js
```

**Output:**
- Console summary with results
- JSON report: `results/performance-report-{timestamp}.json`
- HTML report: `results/performance-report-{timestamp}.html`

### Option 2: Test Single Page

```bash
node cdp-performance-measurer.js http://localhost:5173
node cdp-performance-measurer.js http://localhost:5173 > results/dashboard.json
```

### Option 3: Using Bash Script

```bash
bash run-cdp-performance-test.sh
```

## 📈 Understanding Results

### Performance Score (0-100)

Calculated based on:
- Load Time (30% weight)
- First Contentful Paint (25% weight)
- Largest Contentful Paint (25% weight)
- Resource Count (10% weight)
- Total Blocking Time (10% weight)

**Scoring:**
- 90-100: Excellent (✅ PASSED)
- 75-89: Good (⚠️ WARNING)
- < 75: Needs Improvement (❌ FAILED)

### Key Metrics Explained

#### Load Time
**What it measures**: Time from navigation start to page load complete
**Target**: < 2000ms
**Impact**: User perception of speed

#### First Contentful Paint (FCP)
**What it measures**: Time when first content is rendered
**Target**: < 1800ms
**Impact**: Perceived loading speed

#### Largest Contentful Paint (LCP)
**What it measures**: Time when main content is rendered
**Target**: < 2500ms
**Impact**: Core content visibility

#### Resource Count
**What it measures**: Number of resources loaded
**Target**: < 50
**Impact**: Network overhead

#### Memory Usage
**What it measures**: JavaScript heap size
**Target**: < 100MB
**Impact**: Browser stability

## 🎯 Optimization Strategies

### 1. Code Splitting

**Problem**: Large JavaScript bundles slow down page load

**Solution**:
```javascript
// Instead of direct import
import Dashboard from './pages/Dashboard';

// Use React.lazy()
const Dashboard = React.lazy(() => import('./pages/Dashboard'));

// Wrap with Suspense
<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

**Expected Impact**: 20-30% reduction in load time

### 2. Image Optimization

**Problem**: Unoptimized images increase load time

**Solution**:
```javascript
// Use next/image or react-image
import Image from 'next/image';

<Image
  src="/logo.png"
  width={200}
  height={100}
  loading="lazy"
  placeholder="blur"
/>
```

**Expected Impact**: 10-15% reduction in load time

### 3. CSS Optimization

**Problem**: Render-blocking CSS delays FCP

**Solution**:
```css
/* Inline critical CSS */
<style>
  /* Critical path CSS */
  .header { ... }
  .main-content { ... }
</style>

/* Defer non-critical CSS */
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

**Expected Impact**: 5-10% improvement in FCP

### 4. API Optimization

**Problem**: Multiple API calls slow down page load

**Solution**:
```javascript
// Use React Query for caching and batching
import { useQuery } from '@tanstack/react-query';

const { data } = useQuery({
  queryKey: ['games'],
  queryFn: fetchGames,
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
});
```

**Expected Impact**: 15-25% reduction in API time

### 5. Component Memoization

**Problem**: Unnecessary re-renders slow down interactions

**Solution**:
```javascript
// Use React.memo()
const ExpensiveComponent = React.memo(({ data }) => {
  // Expensive computation
  return <div>{processData(data)}</div>
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.data.id === nextProps.data.id;
});
```

**Expected Impact**: 10-20% improvement in TTI

### 6. Virtual Scrolling

**Problem**: Long lists cause performance issues

**Solution**:
```javascript
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={10000}
  itemSize={35}
  width="100%"
>
  {Row}
</FixedSizeList>
```

**Expected Impact**: 50-70% improvement in large list rendering

## 📊 Page-Specific Recommendations

### Dashboard

**Current Issues**:
- Multiple data fetching calls
- Large component tree
- No lazy loading

**Recommendations**:
1. Implement React Query for data caching
2. Lazy load chart components
3. Add skeleton screens
4. Optimize chart rendering

**Priority**: HIGH
**Expected Improvement**: 30-40%

### Canvas

**Current Issues**:
- Complex node rendering
- No virtualization
- Expensive drag-and-drop

**Recommendations**:
1. Implement canvas virtualization
2. Use React.memo() for nodes
3. Debounce drag events
4. Optimize rendering with requestAnimationFrame

**Priority**: CRITICAL
**Expected Improvement**: 40-50%

### EventNodeBuilder

**Current Issues**:
- Large form handling
- No debouncing
- Synchronous validation

**Recommendations**:
1. Implement debounced validation
2. Use controlled components
3. Optimize form state management
4. Add loading states

**Priority**: CRITICAL
**Expected Improvement**: 25-35%

### Games/Events/Parameters Lists

**Current Issues**:
- No pagination
- No virtualization
- Large data sets

**Recommendations**:
1. Implement server-side pagination
2. Add virtual scrolling
3. Use React Query caching
4. Add infinite scroll

**Priority**: HIGH
**Expected Improvement**: 50-60%

## 🔄 Continuous Monitoring

### Setting Up Scheduled Tests

```bash
# Add to crontab (crontab -e)
# Run performance tests daily at 2 AM
0 2 * * * cd /Users/mckenzie/Documents/event2table/frontend/tests/performance && node event2table-performance-test.js

# Run weekly on Sunday at 3 AM
0 3 * * 0 cd /Users/mckenzie/Documents/event2table/frontend/tests/performance && node event2table-performance-test.js
```

### Tracking Performance Trends

```bash
# Create results archive
mkdir -p results/archive

# Archive results after each test
cp results/performance-report-*.json results/archive/

# Analyze trends
node analyze-trends.js results/archive/
```

### Alerting

```javascript
// Add to CI/CD pipeline
const results = await runAllTests();

if (results.summary.failed > 0) {
  // Send alert (Slack, email, etc.)
  await sendAlert({
    type: 'PERFORMANCE_REGRESSION',
    failed: results.summary.failed,
    pages: results.pages.filter(p => p.status === 'FAILED')
  });

  // Fail the build
  process.exit(1);
}
```

## 📝 Reporting

### Daily Performance Summary

```bash
# Generate daily summary
node generate-summary.js --period daily

# Output:
# - Average load time
# - Pages with regression
# - Pages with improvement
# - Trend comparison
```

### Weekly Performance Report

```bash
# Generate weekly report
node generate-report.js --period weekly --format html

# Output:
# - Detailed metrics per page
# - Comparison with previous week
# - Optimization impact
# - Recommendations
```

### Monthly Executive Summary

```bash
# Generate executive summary
node generate-executive-summary.js --period monthly

# Output:
# - Overall performance score
# - Key improvements
# - Critical issues
# - ROI of optimizations
```

## 🎓 Best Practices

### 1. Test Before Deploy
```bash
# Pre-deploy checklist
npm run test:performance
npm run test:e2e
npm run build
```

### 2. Monitor in Production
```javascript
// Add to production build
if (process.env.NODE_ENV === 'production') {
  // Collect real user metrics
  import('./web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
    getCLS(console.log);
    getFID(console.log);
    getFCP(console.log);
    getLCP(console.log);
    getTTFB(console.log);
  });
}
```

### 3. Set Performance Budgets
```javascript
// In package.json
{
  "scripts": {
    "test:performance": "node event2table-performance-test.js --budget",
    "budget": {
      "loadTime": 2000,
      "fcp": 1800,
      "lcp": 2500
    }
  }
}
```

### 4. Regular Optimization Sprints
- Monthly performance review
- Quarterly optimization sprint
- Annual technical debt cleanup

## 🔍 Troubleshooting

### Issue: Chrome Not Found

```bash
# macOS
brew install --cask google-chrome

# Linux
sudo apt-get install chromium-browser

# Windows
# Download from https://www.chrome.com
```

### Issue: Port Already in Use

```bash
# Find process using port 5173
lsof -ti:5173

# Kill process
kill -9 $(lsof -ti:5173)

# Or use different port
export PORT=5174
npm run dev
```

### Issue: Timeout Errors

```bash
# Increase timeout in test script
const CONFIG = {
  timeout: 60000, // Increase from 30000
};
```

### Issue: Inconsistent Results

```bash
# Run multiple times and average
for i in {1..5}; do
  node event2table-performance-test.js
done

# Use warm-up runs
node event2table-performance-test.js --warmup 3
```

## 📚 Additional Resources

- [Web Vitals](https://web.dev/vitals/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Performance API](https://developer.mozilla.org/en-US/docs/Web/API/Performance)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Vite Performance](https://vitejs.dev/guide/performance.html)

## 🤝 Support

For questions or issues:
1. Check this guide first
2. Review troubleshooting section
3. Check existing GitHub issues
4. Create new issue with details

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-13
**Maintainer**: Event2Table Development Team
