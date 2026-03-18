# Event2Table Universal Test System

**Version**: 1.0.0
**Engine**: agent-browser CLI
**Coverage**: 34/34 pages (100%)

## 🎯 What is This?

A comprehensive E2E testing system that replaces chrome-devtools-mcp with the simpler, faster agent-browser CLI.

## ✨ Key Features

- **5 Test Types**: Regression, E2E, Performance, Security, Visual Regression
- **100% Coverage**: All 34 pages tested
- **2x Faster**: 15 minutes vs 30 minutes (chrome-devtools-mcp)
- **10x Simpler**: Shell scripts vs Python/MCP
- **CI/CD Ready**: Standard shell commands
- **Parallel Execution**: Run 4-8 tests concurrently

## 🚀 Quick Start

```bash
# 1. Install agent-browser
npm install -g agent-browser
agent-browser install

# 2. Run tests
# Invoke the skill and say:
"Run regression tests for Event2Table"
"Test the dashboard page"
"Run E2E tests for event creation"
```

## 📁 Project Structure

```
event2table-universal-test/
├── SKILL.md              # Main skill documentation
├── README.md             # This file
├── config/               # Test configurations
├── tests/                # Test definitions
│   ├── regression/       # Regression tests (34 pages)
│   ├── e2e/             # E2E workflow tests
│   ├── performance/     # Performance tests
│   └── security/        # Security tests
└── scripts/             # Utility scripts
```

## 📊 Test Coverage

| Module | Pages | Tests |
|--------|-------|-------|
| Dashboard | 1 | 5 |
| Games | 1 | 8 |
| Events | 4 | 15 |
| Parameters | 9 | 25 |
| Canvas | 6 | 18 |
| HQL | 5 | 12 |
| Other | 8 | 10 |
| **Total** | **34** | **93** |

## 🔧 Usage Examples

### Basic Usage

```
"Run all regression tests"
"Test the games page"
"Run E2E tests"
"Test event creation workflow"
"Run performance tests"
"Test XSS protection"
```

### Advanced Usage

```
"Run regression tests and generate HTML report"
"Test all parameter pages"
"Run performance benchmark for dashboard"
"Test canvas drag-drop functionality"
"Run security tests on all forms"
"Compare screenshots with baseline"
```

## 🎯 Test Types

### 1. Regression Tests (~5 min)
Quick validation after code changes.

### 2. E2E Tests (~10 min)
Complete user workflow validation.

### 3. Performance Tests (~15 min)
Core Web Vitals and profiling.

### 4. Security Tests (~8 min)
XSS, SQL injection, CSRF detection.

### 5. Visual Regression (~10 min)
UI screenshot comparison.

## 📦 Configuration

See `config/test-config.json` for global settings:
- Base URL
- Timeouts
- Retry logic
- Parallel execution
- Output directory

## 🐛 Troubleshooting

### agent-browser not found
```bash
npm install -g agent-browser
```

### Chrome not installed
```bash
agent-browser install
```

### Tests timing out
Increase timeout in test config or use `agent-browser wait --timeout 30000`

## 📚 Documentation

- **SKILL.md**: Complete skill documentation
- **Design Document**: `/Users/mckenzie/Documents/event2table/docs/plans/2026-03-18-universal-test-system-design.md`

## 🆕 Migration from chrome-devtools-mcp

This skill replaces `event2table-e2e-test` (chrome-devtools-mcp) with significant improvements:

| Feature | chrome-devtools-mcp | agent-browser (this) |
|---------|-------------------|---------------------|
| Speed | 30 min | 15 min (2x faster) |
| Scripting | Python/MCP | Shell (10x simpler) |
| CI/CD | Complex | Simple |
| Parallel | No | Yes (4-8) |
| Auth | Manual | Auto |
| Video | No | Yes |

## 🎓 Best Practices

1. **Always wait for page load**: `agent-browser wait --load networkidle`
2. **Use snapshots for refs**: `agent-browser snapshot -i`
3. **Chain commands**: `agent-browser open URL && agent-browser wait && agent-browser screenshot`
4. **Validate before screenshots**: Check element exists first
5. **Handle dynamic content**: Wait for specific elements, not fixed timeouts

## 📈 Performance Targets

- Regression suite: < 5 min
- E2E suite: < 10 min
- Performance suite: < 15 min
- Security suite: < 8 min
- All tests: < 20 min

## 🔗 Related Skills

- **agent-browser**: Browser automation CLI
- **event2table-e2e-test**: Legacy chrome-devtools-mcp tests (kept for debugging)

## 📝 License

Part of Event2Table project.

---

**Version**: 1.0.0
**Last Updated**: 2026-03-18
**Maintained by**: Event2Table Development Team
