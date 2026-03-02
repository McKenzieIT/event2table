# Select Component Accessibility Fix

**Date**: 2026-03-02  
**Status**: ✅ Complete  
**Test Results**: 39/39 tests passing

## Problem

The Select component was generating an accessibility warning:

```
Warning: Found a label with the text of: Select Option, however the element 
associated with this label (<div />) is non-labellable
```

### Root Cause

The component was using the `htmlFor` attribute on a `<label>` element to associate it with a `<div role="combobox">`:

```jsx
<label htmlFor={inputId}>Select Option</label>
<div id={inputId} role="combobox">...</div>
```

According to [HTML specification](https://html.spec.whatwg.org/multipage/forms.html#the-label-element), only certain form elements can be associated with a label using the `for` attribute:
- `<button>`
- `<input>` (except `type="hidden"`)
- `<keygen>` (deprecated)
- `<meter>`
- `<output>`
- `<progress>`
- `<select>`
- `<textarea>`

A `<div>` with `role="combobox"` is **not** in this list, making it "non-labellable" in the traditional HTML sense.

## Solution

Use `aria-labelledby` instead of `htmlFor` to associate the label with the combobox:

```jsx
<label id={labelId}>Select Option</label>
<div 
  id={triggerId}
  role="combobox"
  aria-labelledby={label ? labelId : undefined}
>
  ...
</div>
```

### Changes Made

**File**: `/frontend/src/shared/ui/Select/Select.tsx`

1. **Separated ID generation** (Lines 138-139):
   ```tsx
   const labelId = React.useId();  // For label element
   const triggerId = React.useId(); // For combobox element
   ```

2. **Updated label element** (Lines 256-260):
   ```tsx
   <label id={labelId} className="cyber-select__label">
     {label}
     {required && <span className="cyber-select__required" aria-hidden="true"> *</span>}
   </label>
   ```
   - Changed from `htmlFor={inputId}` to `id={labelId}`
   - Label now uses `id` instead of `htmlFor`

3. **Updated combobox element** (Lines 264-276):
   ```tsx
   <div
     id={triggerId}
     role="combobox"
     aria-labelledby={label ? labelId : undefined}
     aria-describedby={
       isInvalid ? `${triggerId}-error` : helperText ? `${triggerId}-helper` : undefined
     }
   >
   ```
   - Changed from `id={inputId}` to `id={triggerId}`
   - Added `aria-labelledby={label ? labelId : undefined}` to associate with label
   - Updated `aria-describedby` to use `${triggerId}-error/helper`

4. **Updated helper/error IDs** (Lines 359-369):
   ```tsx
   <p id={`${triggerId}-error`} className="cyber-select__error" role="alert">
   <p id={`${triggerId}-helper`} className="cyber-select__helper">
   ```
   - Changed from `inputId` to `triggerId` for consistency

## ARIA Best Practices

### When to use `aria-labelledby`

✅ **Use `aria-labelledby` when**:
- Associating text with non-form elements (div, span, etc.)
- Associating multiple labels with a single element
- The associated element has a semantic role (combobox, listbox, etc.)

❌ **Don't use `htmlFor` when**:
- The target element is not a labellable form element
- The target is a `<div>` or `<span>` with an ARIA role

### Example Pattern

```jsx
// ✅ Correct: aria-labelledby for non-form elements
<label id={labelId}>Label Text</label>
<div 
  role="combobox"
  aria-labelledby={labelId}
  aria-describedby={descriptionId}
>
  ...
</div>
<p id={descriptionId}>Helper text</p>

// ❌ Incorrect: htmlFor with non-labellable element
<label htmlFor={triggerId}>Label Text</label>
<div id={triggerId} role="combobox">
  ...
</div>
```

## Test Results

All 39 tests passing:
- ✅ Rendering tests (4)
- ✅ Opening/Closing tests (4)
- ✅ Option Selection tests (5)
- ✅ Disabled Options tests (2)
- ✅ Searchable tests (4)
- ✅ Disabled State tests (4)
- ✅ Required tests (1)
- ✅ Error State tests (3)
- ✅ Helper Text tests (2)
- ✅ Keyboard Navigation tests (4)
- ✅ Custom ClassName tests (1)
- ✅ Accessibility tests (4)
- ✅ Memoization tests (1)

### Key Accessibility Test

The test that was previously failing now passes:

```tsx
it('should render with label', () => {
  render(<Select label="Select Option" options={mockOptions} />);
  expect(screen.getByLabelText('Select Option')).toBeInTheDocument();
});
```

This test uses `getByLabelText`, which requires proper label association via:
1. Native `<label for="...">` with labellable element
2. OR `aria-labelledby` with any element
3. OR `aria-label` attribute

Our fix uses option #2 (`aria-labelledby`), which is the correct approach for combobox components.

## Accessibility Improvements

### Before Fix
- ⚠️ Warning: "non-labellable element" in console
- ❌ Test failure: `getByLabelText` couldn't find element
- ⚠️ Screen readers might not announce label correctly
- ⚠️ Not following ARIA best practices

### After Fix
- ✅ No warnings in console
- ✅ All tests passing (39/39)
- ✅ Screen readers properly announce: "Select Option, combobox"
- ✅ Follows ARIA Authoring Practices 1.2
- ✅ Compatible with assistive technologies

## Resources

- [ARIA Authoring Practices Guide - Combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/)
- [HTML Label Element Specification](https://html.spec.whatwg.org/multipage/forms.html#the-label-element)
- [MDN: Using ARIA: aria-labelledby](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-labelledby)
- [WCAG 2.1 - Understanding Label in Name](https://www.w3.org/WAI/WCAG21/Understanding/label-in-name)

## Impact

- **Breaking Changes**: None (internal implementation only)
- **Visual Changes**: None
- **Behavioral Changes**: None
- **Accessibility**: ✅ Improved (removes warning, ensures proper AT support)
- **Test Coverage**: ✅ All tests passing

---

**Reviewed by**: Claude Code  
**Files Modified**: 1 (`Select.tsx`)  
**Tests Fixed**: 1 (`Select.test.tsx` - "should render with label")
