# Parameter Routes - Verification Guide

**Date**: 2026-03-03
**Purpose**: Step-by-step guide to verify the parameter routes fix

---

## Quick Verification (2 minutes)

### Step 1: Open DevTools
1. Open browser (Chrome/Firefox/Edge)
2. Press `F12` or `Cmd+Option+I` (Mac) to open DevTools
3. Go to **Console** tab
4. Clear console (🚫 button)

### Step 2: Test Each Route

#### Test 1: Parameters List (Base Route)
```
URL: http://localhost:5173/#/parameters
Expected:
  - Page title: "参数管理"
  - Content: Table with parameters, search bar, filters
  - Console: No errors
```

#### Test 2: Parameters Dashboard
```
URL: http://localhost:5173/#/parameters/dashboard
Expected:
  - Page title: "参数统计"
  - Content: Dashboard cards with statistics
  - Console: No errors
```

#### Test 3: Parameters Compare
```
URL: http://localhost:5173/#/parameters/compare
Expected:
  - Page title: "参数对比"
  - Content: Parameter comparison interface
  - Console: No errors
```

#### Test 4: Parameters Enhanced
```
URL: http://localhost:5173/#/parameters/enhanced
Expected:
  - Page title: Enhanced parameters view
  - Content: Enhanced parameters table
  - Console: No errors
```

#### Test 5: Legacy Parameter Dashboard (Backward Compatibility)
```
URL: http://localhost:5173/#/parameter-dashboard
Expected:
  - Page title: "参数统计"
  - Content: Dashboard cards with statistics
  - Console: No errors
```

---

## Visual Comparison

### Before Fix (❌ WRONG)
```
URL: /parameters/dashboard
Shows: Parameters List page (参数管理)
Problem: Wrong page!
```

### After Fix (✅ CORRECT)
```
URL: /parameters/dashboard
Shows: Parameter Dashboard page (参数统计)
Result: Correct page!
```

---

## Common Issues and Solutions

### Issue 1: Page Shows "Select Game" Prompt
**Cause**: No game selected in global context
**Solution**: Select a game first from the game selector

### Issue 2: Console Shows "React has detected a change in Hooks"
**Cause**: React Hooks ordering issue (different problem)
**Solution**: This is unrelated to routing, check component code

### Issue 3: Page Shows Loading Spinner Forever
**Cause**: API not responding or game_gid not set
**Solution**:
1. Check backend is running: `curl http://127.0.0.1:5001/api/health`
2. Check game_gid in URL: `?game_gid=10000147`

### Issue 4: Route Shows 404 Page
**Cause**: Route not defined or typo in URL
**Solution**:
1. Check route exists in `routes.tsx`
2. Check URL spelling (no extra slashes, correct hyphens)

---

## Automated Test Script

### Browser Console Test
```javascript
// Run this in browser console to test all routes
const routes = [
  { path: '/parameters', title: '参数管理' },
  { path: '/parameters/dashboard', title: '参数统计' },
  { path: '/parameters/compare', title: '参数对比' },
  { path: '/parameters/enhanced', title: 'Enhanced' },
  { path: '/parameter-dashboard', title: '参数统计' }
];

routes.forEach((route, index) => {
  setTimeout(() => {
    window.location.hash = route.path;
    console.log(`Testing: ${route.path} - Expected: ${route.title}`);
  }, index * 2000);
});
```

### Expected Output
```
Testing: /parameters - Expected: 参数管理
Testing: /parameters/dashboard - Expected: 参数统计
Testing: /parameters/compare - Expected: 参数对比
Testing: /parameters/enhanced - Expected: Enhanced
Testing: /parameter-dashboard - Expected: 参数统计
```

---

## Success Criteria

✅ All 5 routes load without console errors
✅ Each route shows correct page title
✅ Each route shows correct page content
✅ No "Select Game" prompt (if game already selected)
✅ No infinite loading spinners
✅ No 404 pages

---

## If Tests Fail

### Check 1: Route Configuration
```bash
# Verify routes are in correct order
cd /Users/mckenzie/Documents/event2table/frontend/src/routes
grep -A5 "path: \"parameters" routes.tsx
```

Expected output:
```
    // More specific parameter routes must come before general "parameters" route
    { path: "parameters/dashboard", element: <ParameterDashboard /> },
    { path: "parameters/compare", element: <ParameterCompare /> },
    { path: "parameters/enhanced", element: <ParametersEnhanced /> },
    { path: "parameters", element: <ParametersList /> },
```

### Check 2: Dev Server Running
```bash
# Check if dev server is running
ps aux | grep vite | grep -v grep
```

Expected: At least one vite process running

### Check 3: No TypeScript Errors
```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm run build
```

Expected: Build succeeds without errors

### Check 4: Browser Console
Open browser DevTools Console and check:
- ❌ No red error messages
- ❌ No React warnings about Hooks
- ✅ Page renders without crashes

---

## Report Results

### Pass: All Tests Pass
```markdown
✅ Parameter routes fix verified
Date: 2026-03-03
Tester: [Your Name]
Results: 5/5 routes working correctly
```

### Fail: Some Tests Fail
```markdown
❌ Parameter routes fix has issues
Date: 2026-03-03
Tester: [Your Name]
Failed Routes:
- /parameters/dashboard: Shows wrong page
- /parameters/compare: Shows 404
Action: Open issue with details
```

---

## Next Steps

After successful verification:
1. ✅ Mark task as complete
2. ✅ Update CLAUDE.md with routing best practices
3. ✅ Add E2E test for parameter routes
4. ✅ Close related issues

---

## References

- **Fix Report**: [PARAMETER-ROUTES-FIX.md](./PARAMETER-ROUTES-FIX.md)
- **Route File**: `/Users/mckenzie/Documents/event2table/frontend/src/routes/routes.tsx`
- **React Router Docs**: https://reactrouter.com/en/main/route/route#matching-priority
