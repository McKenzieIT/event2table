# Event2Table - Performance Testing Suite

Comprehensive performance testing framework for Event2Table application using Chrome DevTools Protocol (CDP).

## 📋 Overview

This testing suite provides automated performance measurement and optimization recommendations for all key pages in the Event2Table application. It uses Chrome DevTools Protocol to capture real browser metrics including:

- **Page Load Time**: Total time to load the page
- **First Contentful Paint (FCP)**: When first content is rendered
- **Largest Contentful Paint (LCP)**: When main content is rendered
- **Cumulative Layout Shift (CLS)**: Visual stability score
- **First Input Delay (FID)**: Input responsiveness
- **Time to Interactive (TTI)**: When page becomes interactive
- **Total Blocking Time (TBT)**: JavaScript execution blocking time
- **Resource Count**: Number of loaded resources
- **Memory Usage**: JavaScript heap size

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (v14 or higher)
2. **Frontend server** running on `http://localhost:5173`
3. **Backend server** running on `http://127.0.0.1:5001`

### Installation

```bash
# Navigate to performance test directory
cd frontend/tests/performance

# Install dependencies
npm install

# Or install globally
npm install -g chrome-launcher chrome-remote-interface
```

### Running Tests

```bash
# Run all performance tests
npm test

# Or directly with Node.js
node event2table-performance-test.js

# Run CDP tests (bash script)
npm run test:cdp

# Test a single page
node cdp-performance-measurer.js http://localhost:5173
```

## 📊 Test Pages

The following pages are tested:

| Page | Route | Priority | Description |
|------|-------|----------|-------------|
| Dashboard | `#/` | Critical | Main dashboard |
| Canvas | `#/canvas` | Critical | Flow canvas builder |
| EventNodeBuilder | `#/event-node-builder` | Critical | Event node builder |
| Games | `#/games` | High | Games management |
| Events | `#/events` | High | Events list |
| Parameters | `#/parameters` | High | Parameters list |
| Generate | `#/generate` | High | HQL generation |
| FieldBuilder | `#/field-builder` | Medium | Field builder |
| Categories | `#/categories` | Medium | Categories management |
| Flows | `#/flows` | Medium | Flows list |
| HqlManage | `#/hql-manage` | Medium | HQL management |
| ParameterAnalysis | `#/parameter-analysis` | Low | Parameter analysis |
| ParameterNetwork | `#/parameter-network` | Low | Network visualization |

## 📈 Performance Thresholds

### Web Vitals Standards

| Metric | Good | Needs Improvement | Poor |
|--------|------|------------------|------|
| Load Time | < 2000ms | < 4000ms | > 4000ms |
| FCP | < 1800ms | < 3000ms | > 3000ms |
| LCP | < 2500ms | < 4000ms | > 4000ms |
| CLS | < 0.1 | < 0.25 | > 0.25 |
| FID | < 100ms | < 300ms | > 300ms |
| TTI | < 3000ms | < 5000ms | > 5000ms |
| TBT | < 300ms | < 600ms | > 600ms |
| Score | > 90 | > 75 | < 75 |

## 📝 Output Reports

After running tests, you'll find:

1. **JSON Report**: `performance-report-{timestamp}.json`
   - Machine-readable metrics
   - Suitable for CI/CD integration
   - Can be parsed for trend analysis

2. **HTML Report**: `performance-report-{timestamp}.html`
   - Visual dashboard
   - Interactive metrics
   - Optimization recommendations

3. **Console Summary**:
   - Quick overview
   - Priority issues
   - Top performing pages

## 🎯 Optimization Recommendations

The test suite generates specific recommendations for each page:

### Load Time Issues
- Implement code splitting
- Lazy load components
- Optimize images
- Minify CSS/JS
- Enable compression

### FCP/LCP Issues
- Reduce render-blocking resources
- Inline critical CSS
- Preload critical resources
- Optimize critical rendering path

### Memory Issues
- Check for memory leaks
- Use React.memo()
- Implement virtualization
- Clean up subscriptions

### Layout Issues
- Batch DOM operations
- Use CSS transforms
- Reserve space for dynamic content

## 🔧 Configuration

### Modify Pages to Test

Edit `event2table-performance-test.js`:

```javascript
const CONFIG = {
  pages: [
    { name: 'YourPage', path: '/your-path', priority: 'high', description: 'Description' },
    // Add more pages...
  ],
};
```

### Adjust Thresholds

Edit thresholds in the same file:

```javascript
const THRESHOLDS = {
  loadTime: { good: 2000, needsImprovement: 4000 },
  fcp: { good: 1800, needsImprovement: 3000 },
  // Customize as needed...
};
```

## 📚 File Structure

```
frontend/tests/performance/
├── README.md                           # This file
├── package.json                        # Dependencies
├── event2table-performance-test.js     # Main test runner
├── cdp-performance-measurer.js        # CDP measurement tool
├── comprehensive-page-test.mcp.js     # Legacy test script
├── run-cdp-performance-test.sh        # Bash script runner
└── results/                           # Test output directory
    ├── performance-report-{timestamp}.json
    └── performance-report-{timestamp}.html
```

## 🔍 How It Works

### Architecture

```
┌─────────────────────────────────────┐
│   Test Runner (Node.js)             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Chrome Launcher                  │
│   - Launches headless Chrome        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Chrome DevTools Protocol          │
│   - Page.enable()                  │
│   - Performance.enable()            │
│   - Network.enable()               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Page Navigation & Metrics         │
│   - Navigate to URL                │
│   - Wait for load events            │
│   - Collect performance metrics     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Analysis & Reporting              │
│   - Calculate scores                │
│   - Generate recommendations        │
│   - Create reports                 │
└─────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Frontend Not Running

```bash
cd frontend
npm run dev
```

### Backend Not Running

```bash
python web_app.py
```

### Chrome Not Found

```bash
# Install Chrome/Chromium
# macOS
brew install --cask google-chrome

# Ubuntu
sudo apt-get install chromium-browser
```

### Permission Denied

```bash
chmod +x run-cdp-performance-test.sh
```

## 📖 Resources

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Web Vitals](https://web.dev/vitals/)
- [Performance API](https://developer.mozilla.org/en-US/docs/Web/API/Performance)
- [React Performance](https://react.dev/learn/render-and-commit)

## 📄 License

MIT License - Event2Table Development Team

---

**Version**: 1.0.0
**Last Updated**: 2026-02-13
**Maintainer**: Event2Table Development Team
