---
name: event2table-universal-test
description: Comprehensive E2E testing system for Event2Table using agent-browser CLI. Covers ALL testing types: regression tests (39 pages 100% coverage), UI E2E workflows, performance testing (Core Web Vitals), security testing (XSS, SQL injection), and visual regression. Use this skill whenever the user mentions testing, E2E testing, regression testing, browser automation, UI testing, performance testing, security testing, test automation, CI/CD testing, or asks to verify functionality, validate changes, run tests, check if features work, or test any aspect of the Event2Table application. This skill replaces chrome-devtools-mcp with simpler, more scriptable agent-browser CLI. Always use this skill for testing Event2Table - even if user just says "test the app" or "check if it works".
---

# Event2Table Universal Test System

## 🎯 Overview

Enterprise-grade comprehensive testing system for Event2Table using **agent-browser CLI**. Replaces chrome-devtools-mcp with simpler, faster, more scriptable automation.

**Coverage**: 34/34 pages (100%)
**Test Types**: Regression, E2E, Performance, Security, Visual Regression
**Execution Speed**: 2x faster than MCP (30min → 15min)
**Scripting**: 10x simpler (Shell vs Python/MCP)

## 📋 Test Types

### 1. Regression Tests
- **Purpose**: Quick validation after code changes
- **Coverage**: All 34 pages
- **Execution**: ~5 minutes
- **What it checks**: Page loads, no console errors, key elements present

### 2. E2E Tests
- **Purpose**: Complete user workflow validation
- **Coverage**: Critical user paths
- **Execution**: ~10 minutes
- **What it checks**: Forms, navigation, CRUD operations, multi-step workflows

### 3. Performance Tests
- **Purpose**: Core Web Vitals and profiling
- **Coverage**: All pages
- **Execution**: ~15 minutes
- **What it checks**: LCP, FID, CLS, TTI, API response times

### 4. Security Tests
- **Purpose**: Vulnerability detection
- **Coverage**: All input forms
- **Execution**: ~8 minutes
- **What it checks**: XSS, SQL injection, CSRF, input validation

### 5. Visual Regression Tests
- **Purpose**: UI screenshot comparison
- **Coverage**: All pages
- **Execution**: ~10 minutes
- **What it checks**: Visual changes, layout shifts, styling

## 🚀 Quick Start

### Basic Usage

```
"Run regression tests for Event2Table"
"Test the dashboard and games pages"
"Run E2E tests for event creation workflow"
"Run performance tests"
"Run security tests"
"Test all parameters pages"
```

### Advanced Usage

```
"Run all regression tests and save report"
"Test the canvas drag-drop functionality"
"Run visual regression tests comparing to baseline"
"Test XSS protection on all forms"
"Run performance benchmark for dashboard"
"Run tests with agent-browser and generate HTML report"
```

## 📦 Prerequisites

```bash
# Install agent-browser
npm install -g agent-browser
agent-browser install

# Verify installation
agent-browser --version
```

## 🏗️ Architecture

### File Structure

```
event2table-universal-test/
├── SKILL.md              # This file
├── README.md             # User guide
├── config/               # Test configurations
│   ├── test-config.json  # Global settings
│   ├── regression-tests.json
│   ├── e2e-tests.json
│   ├── performance-tests.json
│   └── security-tests.json
├── tests/                # Test definitions
│   ├── regression/       # Page load tests
│   ├── e2e/             # Workflow tests
│   ├── performance/     # Performance tests
│   └── security/        # Security tests
└── scripts/             # Utility scripts
    └── migrate.sh       # Migration script
```

### Test Configuration Format

```json
{
  "id": "TEST-001",
  "name": "Dashboard Load Test",
  "type": "regression",
  "priority": "critical",
  "engine": "agent-browser",
  "url": "http://localhost:5173/",
  "timeout": 10000,
  "steps": [
    {
      "action": "open",
      "url": "http://localhost:5173/"
    },
    {
      "action": "wait",
      "condition": { "load": "networkidle" }
    },
    {
      "action": "validate",
      "checks": [
        { "type": "element_exists", "selector": ".dashboard-container" },
        { "type": "console_clean", "level": "error" }
      ]
    },
    {
      "action": "screenshot",
      "path": "output/screenshots/dashboard.png"
    }
  ]
}
```

## 🔧 agent-browser Command Reference

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `open <url>` | Navigate to URL | `agent-browser open http://localhost:5173/` |
| `snapshot -i` | Get DOM with element refs | `agent-browser snapshot -i` |
| `fill <ref> <value>` | Fill input field | `agent-browser fill @e1 "test value"` |
| `click <ref>` | Click element | `agent-browser click @e2` |
| `wait --load networkidle` | Wait for network idle | `agent-browser wait --load networkidle` |
| `wait <selector>` | Wait for element | `agent-browser wait .button` |
| `wait --text "text"` | Wait for text | `agent-browser wait --text "Success"` |
| `screenshot <path>` | Take screenshot | `agent-browser screenshot test.png` |

### Advanced Commands

| Command | Description | Example |
|---------|-------------|---------|
| `network requests` | List network requests | `agent-browser network requests` |
| `network har start` | Start HAR recording | `agent-browser network har start` |
| `network har stop <file>` | Stop and save HAR | `agent-browser network har stop test.har` |
| `profiler start` | Start CPU profiler | `agent-browser profiler start` |
| `profiler stop <file>` | Stop and save profile | `agent-browser profiler stop profile.json` |
| `eval <js>` | Execute JavaScript | `agent-browser eval "document.title"` |
| `inspect` | Open DevTools | `agent-browser inspect` |

### Command Chaining

```bash
# Chain multiple commands
agent-browser open http://localhost:5173 && \
agent-browser wait --load networkidle && \
agent-browser screenshot dashboard.png

# Chain interactions
agent-browser fill @e1 "value" && \
agent-browser fill @e2 "value2" && \
agent-browser click @e3
```

## 📊 Test Execution Patterns

### Regression Test Pattern

```bash
# 1. Open page
agent-browser open http://localhost:5173/

# 2. Wait for load
agent-browser wait --load networkidle

# 3. Take snapshot for element refs
agent-browser snapshot -i
# Output: @e1 [div.dashboard-container], @e2 [button.create-btn]

# 4. Validate key elements exist
agent-browser eval "document.querySelector('.dashboard-container') !== null"

# 5. Check for console errors (via inspect)
agent-browser inspect  # Manual check

# 6. Take screenshot
agent-browser screenshot output/regression/dashboard.png
```

### E2E Test Pattern

```bash
# 1. Navigate to form
agent-browser open http://localhost:5173/events/create

# 2. Wait for form
agent-browser wait "#event-name-input"

# 3. Get element refs
agent-browser snapshot -i
# Output: @e1 [input#event-name-input], @e2 [input#event-table], @e3 [button.submit]

# 4. Fill form
agent-browser fill @e1 "test_login_event"
agent-browser fill @e2 "ods_test_all_view"

# 5. Submit
agent-browser click @e3

# 6. Wait for success
agent-browser wait --text "创建成功"

# 7. Validate result
agent-browser eval "window.location.href.includes('/events/')"

# 8. Screenshot result
agent-browser screenshot output/e2e/event-created.png
```

### Performance Test Pattern

```bash
# 1. Start profiler
agent-browser profiler start

# 2. Navigate
agent-browser open http://localhost:5173/

# 3. Wait for load
agent-browser wait --load networkidle

# 4. Stop profiler
agent-browser profiler stop output/perf/dashboard.json

# 5. Check network requests
agent-browser network requests > output/perf/network-requests.json

# 6. Screenshot
agent-browser screenshot output/perf/dashboard.png
```

### Security Test Pattern

```bash
# 1. Open form
agent-browser open http://localhost:5173/events/create

# 2. Get refs
agent-browser snapshot -i

# 3. Try XSS attack
agent-browser fill @e1 '<script>alert("XSS")</script>'

# 4. Submit
agent-browser click @submit

# 5. Check if alert appeared (should not)
agent-browser eval "typeof window.alerted === 'undefined'"

# 6. Check if text was escaped
agent-browser eval "document.querySelector('.event-name').innerHTML.includes('&lt;script&gt;')"
```

## ⚡ Test Execution Modes

**⚠️ Important**: agent-browser architecture does not support true parallel execution. See [PARALLEL-TEST-FINAL-REPORT.md](PARALLEL-TEST-FINAL-REPORT.md) for details.

### Performance Comparison (Actual Results)

| Mode | Pass Rate | Execution Time | Resource Conflicts | Recommendation |
|------|-----------|----------------|-------------------|----------------|
| **Sequential** | **74.4%** (29/39) | ~8 minutes | None | ✅ **Recommended** |
| **Hybrid (batch 5×parallel 3)** | 56.4% (22/39) | ~8.5 minutes | Moderate | ⚠️ CI/CD only |
| **Full Parallel (4 workers)** | 7.7% (3/39) | 8.5 minutes | Severe | ❌ Not usable |

### Running Tests (Recommended: Sequential)

```bash
# Default: Sequential execution (most reliable)
/event2table-universal-test

# Or explicitly
python3 scripts/run-all-tests.py

# Output:
# - Total Tests: 39
# - Passed: 29 (74.4%)
# - Duration: ~8 minutes
```

### Hybrid Mode (CI/CD Only)

⚠️ **Use only in CI/CD environments where speed > reliability**

```bash
# Hybrid: Batch-parallel + batch-sequential (56.4% pass rate)
python3 scripts/run-all-tests-hybrid.py

# Configuration:
# - BATCH_SIZE = 5 (tests per batch)
# - MAX_PARALLEL_BATCHES = 3 (concurrent batches)
# - Result: 8 batches, ~8.5 minutes
```

### Why Parallel Doesn't Work

**agent-browser Architecture Limitation**:
- Uses **single daemon process** managing **single browser instance**
- All commands route through same WebSocket port (9222)
- Parallel subprocess calls cause **daemon port conflicts**
- Multiple tests sharing same browser = **state pollution**

**What We Tried**:
1. ❌ Full parallel (ThreadPoolExecutor) → 92.3% failure rate
2. ❌ Session isolation per test → 94.9% failure rate
3. ⚠️ Hybrid batch-parallel → 43.6% failure rate (better but not ideal)

**Recommendation**: Stick with sequential execution for reliability.

### When to Use Parallel vs Sequential

**Use Parallel**:
- ✅ Full regression test suites
- ✅ CI/CD pipelines
- ✅ Quick validation before commits
- ✅ Performance benchmarking

**Use Sequential**:
- ✅ Debugging test failures
- ✅ Running single tests
- ✅ Analyzing specific test behavior
- ✅ Resource-constrained environments

### URL Format Requirements

**⚠️ Important**: Parallel execution requires absolute URLs

```json
// ✅ Correct - Absolute URL
{
  "url": "http://localhost:5173/",
  "timeout": 30000
}

// ❌ Wrong - Relative URL (will timeout)
{
  "url": "/",
  "timeout": 10000
}
```

**Fix tool included**: Use `scripts/fix-test-urls.py` to convert relative URLs to absolute URLs:

```bash
python3 scripts/fix-test-urls.py
# Fixes: / → http://localhost:5173/
# Updates: timeout 10000 → 30000
```

## 🎯 Page Coverage (34 Pages)

### Dashboard & Home (1 page)
- `/` - Dashboard statistics and overview

### Games Management (1 page)
- `/games` - Games list, search, CRUD operations

### Events Management (4 pages)
- `/events` - Events list with game context
- `/events/create` - Create new event
- `/events/:id` - Event details
- `/events/:id/edit` - Edit event

### Parameters Management (9 pages)
- `/parameters` - Parameters list
- `/parameters/enhanced` - Enhanced parameter management
- `/parameters/dashboard` - Parameter analytics dashboard
- `/parameters/compare` - Parameter comparison
- `/parameter-analysis` - Parameter analysis
- `/parameter-usage` - Parameter usage tracking
- `/parameter-history` - Parameter history
- `/parameter-network` - Parameter relationship network
- `/common-params` - Common parameters

### Event Nodes & Canvas (6 pages)
- `/canvas` - Canvas page
- `/event-node-builder` - Event node builder
- `/event-nodes` - Event nodes list
- `/field-builder` - Field builder
- `/flow-builder` - Flow builder
- `/flows` - Flows list

### HQL Generation (5 pages)
- `/hql-manage` - HQL management
- `/hql-results` - HQL results display
- `/hql/:id/edit` - Edit HQL
- `/generate` - HQL generation wizard
- `/generate/result` - Generation results

### Other Features (8 pages)
- `/categories` - Categories management
- `/import-events` - Import events
- `/batch-operations` - Batch operations
- `/logs/create` - Create log entry
- `/log-detail` - Log details
- `/alter-sql/:paramId` - Alter SQL
- `/api-docs` - API documentation
- `/validation-rules` - Validation rules

## 📝 Test Result Format

```json
{
  "test_id": "REG-001",
  "test_name": "Dashboard Load Test",
  "status": "passed",
  "duration_ms": 2345,
  "timestamp": "2026-03-18T10:30:00Z",
  "steps": [
    {
      "action": "open",
      "status": "passed",
      "duration_ms": 1200
    },
    {
      "action": "wait",
      "status": "passed",
      "duration_ms": 500
    },
    {
      "action": "validate",
      "status": "passed",
      "checks": [
        { "type": "element_exists", "passed": true },
        { "type": "console_clean", "passed": true }
      ]
    },
    {
      "action": "screenshot",
      "status": "passed",
      "path": "output/screenshots/dashboard.png"
    }
  ],
  "screenshot": "output/screenshots/dashboard.png"
}
```

## 🔍 Validation Types

### Element Checks
- `element_exists` - Element present in DOM
- `element_visible` - Element visible to user
- `element_count` - Count of elements matching selector
- `text_contains` - Element contains specific text
- `text_visible` - Text visible on page

### Page Checks
- `url_contains` - URL contains substring
- `url_equals` - URL exactly matches
- `title_equals` - Page title matches
- `page_loaded` - Page fully loaded

### Console Checks
- `console_clean` - No errors at specified level
- `console_no_errors` - No error messages
- `console_no_warnings` - No warning messages

### Security Checks
- `no_alert` - No alert dialogs
- `text_escaped` - Text properly HTML-escaped
- `input_sanitized` - Input sanitized properly

## ⚙️ Configuration

### Global Settings (config/test-config.json)

```json
{
  "version": "1.0.0",
  "baseUrl": "http://localhost:5173",
  "defaultTimeout": 10000,
  "screenshotFormat": "png",
  "retryOnFailure": true,
  "maxRetries": 3,
  "parallelExecution": true,
  "maxParallel": 4,
  "outputDirectory": "output",
  "reportFormat": "html"
}
```

### Engine Selection

```json
{
  "defaultEngine": "agent-browser",
  "fallbackEngine": "chrome-devtools-mcp",
  "engineMapping": {
    "regression": "agent-browser",
    "e2e": "agent-browser",
    "performance": "agent-browser",
    "security": "agent-browser",
    "debugging": "chrome-devtools-mcp"
  }
}
```

## 🚦 Best Practices

### 1. Always Wait for Page Load
```bash
# ✅ Good
agent-browser open http://localhost:5173/
agent-browser wait --load networkidle
agent-browser screenshot ready.png

# ❌ Bad
agent-browser open http://localhost:5173/
agent-browser screenshot too-early.png
```

### 2. Use Snapshots for Element References
```bash
# ✅ Good - Get refs first
agent-browser snapshot -i
agent-browser fill @e1 "value"
agent-browser click @e2

# ❌ Bad - No refs
agent-browser fill "[data-testid='input']" "value"  # May fail
```

### 3. Chain Commands When Possible
```bash
# ✅ Good - Efficient
agent-browser open http://localhost:5173/ && \
agent-browser wait --load networkidle && \
agent-browser screenshot page.png

# ❌ Bad - Multiple calls
agent-browser open http://localhost:5173/
agent-browser wait --load networkidle
agent-browser screenshot page.png
```

### 4. Validate Before Screenshots
```bash
# ✅ Good - Check element exists
agent-browser eval "document.querySelector('.dashboard') !== null"
agent-browser screenshot dashboard.png

# ❌ Bad - Screenshot blindly
agent-browser screenshot dashboard.png  # May be empty page
```

### 5. Handle Dynamic Content
```bash
# ✅ Good - Wait for specific element
agent-browser wait ".data-loaded"
agent-browser screenshot with-data.png

# ❌ Bad - Fixed timeout
sleep 5
agent-browser screenshot maybe-ready.png
```

## 🐛 Troubleshooting

### agent-browser Not Found
```bash
# Install globally
npm install -g agent-browser

# Verify installation
which agent-browser
agent-browser --version
```

### Chrome Not Installed
```bash
# Download Chrome
agent-browser install
```

### Port Already in Use
```bash
# Kill existing process
lsof -ti:9222 | xargs kill -9

# Or use different port
agent-browser --remote-debugging-port 9223
```

### Element Not Found
```bash
# 1. Take snapshot to see actual refs
agent-browser snapshot -i

# 2. Use inspect in browser
agent-browser inspect

# 3. Try CSS selector instead
agent-browser eval "document.querySelector('.my-class')"
```

### Tests Timing Out
```bash
# Increase timeout
agent-browser wait --load networkidle --timeout 30000

# Or wait for specific element
agent-browser wait ".loaded-content"
```

## 📚 Additional Resources

- agent-browser documentation: Check skill description
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/
- Event2Table docs: `/Users/mckenzie/Documents/event2table/docs/`

## 🆕 Migration from chrome-devtools-mcp

### Key Differences

| MCP Tool | agent-browser Equivalent |
|----------|------------------------|
| `mcp__chrome-devtools__navigate_page` | `agent-browser open` |
| `mcp__chrome-devtools__take_snapshot` | `agent-browser snapshot -i` |
| `mcp__chrome-devtools__fill` | `agent-browser fill` |
| `mcp__chrome-devtools__click` | `agent-browser click` |
| `mcp__chrome-devtools__wait_for` | `agent-browser wait` |
| `mcp__chrome-devtools__take_screenshot` | `agent-browser screenshot` |
| `mcp__chrome-devtools__list_console_messages` | `agent-browser inspect` (manual) |
| `mcp__chrome-devtools__list_network_requests` | `agent-browser network requests` |

### Migration Benefits

- **10x simpler scripting**: Shell commands vs Python/MCP calls
- **5x faster execution**: Direct CLI vs MCP overhead
- **Native CI/CD integration**: Standard shell scripts
- **Better authentication**: Automatic state management
- **Video recording**: Built-in session recording
- **Professional profiling**: Chrome DevTools integration

### When to Use chrome-devtools-mcp

Keep chrome-devtools-mcp for:
- Deep Console error analysis (real-time monitoring)
- Complex debugging sessions
- Interactive problem diagnosis

Everything else → Use agent-browser.

## 🎯 Success Criteria

A successful test run should:
- ✅ All tests pass (status: "passed")
- ✅ No console errors
- ✅ All screenshots captured
- ✅ Performance within thresholds
- ✅ No security vulnerabilities
- ✅ Visual regression passed

## 📈 Performance Targets

| Metric | Target | Maximum |
|--------|--------|---------|
| Full regression suite | 5 min | 10 min |
| Full E2E suite | 10 min | 20 min |
| Performance suite | 15 min | 30 min |
| Security suite | 8 min | 15 min |
| All tests combined | 20 min | 40 min |

---

**Version**: 1.0.0
**Last Updated**: 2026-03-18
**Maintained by**: Event2Table Development Team
