# Games Management Modal E2E Test Plan

## Test Environment
- Backend: http://127.0.0.1:5001 ✅ (Running)
- Frontend: http://localhost:5173 ❌ (Needs to be started)
- Test Database: data/test_database.db

## Test Scenarios

### 1. Verify Games Page Loads
**Steps:**
1. Navigate to http://localhost:5173/#/games
2. Verify page loads without errors
3. Check browser console for errors
4. Verify "游戏管理" title is visible
5. Verify "管理游戏" button is visible

**Expected Result:**
- Page loads successfully
- No console errors
- Page title visible
- "管理游戏" button visible

### 2. Click "管理游戏" Button
**Steps:**
1. On games page
2. Click "管理游戏" button
3. Wait for modal to appear
4. Check modal title
5. Check modal content

**Expected Result:**
- Modal opens
- Modal title shows "游戏管理" or similar
- Game list visible in modal
- No console errors

### 3. Create New Game
**Steps:**
1. Open game management modal
2. Click "添加游戏" button
3. Fill form:
   - GID: 90000001 (test GID)
   - Name: "E2E Test Game"
   - ODS DB: "ieu_ods"
4. Click "保存"
5. Verify success message
6. Close modal
7. Verify game appears in list

**Expected Result:**
- Add game modal opens
- Form submits successfully
- Success toast shown
- Game appears in list
- No console errors

### 4. Edit Existing Game
**Steps:**
1. Open game management modal
2. Select a game (NOT GID 10000147 - STAR001 protected)
3. Modify game name
4. Click "保存"
5. Verify success message
6. Verify game updated in list

**Expected Result:**
- Edit mode activates
- Save button appears
- Update succeeds
- Changes reflected in list
- No console errors

### 5. Delete Game (Non-STAR001)
**Steps:**
1. Create test game (GID: 90000002)
2. Open game management modal
3. Select test game
4. Click "删除"
5. Confirm deletion
6. Verify game removed from list

**Expected Result:**
- Delete confirmation shown
- Game deleted successfully
- Game removed from list
- No console errors

### 6. Verify STAR001 Protection
**Steps:**
1. Open game management modal
2. Find STAR001 (GID: 10000147)
3. Try to delete or modify critical fields
4. Verify protection mechanism

**Expected Result:**
- Cannot delete STAR001
- Warning message shown
- STAR001 remains intact

## Test Data

### Test GIDs (Safe to use)
- 90000001 - 90000100: Test game GID range

### Protected GIDs (DO NOT MODIFY)
- 10000147: STAR001 (Production game)

## Success Criteria

✅ All tests pass
✅ No console errors
✅ No network errors
✅ Modal opens and closes smoothly
✅ CRUD operations work correctly
✅ STAR001 protection active

## Current Status

- [ ] Test environment setup
- [ ] Scenario 1: Page loads
- [ ] Scenario 2: Modal opens
- [ ] Scenario 3: Create game
- [ ] Scenario 4: Edit game
- [ ] Scenario 5: Delete game
- [ ] Scenario 6: STAR001 protection
- [ ] Final verification

## Notes

- Use Chrome DevTools MCP for testing
- Take screenshots at each step
- Record console errors
- Verify test database isolation
- Clean up test data after testing
