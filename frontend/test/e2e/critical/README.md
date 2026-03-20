# E2E Test Suite - Critical Pages

This directory contains comprehensive E2E tests for all critical pages in Event2Table.

## Test Files

- `01-dashboard.spec.ts` - Dashboard (首页) tests
- `02-games-list.spec.ts` - Games List (游戏列表) tests
- `03-games-modal.spec.ts` - Games Modal (游戏管理模态框) tests
- `04-events-list.spec.ts` - Events List (事件列表) tests
- `05-events-create.spec.ts` - Events Create (创建事件) tests
- `06-parameters-list.spec.ts` - Parameters List (参数列表) tests
- `07-parameter-dashboard.spec.ts` - Parameter Dashboard (参数仪表板) tests
- `08-event-node-builder.spec.ts` - Event Node Builder (事件节点构建器) tests
- `09-event-nodes.spec.ts` - Event Nodes (事件节点管理) tests
- `10-canvas.spec.ts` - Canvas (HQL构建画布) tests
- `11-flows.spec.ts` - Flows Management (HQL流程管理) tests
- `12-categories.spec.ts` - Categories Management (分类管理) tests
- `13-common-params.spec.ts` - Common Parameters (公参管理) tests

## Test Coverage

Each test file covers 10 essential functionalities:

1. ✅ Page load + DOM structure validation
2. ✅ Console error checking
3. ✅ All button clicks
4. ✅ Form interactions
5. ✅ Search/filter functionality
6. ✅ Modal opening/closing
7. ✅ API call status
8. ✅ Statistics/data display
9. ✅ Pagination
10. ✅ Performance measurement

## Running Tests

### Run all critical tests:
```bash
cd frontend
npx playwright test critical/
```

### Run specific test file:
```bash
npx playwright test critical/01-dashboard.spec.ts
```

### Run with UI:
```bash
npx playwright test critical/ --ui
```

### Run with debugging:
```bash
npx playwright test critical/ --debug
```

## Test Data

- Production test game: GID 10000147 (STAR001)
- Test GID range: 90000000+ (avoids conflicts)
- Test games are automatically cleaned up after tests

## Expected Results

- All tests should pass (>95% pass rate)
- No console errors
- Page load < 10 seconds
- All buttons clickable
- All forms submittable
- API calls successful (no 500 errors)

## Troubleshooting

### Tests fail with "Target closed"
- Backend server not running
- Solution: Start backend with `python web_app.py`

### Tests timeout
- Page loading too slowly
- Solution: Check browser console for JavaScript errors

### API call failures
- Backend not responding
- Solution: Check backend logs and restart server

### Database errors
- Test database not initialized
- Solution: Run `python scripts/setup/init_db.py`
