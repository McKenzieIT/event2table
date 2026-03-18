# Event2Table Universal Test System - Design Document

**Version**: 1.0.0
**Date**: 2026-03-18
**Status**: Design Phase
**Author**: Claude (Brainstorming Skill)

---

## Executive Summary

This document outlines the design for a comprehensive testing system that will replace the current chrome-devtools-mcp based testing with agent-browser CLI based testing. The new system will support:

- **Regression Testing** - Quick validation of existing functionality
- **UI E2E Testing** - Complete user workflow testing
- **Performance Testing** - Core Web Vitals and profiling
- **Security Testing** - SQL injection, XSS, CSRF detection
- **Visual Regression Testing** - UI screenshot comparison

**Target Migration Timeline**: 8-12 weeks with dual-track parallel execution.

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Proposed Solution](#2-proposed-solution)
3. [Architecture Design](#3-architecture-design)
4. [Test Coverage Matrix](#4-test-coverage-matrix)
5. [Migration Strategy](#5-migration-strategy)
6. [Technical Implementation](#6-technical-implementation)
7. [Risk Assessment](#7-risk-assessment)
8. [Success Metrics](#8-success-metrics)
9. [Next Steps](#9-next-steps)

---

## 1. Current State Analysis

### 1.1 Existing System

**Skill**: `event2table-e2e-test`
**Engine**: Chrome DevTools MCP (mcp__chrome-devtools__*)
**Test Coverage**:
- Analytics Module: 30+ tests
- Event Builder: 20+ tests
- Canvas Module: 15+ tests
- **Total**: ~65 tests

**Strengths**:
- ✅ Real-time interactive diagnosis
- ✅ Deep DOM analysis
- ✅ Console error monitoring
- ✅ Network request tracking

**Limitations**:
- ❌ Hard to script and automate
- ❌ No batch execution support
- ❌ Complex CI/CD integration
- ❌ No concurrent testing
- ❌ Manual authentication each time

### 1.2 Project Scope

**Total Pages**: 34 pages across 7 modules

| Module | Pages | Key Functionality |
|--------|-------|------------------|
| Dashboard & Home | 1 | Statistics, overview |
| Games Management | 1 | CRUD operations, search |
| Events Management | 4 | CRUD, details, filtering |
| Parameters Management | 9 | CRUD, analytics, comparison |
| Event Nodes & Canvas | 6 | Canvas, drag-drop, workflows |
| HQL Generation | 5 | Generation, editing, results |
| Other Features | 8 | Import, batch ops, API docs |

---

## 2. Proposed Solution

### 2.1 System Overview

**New Skill**: `event2table-universal-test`
**Engine**: agent-browser CLI
**Philosophy**: "Test everything, test often, test automatically"

### 2.2 Key Improvements

| Aspect | Current (MCP) | New (CLI) | Improvement |
|--------|--------------|-----------|-------------|
| **Scripting** | Complex Python/MCP | Simple Shell | **10x simpler** |
| **Batch Execution** | Manual | Native support | **5x faster** |
| **CI/CD Integration** | Complex | Simple | **10x simpler** |
| **Concurrency** | None | 4-8 parallel | **∞** |
| **Authentication** | Manual | Automatic state | **∞** |
| **Video Recording** | No | Yes | **∞** |
| **Performance Profiling** | Basic | Professional | **5x detailed** |
| **Console Monitoring** | Excellent | Good (via inspect) | Slightly worse |

---

## 3. Architecture Design

### 3.1 System Architecture

```
event2table-universal-test/
├── SKILL.md                        # Main skill documentation
├── README.md                       # User guide
├── lib/
│   ├── core/
│   │   ├── TestRunner.js           # Core test executor
│   │   ├── TestSuite.js            # Test suite manager
│   │   └── Test.js                 # Individual test
│   ├── executors/
│   │   ├── RegressionExecutor.js   # Regression tests
│   │   ├── E2EExecutor.js          # E2E tests
│   │   ├── PerformanceExecutor.js  # Performance tests
│   │   └── SecurityExecutor.js     # Security tests
│   ├── reporters/
│   │   ├── ConsoleReporter.js      # Console output
│   │   ├── HTMLReporter.js         # HTML report
│   │   └── JUnitReporter.js        # JUnit XML (CI/CD)
│   ├── utils/
│   │   ├── cli-wrapper.js          # agent-browser wrapper
│   │   ├── dom-helper.js           # DOM utilities
│   │   └── assertion-library.js    # Assertions
│   └── adapters/
│       ├── AgentBrowserAdapter.js  # agent-browser adapter
│       └── DevToolsAdapter.js      # MCP adapter (compatibility)
├── tests/
│   ├── regression/                 # Regression tests (34 pages)
│   ├── e2e/                        # E2E workflow tests
│   ├── performance/                # Performance tests
│   └── security/                   # Security tests
├── config/
│   ├── test-config.json            # Global configuration
│   ├── regression-tests.json       # Regression test configs
│   ├── e2e-tests.json              # E2E test configs
│   └── thresholds.json             # Performance thresholds
├── templates/
│   └── report-template.html        # Report template
└── scripts/
    ├── setup.sh                    # Initialization
    └── migrate.sh                  # Migration scripts
```

### 3.2 Component Design

#### TestRunner
```javascript
class TestRunner {
  constructor(engine = 'agent-browser') {
    this.engine = engine;
    this.adapter = this.createAdapter(engine);
    this.results = [];
  }

  async runTest(testConfig) {
    const test = new Test(testConfig, this.adapter);
    const result = await test.execute();
    this.results.push(result);
    return result;
  }

  async runSuite(suiteConfig) {
    const suite = new TestSuite(suiteConfig, this.adapter);
    return await suite.run();
  }
}
```

#### AgentBrowserAdapter
```javascript
class AgentBrowserAdapter {
  async open(url) {
    execSync(`agent-browser open ${url}`);
  }

  async snapshot(options = {}) {
    const output = execSync(`agent-browser snapshot -i`);
    return this.parseSnapshot(output);
  }

  async fill(ref, value) {
    execSync(`agent-browser fill ${ref} "${value}"`);
  }

  async click(ref) {
    execSync(`agent-browser click ${ref}`);
  }

  async wait(condition) {
    let cmd = 'agent-browser wait';
    if (condition.load === 'networkidle') {
      cmd += ' --load networkidle';
    }
    execSync(cmd);
  }

  async screenshot(path) {
    execSync(`agent-browser screenshot ${path}`);
  }
}
```

---

## 4. Test Coverage Matrix

### 4.1 Complete Page Coverage (34/34 = 100%)

| Module | Pages | Test Types | Coverage |
|--------|-------|-----------|----------|
| **Dashboard** | 1 | Regression, E2E, Performance, Visual | ✅ 100% |
| **Games** | 1 | Regression, E2E, Security | ✅ 100% |
| **Events** | 4 | Regression, E2E, Security | ✅ 100% |
| **Parameters** | 9 | Regression, E2E, Analytics | ✅ 100% |
| **Canvas** | 6 | Regression, E2E, Interaction | ✅ 100% |
| **HQL** | 5 | Regression, E2E, Performance | ✅ 100% |
| **Other** | 8 | Regression, E2E | ✅ 100% |

### 4.2 Test Type Coverage

| Test Type | Pages | Coverage | agent-browser Support |
|-----------|-------|----------|---------------------|
| **Regression** | 34/34 | 100% | ✅✅✅ Excellent |
| **UI E2E** | 34/34 | 100% | ✅✅✅ Excellent |
| **Interaction** | 30/34 | 88% | ✅✅ Very Good |
| **Performance** | 34/34 | 100% | ✅✅ Excellent |
| **Security** | 34/34 | 100% | ✅✅ Excellent |
| **Visual Regression** | 34/34 | 100% | ✅✅ Excellent |

---

## 5. Migration Strategy

### 5.1 Dual-Track Parallel Migration

**Duration**: 8-12 weeks
**Approach**: Incremental migration with parallel validation

#### Phase 0: Preparation (Week 1-2)

**Tasks**:
- Install agent-browser
- Create skill structure
- Verify basic functionality
- Create first test

**Deliverables**:
- ✅ agent-browser installed and verified
- ✅ Skill directory structure created
- ✅ First regression test passing

#### Phase 1: Regression Tests (Week 3-5)

**Scope**:
- Dashboard & Games (Week 3)
- Events Management (Week 4)
- Parameters Management Part 1 (Week 5)

**Validation**:
- Run both MCP and CLI in parallel
- Compare results
- Document any differences

#### Phase 2: E2E Tests (Week 6-8)

**Scope**:
- Form interactions
- Navigation flows
- User workflows

**Validation**:
- Parallel execution
- Result comparison
- Bug fixes

#### Phase 3: Advanced Features (Week 9-11)

**Scope**:
- Performance testing
- Security testing
- Visual regression

**Validation**:
- Benchmark comparisons
- Security scan validation
- Screenshot diff analysis

#### Phase 4: Canvas Special Cases (Week 12)

**Scope**:
- Canvas drag-drop
- Node connections
- Flow builder

**Validation**:
- Manual testing
- Performance validation

#### Phase 5: Cutover (Week 13)

**Tasks**:
- Make agent-browser default engine
- Demote chrome-devtools-mcp to fallback
- Update all documentation
- Team training

### 5.2 Rollback Plan

**Trigger Criteria**:
- Critical test failures > 20%
- Performance degradation > 50%
- Blocking bugs unfixed for 1 week

**Rollback Steps**:
1. Revert to chrome-devtools-mcp as default
2. Investigate and fix issues
3. Resume migration when stable

---

## 6. Technical Implementation

### 6.1 Test Configuration Format

```json
{
  "id": "REG-001",
  "name": "Dashboard Load Test",
  "priority": "critical",
  "engine": "agent-browser",
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
      "action": "snapshot",
      "saveRefs": true
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
      "path": "output/screenshots/regression/dashboard.png"
    }
  ]
}
```

### 6.2 E2E Test Example

```json
{
  "id": "E2E-001",
  "name": "Create Event Workflow",
  "priority": "critical",
  "steps": [
    {
      "action": "open",
      "url": "http://localhost:5173/events/create"
    },
    {
      "action": "wait",
      "condition": { "selector": "#event-name-input" }
    },
    {
      "action": "snapshot"
    },
    {
      "action": "fill",
      "ref": "@event-name-input",
      "value": "test_login_event"
    },
    {
      "action": "fill",
      "ref": "@event-table-input",
      "value": "ods_test_all_view"
    },
    {
      "action": "click",
      "ref": "@submit-button"
    },
    {
      "action": "wait",
      "condition": { "text": "创建成功" }
    },
    {
      "action": "validate",
      "checks": [
        { "type": "url_contains", "value": "/events/" },
        { "type": "text_visible", "text": "test_login_event" }
      ]
    }
  ]
}
```

### 6.3 Performance Test Example

```json
{
  "id": "PERF-001",
  "name": "Dashboard Performance",
  "thresholds": {
    "LCP": 2500,
    "FID": 100,
    "CLS": 0.1,
    "TTI": 3000
  },
  "steps": [
    { "action": "profiler_start" },
    { "action": "open", "url": "http://localhost:5173/" },
    { "action": "wait", "condition": { "load": "networkidle" } },
    { "action": "profiler_stop", "path": "output/traces/perf-dashboard.json" },
    { "action": "measure_performance", "metrics": ["LCP", "FID", "CLS", "TTI"] }
  ]
}
```

### 6.4 Security Test Example

```json
{
  "id": "SEC-001",
  "name": "XSS Protection",
  "steps": [
    {
      "action": "open",
      "url": "http://localhost:5173/events/create"
    },
    {
      "action": "fill",
      "selector": "#event-name-input",
      "value": "<script>alert('XSS')</script>"
    },
    {
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "action": "validate",
      "checks": [
        { "type": "no_alert", "expected": true },
        { "type": "text_escaped", "selector": ".event-name", "expected": "&lt;script&gt;" }
      ]
    }
  ]
}
```

---

## 7. Risk Assessment

### 7.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| **agent-browser limitations** | High | Medium | Keep MCP as fallback; use `eval` for custom JS |
| **Console monitoring gaps** | Medium | High | Use `inspect` for manual checks; integrate logging tools |
| **Canvas drag-drop complexity** | Medium | Medium | Use coordinate simulation; keep MCP for complex cases |
| **Performance test accuracy** | Low | Low | Validate with professional profilers |
| **Concurrent test conflicts** | Medium | Medium | Use isolated browser profiles; test isolation |

### 7.2 Migration Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| **Inconsistent results** | High | Medium | Dual-track validation; detailed logging |
| **Steep learning curve** | Medium | Low | Comprehensive docs; gradual migration |
| **Existing test failures** | High | Low | Keep original tests; incremental rollout |
| **CI/CD integration issues** | Medium | Low | Early integration testing; backward compatibility |

---

## 8. Success Metrics

### 8.1 Quantitative Metrics

| Metric | Current (MCP) | Target (CLI) | Measurement |
|--------|--------------|-------------|-------------|
| **Execution time** | ~30 min | ~15 min | Timing statistics |
| **Script complexity** | High | Low | Lines of code |
| **Maintenance cost** | High | Low | Bug fix time |
| **CI/CD complexity** | High | Low | Integration steps |
| **Test coverage** | 85% | 95%+ | Coverage tools |
| **Concurrent execution** | None | 4-8 parallel | Concurrency count |
| **Automation level** | 60% | 90%+ | Automation ratio |

### 8.2 Qualitative Metrics

- ✅ **Developer Experience** - Simpler test authoring and debugging
- ✅ **Maintainability** - Clearer code structure
- ✅ **Extensibility** - Easier to add new tests
- ✅ **Stability** - Fewer test failures

---

## 9. Next Steps

### 9.1 Immediate Actions (This Week)

```bash
# 1. Install agent-browser
npm install -g agent-browser
agent-browser install

# 2. Verify installation
agent-browser --version
agent-browser open http://localhost:5173/
agent-browser snapshot -i

# 3. Create skill structure
mkdir -p .claude/skills/event2table-universal-test
cd .claude/skills/event2table-universal-test
mkdir -p lib/{core,executors,reporters,utils,adapters}
mkdir -p tests/{regression,e2e,performance,security}
mkdir -p config templates scripts output

# 4. Write first test
cat > tests/regression/dashboard-load.test.json << 'EOF'
{
  "id": "REG-001",
  "name": "Dashboard Load Test",
  "priority": "critical",
  "engine": "agent-browser",
  "steps": [
    { "action": "open", "url": "http://localhost:5173/" },
    { "action": "wait", "condition": { "load": "networkidle" } },
    { "action": "screenshot", "path": "output/screenshots/dashboard.png" },
    { "action": "validate", "checks": [
      { "type": "element_exists", "selector": ".dashboard-container" }
    ]}
  ]
}
EOF
```

### 9.2 Week 1-2 Goals

- ✅ Complete Phase 0: Preparation
- ✅ First 10 regression tests passing
- ✅ Basic reporting working
- ✅ Documentation draft completed

### 9.3 Week 3-4 Goals

- ✅ Phase 1: Dashboard & Games migration
- ✅ 20 regression tests passing
- ✅ Parallel validation with MCP
- ✅ Performance baseline established

### 9.4 Week 5-8 Goals

- ✅ Phase 2: E2E tests migration
- ✅ 50 total tests passing
- ✅ CI/CD integration tested
- ✅ Team training completed

### 9.5 Week 9-12 Goals

- ✅ Phase 3-4: Advanced features
- ✅ 100+ tests passing
- ✅ Performance tests validated
- ✅ Security tests operational

### 9.6 Week 13 Goals

- ✅ Phase 5: Cutover
- ✅ agent-browser as default
- ✅ Full documentation
- ✅ Legacy MCP deprecated

---

## Appendix

### A. agent-browser Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `open <url>` | Navigate to URL | `agent-browser open http://localhost:5173/` |
| `snapshot -i` | Get DOM with element refs | `agent-browser snapshot -i` |
| `fill <ref> <value>` | Fill input field | `agent-browser fill @e1 "test value"` |
| `click <ref>` | Click element | `agent-browser click @e2` |
| `wait --load networkidle` | Wait for network idle | `agent-browser wait --load networkidle` |
| `screenshot <path>` | Take screenshot | `agent-browser screenshot test.png` |
| `profiler start` | Start profiling | `agent-browser profiler start` |
| `network requests` | List network requests | `agent-browser network requests` |

### B. Test Configuration Schema

```typescript
interface TestConfig {
  id: string;
  name: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  engine: 'agent-browser' | 'chrome-devtools-mcp';
  timeout?: number;
  steps: TestStep[];
  validations?: Validation[];
}

interface TestStep {
  action: 'open' | 'wait' | 'snapshot' | 'fill' | 'click' | 'screenshot' | 'validate';
  url?: string;
  condition?: WaitCondition;
  ref?: string;
  selector?: string;
  value?: string;
  path?: string;
  checks?: Validation[];
}

interface Validation {
  type: 'element_exists' | 'console_clean' | 'text_visible' | 'url_contains';
  selector?: string;
  text?: string;
  value?: string;
  level?: string;
  expected?: any;
}

interface WaitCondition {
  load?: 'networkidle' | 'domcontentloaded';
  selector?: string;
  text?: string;
  timeout?: number;
}
```

### C. Migration Checklist

- [ ] Install agent-browser
- [ ] Verify basic functionality
- [ ] Create skill structure
- [ ] Write first test
- [ ] Implement TestRunner
- [ ] Implement AgentBrowserAdapter
- [ ] Implement TestSuite
- [ ] Implement reporters
- [ ] Migrate regression tests (34 pages)
- [ ] Migrate E2E tests (key workflows)
- [ ] Migrate performance tests
- [ ] Migrate security tests
- [ ] Parallel validation
- [ ] CI/CD integration
- [ ] Documentation
- [ ] Team training
- [ ] Cutover to new system
- [ ] Deprecate legacy system

---

**Document Version**: 1.0.0
**Last Updated**: 2026-03-18
**Status**: Ready for Review
