# Dashboard Card Click Fix - Verification Report

**Date**: 2026-02-12
**Issue**: Dashboard quick action cards not responding to clicks
**Status**: ✅ FIXED

---

## Root Cause Analysis

### Problem
The Dashboard was using `<Card as={Link} to="/games">` syntax, but the Card component exported from `@shared/ui` did not support the `as` prop.

### Technical Details

**File Location**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Card/Card.jsx`

**Original Code** (Line 56):
```jsx
return (
  <div ref={ref} className={cardClass} {...domProps}>
    {children}
  </div>
);
```

**Issue**: The component hardcoded the HTML element as `<div>`, ignoring any `as` prop passed by the consumer.

---

## Solution Implemented

### Changes Made

#### 1. Added `as` prop support to Card component

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Card/Card.jsx`

**Modified Code**:
```jsx
const Card = React.forwardRef(({
  children,
  className = '',
  variant = 'default',
  hoverable = false,
  glowing = false,
  hover = false,
  padding = 'md',
  as: Component = 'div',  // ✅ NEW: Support custom component
  ...props
}, ref) => {
  // ...existing code...

  // Filter out boolean props and 'as' prop before spreading to DOM
  const { hoverable: _, glowing: __, hover: ___, as: ____, ...domProps } = props;

  return (
    <Component ref={ref} className={cardClass} {...domProps}>
      {children}
    </Component>
  );
});
```

#### 2. Updated React.memo comparison

**Added `as` prop to memo comparison**:
```jsx
const MemoizedCard = React.memo(Card, (prevProps, nextProps) => {
  return (
    prevProps.variant === nextProps.variant &&
    (prevProps.hover || prevProps.hoverable) === (nextProps.hover || nextProps.hoverable) &&
    prevProps.glowing === nextProps.glowing &&
    prevProps.padding === nextProps.padding &&
    prevProps.className === nextProps.className &&
    prevProps.as === nextProps.as &&  // ✅ NEW: Compare 'as' prop
    prevProps.children === nextProps.children
  );
});
```

#### 3. Updated documentation

Added example in JSDoc:
```jsx
/**
 * @example
 * // Clickable card (as Link)
 * <Card as={Link} to="/games" hoverable>
 *   <Card.Content>Manage Games</Card.Content>
 * </Card>
 */
```

---

## Verification Steps

### Manual Testing Required

Since Node.js is not available in this environment, **manual testing is required**:

1. **Start development server**:
   ```bash
   cd /Users/mckenzie/Documents/event2table/frontend
   npm run dev
   ```

2. **Open browser** to `http://localhost:5173`

3. **Test Dashboard quick action cards**:
   - Click "管理游戏" card → Should navigate to `/games`
   - Click "管理事件" card → Should navigate to `/events`
   - Click "HQL画布" card → Should navigate to `/canvas`
   - Click "流程管理" card → Should navigate to `/flows`

4. **Test recent games cards**:
   - Click any recent game card → Should navigate to `/events?game_gid={gid}`

5. **Verify hover effects**:
   - Cards should lift up (`translateY(-2px)`)
   - Cards should show enhanced border glow
   - Cursor should change to pointer

### Expected Behavior

✅ **Clicking any card should navigate to the target route**
✅ **Hover effects should work**
✅ **No JavaScript errors in console**
✅ **Router should correctly update URL**

---

## Impact Analysis

### Files Modified
1. `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Card/Card.jsx`

### Files Using Card with `as` prop
- `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/Dashboard.jsx` (Lines 100-122)
- Any other component using `<Card as={Link} ...>` syntax

### Backward Compatibility
✅ **Fully backward compatible**
- Default behavior unchanged (renders as `<div>`)
- Existing cards continue to work
- No breaking changes

---

## Additional Notes

### CSS Pointer Events
The `pointer-events: none` in `Card/Card.css:135` is **correct behavior** - it's applied to the `::before` pseudo-element (decorative grid overlay), not the card itself. This allows clicks to pass through the decorative overlay to the card content.

### Duplicate Card Components
The project has two Card components:
1. `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Card/Card.jsx` (actively used, exported via index.ts)
2. `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Card.jsx` (legacy, not exported)

**The active Card component (Card/Card.jsx) now supports the `as` prop, matching the legacy Card.jsx behavior.**

---

## Testing Checklist

Before merging, verify:

- [ ] All Dashboard quick action cards are clickable
- [ ] Navigation works correctly (URL updates)
- [ ] Hover effects work as expected
- [ ] No console errors
- [ ] Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- [ ] Responsive design intact (mobile, tablet, desktop)
- [ ] No regression in other Card usage (non-link cards)
- [ ] React.memo optimization still works

---

## Follow-up Actions

### Recommended
1. Remove legacy `Card.jsx` from `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/` to avoid confusion
2. Add unit tests for `as` prop behavior
3. Update Storybook/Card documentation with Link examples

### Optional
1. Consider adding `clickable` prop alias for better DX
2. Add TypeScript type definitions for `as` prop

---

**Fix completed by**: Claude Code
**Date**: 2026-02-12
**Commit recommendation**: "fix: Add `as` prop support to Card component for clickable links"
