# P0 Bug Fix Plan - Game Context Issues

## Summary

This document outlines the bugs found in P0 pages through TDD-based testing and the fixes applied.

## Bugs Discovered

### BUG #1: FieldBuilder URL Parameter Inconsistency ⚠️ **CRITICAL**

**File**: `src/event-builder/pages/FieldBuilder.tsx`

**Location**: Lines 163, 165

**Issue**:
```typescript
// Line 163: Writes gameGid (camelCase)
setSearchParams({ gameGid: urlGameGid.toString(), eventId: selectedEventId.toString() });

// Line 165: Writes gameGid (camelCase)
setSearchParams({ gameGid: urlGameGid.toString() });

// Line 63: Reads game_gid (snake_case)
const gameGidFromUrl = searchParams.get('game_gid');
```

**Impact**:
- When user navigates within FieldBuilder, URL parameters change from `game_gid` to `gameGid`
- Page refresh or direct link with `gameGid` parameter fails to read game context
- Inconsistent with backend API which uses `game_gid`

**Fix**:
```typescript
// Change line 163
setSearchParams({ game_gid: urlGameGid.toString(), eventId: selectedEventId.toString() });

// Change line 165
setSearchParams({ game_gid: urlGameGid.toString() });
```

### BUG #2: FlowBuilder Missing Game Context ⚠️ **MODERATE**

**File**: `src/features/canvas/pages/FlowBuilder.tsx`

**Issue**:
- FlowBuilder is a stub component that doesn't read game context
- Should read `game_gid` from URL parameters
- Should pass game context to child components

**Impact**:
- FlowBuilder cannot display game-specific flows
- Future Canvas features will fail without game context

**Fix**:
Add game context reading logic similar to other P0 pages:
```typescript
import { useSearchParams } from 'react-router-dom';
import { useGameContext } from '@shared/hooks/useGameContext';

function FlowBuilder() {
  const [searchParams] = useSearchParams();
  const { currentGameGid } = useGameContext();

  // Priority: URL parameter > useGameContext > localStorage > default
  const gameGidFromUrl = searchParams.get('game_gid');
  const gameGidFromStorage = typeof window !== 'undefined'
    ? localStorage.getItem('selectedGameGid')
    : null;
  const gameGid = gameGidFromUrl || currentGameGid || gameGidFromStorage || '10000147';

  // Use gameGid for API calls and child components
  // ...
}
```

### BUG #3: Generate and ImportEvents Good Practices ✅ **NO BUG**

**Files**:
- `src/analytics/pages/Generate.tsx` (Line 47)
- `src/analytics/pages/ImportEvents.tsx` (Line 123)

**Status**: These pages use correct fallback logic:
```typescript
const gameGid = currentGameGid || localStorage.getItem("selectedGameGid") || "10000147";
```

**Verdict**: This is good defensive programming. No fix needed.

## TDD Cycle for Bug Fixes

### Bug #1 Fix - FieldBuilder

**RED Phase**:
1. Write test `p0-bug-detection.spec.ts` that demonstrates URL parameter inconsistency
2. Run test and confirm it fails
3. Document the bug with console output

**GREEN Phase**:
1. Fix FieldBuilder.tsx lines 163 and 165
2. Run test again and confirm it passes
3. Verify URL parameter consistency

**REFACTOR Phase**:
1. Extract URL parameter name to constant
2. Add TypeScript type for URL parameters
3. Document the convention in code comments

### Bug #2 Fix - FlowBuilder

**RED Phase**:
1. Write test that verifies FlowBuilder reads game context
2. Run test and confirm it fails (FlowBuilder is a stub)

**GREEN Phase**:
1. Add game context reading logic to FlowBuilder
2. Run test and confirm it passes
3. Verify game context is used correctly

**REFACTOR Phase**:
1. Share common game context reading logic across all P0 pages
2. Create custom hook `useGameGid`
3. Update all pages to use the shared hook

## Implementation Priority

1. **P0 - URGENT**: Fix FieldBuilder URL parameter inconsistency
2. **P1 - HIGH**: Add game context reading to FlowBuilder
3. **P2 - MEDIUM**: Create shared `useGameGid` hook for code reuse

## Testing Strategy

### Unit Tests
- Test `useGameGid` hook with various scenarios
- Test URL parameter parsing logic

### E2E Tests
- Test each P0 page with different URL parameter formats
- Test navigation within pages preserves game context
- Test page refresh maintains game context

### Manual Testing
1. Navigate to `/field-builder?game_gid=10000147`
2. Select an event
3. Verify URL stays `/field-builder?game_gid=10000147&eventId=123`
4. Refresh page
5. Verify game context is maintained

## Success Criteria

- [ ] All P0 pages use `game_gid` (snake_case) consistently
- [ ] All P0 pages read game context from URL parameters
- [ ] All P0 pages have fallback logic for missing game context
- [ ] E2E tests pass for all P0 pages
- [ ] Manual testing confirms game context is preserved across navigation
- [ ] No console errors related to game context

## Files to Modify

1. `src/event-builder/pages/FieldBuilder.tsx` - Fix URL parameter names
2. `src/features/canvas/pages/FlowBuilder.tsx` - Add game context reading
3. `src/shared/hooks/useGameGid.ts` - Create shared hook (NEW)
4. `src/analytics/pages/Generate.tsx` - Use shared hook (REFACTOR)
5. `src/analytics/pages/ImportEvents.tsx` - Use shared hook (REFACTOR)
6. `src/event-builder/pages/FieldBuilder.tsx` - Use shared hook (REFACTOR)
7. `src/features/canvas/pages/FlowBuilder.tsx` - Use shared hook (REFACTOR)

## Rollback Plan

If bugs are introduced:
1. Revert changes to affected files
2. Run E2E tests to verify baseline
3. Apply fixes incrementally
4. Test each fix individually before proceeding

## References

- URL Parameter Convention: Backend API uses `game_gid` (snake_case)
- Game Context Hook: `src/shared/hooks/useGameContext.ts`
- TDD Documentation: `docs/lessons-learned/testing-guide.md`
