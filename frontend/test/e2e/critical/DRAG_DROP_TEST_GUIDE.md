# Drag and Drop E2E Tests - Quick Reference

## Test File Location
```
/Users/mckenzie/Documents/event2table/frontend/test/e2e/critical/drag-drop-functionality.spec.ts
```

## Test Summary

### File Statistics
- **Total Lines**: 642
- **Total Tests**: 15
- **Test Suites**: 6
- **Helper Functions**: 5

### Test Coverage

#### 1. Test Suite: Drag Parameter Field to Canvas (2 tests)
- ✅ Successfully drag a parameter field from sidebar to Canvas
- ✅ Show correct parameter name and type after drag

#### 2. Test Suite: Canvas Field Reordering (2 tests)
- ✅ Reorder fields when dragging within Canvas
- ✅ Maintain order after save and reload

#### 3. Test Suite: Drag Base Fields (2 tests)
- ✅ Drag base field (ds, role_id, etc.) to Canvas
- ✅ Show special styling for base fields

#### 4. Test Suite: Drag Common/Universal Fields (2 tests)
- ✅ Identify and handle common fields (role_id, account_id, etc.)
- ✅ Display common fields with correct data types

#### 5. Test Suite: Drop Zone Visual Feedback (4 tests)
- ✅ Show visual feedback when dragging over Canvas
- ✅ Remove visual feedback after drop completes
- ✅ Show active state when Canvas is ready to receive drops
- ✅ Highlight drop zone border during drag operation

#### 6. Test Suite: Edge Cases and Error Handling (3 tests)
- ✅ Handle dragging multiple fields quickly
- ✅ Prevent duplicate fields when dragging same parameter twice
- ✅ Handle drag from empty parameter list

## Running the Tests

### Run All Drag-Drop Tests
```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm run test:e2e -- drag-drop-functionality.spec.ts
```

### Run Specific Test Suite
```bash
# Run only parameter field tests
npm run test:e2e -- drag-drop-functionality.spec.ts -g "Test 1"

# Run only reordering tests
npm run test:e2e -- drag-drop-functionality.spec.ts -g "Test 2"

# Run only visual feedback tests
npm run test:e2e -- drag-drop-functionality.spec.ts -g "Test 5"
```

### Run with UI Mode
```bash
npm run test:e2e:ui -- drag-drop-functionality.spec.ts
```

### Run with Debug Mode
```bash
npm run test:e2e:debug -- drag-drop-functionality.spec.ts
```

## Test Data

### Configuration
- **Test Game GID**: 10000147 (STAR001)
- **Base URL**: http://localhost:5173
- **Test Page**: /#/event-node-builder?game_gid=10000147
- **Test Event**: phxcard.gacha

### Helper Functions

#### `waitForEventSelection(page)`
Closes the FieldSelectionModal that appears after event selection.

#### `selectEvent(page, eventName)`
Selects an event from the dropdown and waits for parameters to load.

#### `getCanvasFieldCount(page)`
Returns the current number of fields on the Canvas.

#### `clearCanvas(page)`
Clears all fields from the Canvas (with confirmation dialog handling).

## Technical Implementation

### Drag and Drop APIs Used
- **Playwright dragTo()**: Primary method for drag-and-drop
- **dnd-kit**: Library used in the application
- **HTML5 Drag and Drop**: Fallback for certain components

### Selectors Used
- `[data-testid="event-node-builder"]` - Main container
- `[data-testid="field-canvas-drop-zone"]` - Canvas drop zone
- `[data-testid^="param-"]` - Parameter fields
- `.field-item` - Canvas field items
- `.field-handle` - Drag handle for reordering
- `.field-alias` - Field display name
- `.field-type-label` - Field type badge

### Test Isolation
Each test:
1. Starts with a fresh page load
2. Clears any existing Canvas data
3. Selects the test event
4. Performs drag-drop operations
5. Verifies results
6. Cleans up in afterEach

## Execution Time Estimate

| Test Suite | Estimated Time |
|------------|---------------|
| Test 1: Parameter Fields | ~30 seconds |
| Test 2: Reordering | ~40 seconds |
| Test 3: Base Fields | ~30 seconds |
| Test 4: Common Fields | ~30 seconds |
| Test 5: Visual Feedback | ~40 seconds |
| Edge Cases | ~30 seconds |
| **Total** | **~3-4 minutes** |

## Expected Behavior

### Successful Test Flow
1. Page loads at `/event-node-builder?game_gid=10000147`
2. Event "phxcard.gacha" is selected
3. FieldSelectionModal is closed
4. Parameters are loaded in left sidebar
5. Drag operations complete successfully
6. Canvas updates in real-time
7. Visual feedback appears/disappears correctly
8. Field types and names display correctly

### Common Issues and Solutions

#### Issue: Parameters not loading
**Solution**: Wait for event selection to complete before dragging

#### Issue: FieldSelectionModal blocks drag operations
**Solution**: Use `waitForEventSelection()` helper to close modal

#### Issue: Drop zone not accepting drops
**Solution**: Verify event is selected and parameters are loaded

#### Issue: Tests timing out
**Solution**: Increase timeout in test config or add more wait time

## Validation Checklist

After running tests, verify:
- ✅ All 15 tests pass
- ✅ No console errors
- ✅ No network failures
- ✅ Canvas fields display correctly
- ✅ Field types are accurate
- ✅ Visual feedback works as expected

## Maintenance Notes

### When to Update Tests
- Component selectors change
- New field types are added
- Drag-drop behavior changes
- Event names or structure changes

### Test Dependencies
- Playwright >= 1.40.0
- Application must be running on http://localhost:5173
- Backend API must be accessible
- Test game (GID 10000147) must exist in database

## Related Files

- **Component**: `/frontend/src/event-builder/components/FieldCanvas.tsx`
- **Component**: `/frontend/src/event-builder/components/ParamSelector.tsx`
- **Component**: `/frontend/src/event-builder/components/LeftSidebar.tsx`
- **Page**: `/frontend/src/event-builder/pages/EventNodeBuilder.tsx`
- **Hook**: `/frontend/src/shared/hooks/useEventNodeBuilder.ts`

## Test Report Template

After running tests, document results:

```
Date: [DATE]
Tester: [NAME]
Environment: [DEV/STAGING/PROD]

Results:
- Total Tests: 15
- Passed: X
- Failed: Y
- Skipped: Z

Issues Found:
1. [Description]
2. [Description]

Screenshots:
- [Attach if failures occur]
```

---

**Created**: 2026-03-12
**Last Updated**: 2026-03-12
**Version**: 1.0.0
