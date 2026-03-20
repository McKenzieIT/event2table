# Quick Test Execution Guide

## Purpose
Quick guide to run the E2E tests and verify the bug fixes.

## Prerequisites Checklist

- [ ] Backend server running on http://127.0.0.1:5001
- [ ] Frontend server running on http://localhost:5173
- [ ] Virtual environment activated: `source backend/venv/bin/activate`
- [ ] Node.js dependencies installed: `cd frontend && npm install`

## Step-by-Step Execution

### 1. Start Backend Server
```bash
# Terminal 1
cd /Users/mckenzie/Documents/event2table
source backend/venv/bin/activate
python web_app.py

# Expected output:
#  * Running on http://127.0.0.1:5001
#  * Restarting with stat
#  * Debugger is active!
```

### 2. Start Frontend Server
```bash
# Terminal 2
cd /Users/mckenzie/Documents/event2table/frontend
npm run dev

# Expected output:
#   VITE v7.3.1  ready in XXX ms
#
#   ➜  Local:   http://localhost:5173/
#   ➜  Network: use --host to expose
```

### 3. Run Critical E2E Tests
```bash
# Terminal 3
cd /Users/mckenzie/Documents/event2table/frontend

# Run all critical tests
npm run test:e2e:critical

# Expected output:
# Running 5 test suites using 1 worker
#
#   ✓ generate-page.spec.ts (8/8 tests)
#   ✓ field-builder-page.spec.ts (9/9 tests)
#   ✓ flow-builder-page.spec.ts (8/8 tests)
#   ✓ import-events-page.spec.ts (9/9 tests)
#   ✓ p0-bug-detection.spec.ts (3/3 tests)
#
# 37 passed (XXs)
```

### 4. Interpret Results

**All Tests Pass** ✅
```
37 passed (XXs)
```
→ All bugs fixed! Game context working correctly.

**Tests Fail** ❌
```
X failed
```
→ Check the error message:
- If "URL parameter inconsistency" → FieldBuilder fix didn't work
- If "Game context not found" → FlowBuilder fix didn't work
- If "Page load failed" → Server not running or wrong port

### 5. Run Individual Tests (Optional)

**Test Generate page only**:
```bash
npx playwright test test/e2e/critical/generate-page.spec.ts
```

**Test FieldBuilder page only**:
```bash
npx playwright test test/e2e/critical/field-builder-page.spec.ts
```

**Test FlowBuilder page only**:
```bash
npx playwright test test/e2e/critical/flow-builder-page.spec.ts
```

**Test ImportEvents page only**:
```bash
npx playwright test test/e2e/critical/import-events-page.spec.ts
```

**Test bug detection only**:
```bash
npx playwright test test/e2e/critical/p0-bug-detection.spec.ts
```

### 6. View Test Reports (Optional)

**HTML Report**:
```bash
npx playwright show-report test-output/playwright/report
```

**JSON Report**:
```bash
cat test-output/playwright/results/results.json | jq
```

## Troubleshooting

### Issue: "Cannot connect to server"
**Solution**: Make sure both backend and frontend servers are running

### Issue: "Test timeout"
**Solution**: Increase timeout in playwright.config.ts or check server logs

### Issue: "Page not found"
**Solution**: Check frontend routing configuration and verify URL paths

### Issue: "Game context not found"
**Solution**: Verify bug fixes were applied correctly to source files

## Quick Verification

**Verify FieldBuilder Fix**:
1. Open http://localhost:5173/field-builder?game_gid=10000147
2. Select an event
3. Check URL - should be `/field-builder?game_gid=10000147&eventId=123`
4. ✅ Correct if URL has `game_gid` (not `gameGid`)

**Verify FlowBuilder Fix**:
1. Open http://localhost:5173/flow-builder?game_gid=10000147
2. Check page - should display "游戏 GID: 10000147"
3. ✅ Correct if game GID is displayed

## Test Results Template

Copy and paste this template for your test results:

```
## Test Execution Results

**Date**: 2026-03-06
**Tester**: [Your Name]
**Environment**: [Development/Production]

### Server Status
- [ ] Backend server running (port 5001)
- [ ] Frontend server running (port 5173)

### Test Results
- generate-page.spec.ts: ___/8 passed
- field-builder-page.spec.ts: ___/9 passed
- flow-builder-page.spec.ts: ___/8 passed
- import-events-page.spec.ts: ___/9 passed
- p0-bug-detection.spec.ts: ___/3 passed

**Total**: ___/37 passed

### Bugs Fixed
- [ ] FieldBuilder URL parameter consistency (gameGid → game_gid)
- [ ] FlowBuilder game context reading added

### Issues Found
- [List any issues or test failures]

### Notes
- [Any additional observations]
```

## Need Help?

- **Backend Issues**: Check `logs/backend.log`
- **Frontend Issues**: Check browser console and `/tmp/frontend.log`
- **Test Issues**: Check `test-output/playwright/report/`

---

**Last Updated**: 2026-03-06
**For detailed information**: See `E2E-TEST-INFRASTRUCTURE-FIX-REPORT.md`
