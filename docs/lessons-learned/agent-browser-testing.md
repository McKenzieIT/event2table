# Agent-Browser Testing Methodology

> **Priority**: P0 - Critical
> **Source**: CLAUDE.md Agent-Browser section + March 2026 E2E reports
> **Last Updated**: 2026-03-20

---

## Overview

Agent-Browser is a critical testing tool for Event2Table's E2E testing workflow. This experience document covers troubleshooting, testing methodologies, and alternative approaches when agent-browser encounters issues.

---

## Problem #1: Resource Temporarily Unavailable (os error 35)

**Priority**: P0
**Frequency**: High
**Impact**: Blocks all E2E testing

### Problem Symptoms

```
Error: Resource temporarily unavailable (os error 35)
```

### Root Cause

The agent-browser daemon process is either:
1. Busy with another operation
2. Stuck in a deadlock state
3. Exceeded resource limits
4. Not properly cleaned up after previous test

### Solution

**Step 1: Terminate all agent-browser processes**
```bash
pkill -f "agent-browser"
```

**Step 2: Wait 2-3 seconds for cleanup**
```bash
sleep 3
```

**Step 3: Restart agent-browser**
```bash
agent-browser open http://localhost:5173
```

### Prevention

- Always clean up agent-browser processes after testing
- Use command chains (`&&`) to ensure sequential execution
- Monitor Chrome process memory usage
- Implement automatic cleanup in test scripts

---

## Problem #2: Commands Run in Background with No Output

**Priority**: P1
**Frequency**: Medium
**Impact**: Difficult to debug test failures

### Problem Symptoms

```bash
agent-browser open http://localhost:5173
# No output, hangs indefinitely
```

### Root Cause

Agent-browser defaults to background execution. When commands are run separately, the daemon may not be ready for the next command.

### Solution

**Use command chains with `&&`**:
```bash
# ✅ Correct: Use command chain
agent-browser open http://localhost:5173 && \
agent-browser wait --load networkidle && \
agent-browser get url

# ❌ Wrong: Separate commands (will likely fail)
agent-browser open http://localhost:5173
agent-browser wait --load networkidle
```

### Why This Works

The `&&` operator ensures:
1. Each command waits for the previous one to complete
2. If any command fails, subsequent commands are not executed
3. The daemon stays in sync with the test flow

---

## Problem #3: Chrome Process Memory Bloat

**Priority**: P1
**Frequency**: High (with repeated testing)
**Impact**: System slowdown, test instability

### Problem Symptoms

- Chrome using >2GB RAM
- Multiple Chrome processes remaining after tests
- System becomes sluggish
- agent-browser commands timeout

### Root Cause

Each agent-browser session spawns Chrome processes that may not be properly cleaned up.

### Solution

**定期清理agent-browser进程**:
```bash
# Before testing
pkill -f "agent-browser"

# Run tests
# ...

# After testing
pkill -f "agent-browser"
```

### Automation

Add to test setup/teardown:
```bash
# In test script setup()
cleanup_agent_browser() {
    pkill -f "agent-browser" || true
    sleep 2
}

# In test script teardown()
cleanup_agent_browser
```

---

## Alternative Testing Approaches

When agent-browser is unavailable or unstable, use these alternatives:

### Alternative 1: Event2Table Universal Test Skill (Recommended)

```bash
/skills: event2table-universal-test
```

**Advantages**:
- ✅ Designed specifically for Event2Table
- ✅ Covers all testing types (regression, E2E, API)
- ✅ No agent-browser dependency
- ✅ Comprehensive test coverage (39 pages)

### Alternative 2: Direct GraphQL API Testing

```bash
#适用于后端逻辑验证
curl -s -X POST http://127.0.0.1:5001/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { ... }"}'
```

**Use Cases**:
- Backend logic validation
- API contract testing
- Quick smoke tests
- Continuous integration

### Alternative 3: Code Review Verification

When automated testing isn't possible:
- ✅ Check component props interfaces
- ✅ Review conditional rendering logic
- ✅ Verify event bindings
- ✅ Manually trace through code paths

---

## Prohibited Behaviors ⚠️

### ❌ DO NOT: Create Alternative Test Scripts to Bypass agent-browser Issues

**Why This is Wrong**:
- Creates technical debt
- Avoids fixing the root cause
- Leads to fragmented test infrastructure
- Makes debugging harder in the future

**Correct Approach**:
1. Attempt to diagnose and fix agent-browser issues
2. Use project-specific testing skills (event2table-universal-test)
3. Document the problem and solution
4. Only use alternatives when agent-browser is truly unavailable

### ❌ DO NOT: Use Other Tools Without Reporting agent-browser Problems

**Why This is Wrong**:
- Team loses visibility into agent-browser reliability issues
- Problems never get fixed
- Knowledge isn't shared

**Correct Approach**:
- Document the error (os error 35, etc.)
- Record the fix steps
- Update this experience document
- If unfixable, create issue ticket

---

## Documentation Requirements

When encountering agent-browser issues, document:

1. **Error Information**:
   - Exact error message
   - Error code (os error 35, etc.)
   - Frequency of occurrence

2. **Solution Steps**:
   - What worked
   - What didn't work
   - Commands used

3. **Context**:
   - What was being tested
   - Testing environment
   - Chrome version
   - agent-browser version

4. **Follow-up**:
   - Was the issue resolved?
   - Are there any remaining concerns?
   - Should this be added to troubleshooting guide?

---

## Code Review Checklist

**每次使用agent-browser时必须检查**:

- [ ] 是否有多个Chrome进程残留？
  ```bash
  ps aux | grep -i chrome | grep -v grep
  ```

- [ ] daemon进程是否响应？
  ```bash
  lsof -i :9222  # Check if debugging port is in use
  ```

- [ ] 命令链是否正确使用 `&&` 连接？
  ```bash
  # Verify commands are chained, not separate
  ```

- [ ] 是否等待足够时间让页面加载？
  ```bash
  # Use wait --load networkidle for reliability
  ```

---

## Violation Consequences

**违反后果**:
- ⚠️ **技术债务累积**: Workarounds become permanent
- ⚠️ **测试覆盖不完整**: Skipping tests reduces confidence
- ⚠️ **无法发现真实用户体验问题**: Manual testing misses automated test scenarios
- ⚠️ **知识孤岛**: Team members repeat same mistakes
- ❌ **Code Review必须要求**: 记录问题和解决方案

---

## Related Experiences

- [Testing Guide - E2E Testing](./testing-guide.md#e2e测试)
- [Testing Guide - Chrome DevTools MCP](./testing-guide.md#chrome-devtools-mcp测试流程)
- [React Best Practices - React Mount Diagnosis](./react-best-practices.md#react应用挂载问题诊断)
- [API Design Patterns - API Contract Testing](./api-design-patterns.md#api契约一致性验证)

---

## Quick Reference

### Common agent-browser Commands

```bash
# Open page
agent-browser open http://localhost:5173

# Wait for page load
agent-browser wait --load networkidle

# Get page URL
agent-browser get url

# Take screenshot
agent-browser screenshot --file /path/to/screenshot.png

# Get page snapshot
agent-browser snapshot

# List console messages
agent-browser console --types error,warning

# Click element
agent-browser click --selector "#button-id"

# Fill input
agent-browser fill --selector "#input-id" --value "test value"

# Execute JavaScript
agent-browser eval "document.title"

# Close browser
agent-browser close
```

### Troubleshooting Commands

```bash
# Check Chrome processes
ps aux | grep -i chrome | grep -v grep

# Kill all agent-browser processes
pkill -f "agent-browser"

# Check if debugging port is in use
lsof -i :9222

# Check Chrome memory usage
ps aux | grep -i chrome | awk '{print $6}' | awk '{sum+=$1} END {print sum/1024" MB"}'

# Restart Chrome with clean profile
agent-browser open --profile /tmp/clean-profile http://localhost:5173
```

---

**Experience Template Version**: 1.0
**Category**: Testing
**Subcategory**: E2E Testing
**Tags**: agent-browser, chrome-devtools, e2e, testing, troubleshooting
