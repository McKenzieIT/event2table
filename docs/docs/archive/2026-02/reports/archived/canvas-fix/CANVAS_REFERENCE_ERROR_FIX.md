# Canvas ReferenceError Fix - Summary

## Problem Description

The canvas feature was throwing a `ReferenceError: Cannot access 'ye' before initialization` error when accessed. This is a classic JavaScript Temporal Dead Zone (TDZ) error caused by circular references in the `queryKeys` object initialization.

## Root Cause

The issue was in the `queryKeys` objects across multiple files. The object was trying to reference itself during initialization:

```javascript
// ❌ PROBLEMATIC CODE
export const queryKeys = {
  eventConfigs: {
    all: ['event-configs'],
    lists: () => [...queryKeys.eventConfigs.all, 'list'],  // ❌ Circular reference!
    list: (gameGid) => [...queryKeys.eventConfigs.lists(), gameGid],  // ❌ Circular reference!
    // ... more circular references
  },
  // ... more objects with circular references
};
```

### Why This Failed

In JavaScript, when using `const`, variables cannot be referenced during their initialization. The `queryKeys` object was being defined, but its methods were trying to access `queryKeys.eventConfigs.all` before the entire object was fully initialized. This caused the minified build to fail with a ReferenceError.

## Solution

The fix involves extracting the base keys into separate constants before defining the main object:

```javascript
// ✅ FIXED CODE
// Define base keys first to avoid circular references
const eventConfigsBase = ['event-configs'];
const flowsBase = ['flows'];
const gamesBase = ['games'];
const canvasBase = ['canvas'];

export const queryKeys = {
  eventConfigs: {
    all: eventConfigsBase,  // ✅ Uses the pre-defined constant
    lists: () => [...eventConfigsBase, 'list'],  // ✅ No circular reference
    list: (gameGid) => [...eventConfigsBase, 'list', gameGid],  // ✅ Direct reference
    // ... rest of the methods
  },
  // ... rest of the object
};
```

## Files Modified

1. **`/Users/mckenzie/Documents/event2table/frontend/src/features/canvas/api/queryKeys.ts`**
   - TypeScript version with type definitions
   - Fixed circular references in eventConfigs, flows, games, and canvas objects

2. **`/Users/mckenzie/Documents/event2table/frontend/src/features/canvas/api/queryKeys.js`**
   - JavaScript version in the features/canvas directory
   - Same fix applied

3. **`/Users/mckenzie/Documents/event2table/frontend/src/canvas/api/queryKeys.js`**
   - JavaScript version in the canvas directory (legacy/alternate location)
   - Same fix applied

## Changes Made

### Before:
- Object methods referenced `queryKeys.{category}.{property}` during initialization
- Created circular dependencies that violated JavaScript's TDZ rules
- Failed during minification/build process

### After:
- Base keys extracted to standalone constants (e.g., `eventConfigsBase`, `flowsBase`)
- All object methods reference the pre-defined constants instead of the object itself
- No circular dependencies
- Compliant with JavaScript's initialization rules

## Testing Instructions

### 1. Rebuild the Frontend

```bash
cd /Users/mckenzie/Documents/event2table/frontend
npm run build
```

### 2. Start the Flask Server

```bash
cd /Users/mckenzie/Documents/event2table
python web_app.py
```

### 3. Access the Application

1. Open a browser and navigate to: `http://localhost:5001`
2. Navigate to the canvas feature
3. Verify that no ReferenceError occurs
4. Test canvas functionality (loading flows, saving flows, executing flows)

## Expected Results

- ✅ No `ReferenceError: Cannot access 'ye' before initialization` error
- ✅ Canvas feature loads successfully
- ✅ All React Query hooks work correctly
- ✅ Query key generation functions work as expected

## Technical Details

### JavaScript Temporal Dead Zone (TDZ)

The TDZ is a behavior in JavaScript where variables declared with `const` and `let` cannot be accessed before their declaration is complete. In this case:

1. `const queryKeys` begins initialization
2. Object literal starts being created
3. Method definitions try to access `queryKeys.eventConfigs.all`
4. ❌ Error! `queryKeys` is not yet fully initialized

### Why the Fix Works

By defining base keys as separate constants before the `queryKeys` object:

1. `eventConfigsBase` is fully initialized ✅
2. `flowsBase` is fully initialized ✅
3. `gamesBase` is fully initialized ✅
4. `canvasBase` is fully initialized ✅
5. `queryKeys` object can now reference these constants ✅

### Vite Configuration Note

The `vite.config.js` file already had a comment about TDZ errors:

```javascript
// 优化依赖预构建，避免ReactFlow的TDZ错误
optimizeDeps: {
  exclude: ['reactflow'],  // 排除ReactFlow，使用源码而非预构建
},
```

This indicates the project was aware of TDZ issues with ReactFlow, but the `queryKeys` circular reference was a separate, previously unidentified TDZ issue.

## Related Code Patterns

This fix follows best practices for:

1. **React Query Key Factories**: Using stable base arrays that don't change
2. **JavaScript Initialization Order**: Avoiding self-references during object initialization
3. **Type Safety**: Maintaining type definitions in TypeScript while fixing runtime issues

## Prevention

To prevent similar issues in the future:

1. **Avoid self-referential object initializations** with `const`
2. **Extract base values** to separate constants before using them in complex objects
3. **Use factory functions** if dynamic object creation is needed
4. **Test with production builds** (minified code can expose TDZ issues that don't appear in development)

## Additional Notes

- The fix maintains backward compatibility - the queryKeys object structure and API remain unchanged
- All existing code using `queryKeys.eventConfigs.all`, `queryKeys.flows.detail(id)`, etc. will continue to work
- The generated query keys are identical to the previous implementation
- This is a pure bug fix with no functional changes to the API

---

**Fix Applied:** February 11, 2026
**Status:** Ready for rebuild and testing
**Files Changed:** 3 files (queryKeys.ts, 2x queryKeys.js)
**Lines Changed:** ~15 lines per file
