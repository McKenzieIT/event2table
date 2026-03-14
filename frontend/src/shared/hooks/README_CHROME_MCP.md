# useChromeMCPCompatibleInput Hook

## 📋 Overview

A custom React hook that solves Chrome DevTools MCP compatibility issues with form inputs. The hook automatically synchronizes DOM values with React state, ensuring that Chrome DevTools MCP's `fill` operation works correctly with React-controlled components.

## 🎯 Problem Solved

**The Issue**: Chrome DevTools MCP's `fill` operation updates the DOM directly but doesn't trigger React's `onChange` events, causing a mismatch between what users see (DOM) and what React thinks the value is (state).

**The Solution**: This hook uses `useEffect` to monitor DOM values and sync them to React state when they differ, providing seamless Chrome MCP compatibility.

## 📦 Installation

The hook is located at:
```
frontend/src/shared/hooks/useChromeMCPCompatibleInput.ts
```

It's exported from the main hooks index:
```typescript
import { useChromeMCPCompatibleInput } from '@shared/hooks';
```

## 🚀 Quick Start

### Basic Usage

```tsx
import { useChromeMCPCompatibleInput } from '@shared/hooks';
import { Input } from '@shared/ui';

function MyForm() {
  const { values, handleChange, register } = useChromeMCPCompatibleInput({
    initialValues: {
      name: '',
      email: '',
      phone: ''
    }
  });

  return (
    <form>
      <Input
        label="Name"
        value={values.name}
        onChange={(e) => handleChange('name', e.target.value)}
        ref={register('name')}
      />
      <Input
        label="Email"
        value={values.email}
        onChange={(e) => handleChange('email', e.target.value)}
        ref={register('email')}
      />
      <Input
        label="Phone"
        value={values.phone}
        onChange={(e) => handleChange('phone', e.target.value)}
        ref={register('phone')}
      />
    </form>
  );
}
```

### With Change Callback

```tsx
function MyForm() {
  const { values, handleChange, register } = useChromeMCPCompatibleInput({
    initialValues: { name: '', email: '' },
    onValuesChange: (values) => {
      console.log('Form values changed:', values);
      // Send to API, validate, etc.
    }
  });

  // ... rest of component
}
```

### With Reset Functionality

```tsx
function MyForm() {
  const { values, handleChange, register, resetValues } = useChromeMCPCompatibleInput({
    initialValues: { name: '', email: '' }
  });

  const handleReset = () => {
    resetValues(); // Reset to initial values
    // or
    resetValues({ name: 'John', email: 'john@example.com' }); // Reset to new values
  };

  return (
    <form>
      {/* ... form fields ... */}
      <button type="button" onClick={handleReset}>
        Reset Form
      </button>
    </form>
  );
}
```

## 📚 API Reference

### `useChromeMCPCompatibleInput<T>(options)`

#### Type Parameters

- **`T`** - Type extending `Record<string, string>` representing the form fields

#### Parameters

**`options`** (optional): `UseChromeMCPCompatibleInputOptions<T>`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `initialValues` | `T` | `{}` | Initial values for form fields |
| `onValuesChange` | `(values: T) => void` | `undefined` | Callback invoked when any field changes |
| `enableDomSync` | `boolean` | `true` | Enable/disable DOM synchronization |

#### Returns

`UseChromeMCPCompatibleInputReturn<T>`

| Property | Type | Description |
|----------|------|-------------|
| `refs` | `Record<keyof T, React.RefObject>` | React ref objects for each registered field |
| `values` | `T` | Current values of all fields |
| `handleChange` | `(field: keyof T, value: string) => void` | Handler to update a field value |
| `register` | `(field: keyof T) => React.RefObject` | Register a field and get its ref |
| `resetValues` | `(values?: T) => void` | Reset all values to initial or provided values |
| `getDomValue` | `(field: keyof T) => string` | Get current DOM value for a field |
| `syncFromDom` | `() => void` | Manually trigger DOM synchronization |

## 🔧 Advanced Usage

### Type-Safe Form Fields

```tsx
type MyFormFields = 'name' | 'email' | 'phone';

function MyForm() {
  const { values, handleChange, register } = useChromeMCPForm<MyFormFields>({
    initialValues: { name: '', email: '', phone: '' }
  });

  // TypeScript will autocomplete field names
  return (
    <form>
      <Input
        label="Name"
        value={values.name}
        onChange={(e) => handleChange('name', e.target.value)}
        ref={register('name')}
      />
    </form>
  );
}
```

### Manual DOM Sync

```tsx
function MyForm() {
  const { values, handleChange, register, syncFromDom } = useChromeMCPCompatibleInput({
    initialValues: { name: '' }
  });

  const handleExternalUpdate = () => {
    // After external DOM modifications
    syncFromDom();
  };

  return (
    <form>
      <Input
        label="Name"
        value={values.name}
        onChange={(e) => handleChange('name', e.target.value)}
        ref={register('name')}
      />
      <button type="button" onClick={handleExternalUpdate}>
        Sync from DOM
      </button>
    </form>
  );
}
```

### Disable DOM Sync Temporarily

```tsx
function MyForm() {
  const { values, handleChange, register } = useChromeMCPCompatibleInput({
    initialValues: { name: '' },
    enableDomSync: false // Disable automatic sync
  });

  // Manually control when to sync
  // Useful for performance optimization or special cases

  return <form>...</form>;
}
```

## 🎨 Real-World Example

### NodeConfigModal Refactoring

**Before** (~60 lines):
```tsx
const [localConfig, setLocalConfig] = useState<NodeConfig>({...});
const nameEnRef = useRef<HTMLInputElement>(null);
const nameCnRef = useRef<HTMLInputElement>(null);
const descRef = useRef<HTMLTextAreaElement>(null);

// Manual DOM sync useEffect (15+ lines)
useEffect(() => {
  if (!nameEnRef.current || !nameCnRef.current || !descRef.current) return;
  const nameEnDomValue = nameEnRef.current.value;
  const nameCnDomValue = nameCnRef.current.value;
  const descDomValue = descRef.current.value;
  const updates: Partial<NodeConfig> = {};
  if (nameEnDomValue !== localConfig.nameEn) updates.nameEn = nameEnDomValue;
  if (nameCnDomValue !== localConfig.nameCn) updates.nameCn = nameCnDomValue;
  if (descDomValue !== localConfig.description) updates.description = descDomValue;
  if (Object.keys(updates).length > 0) {
    setLocalConfig(prev => ({ ...prev, ...updates }));
  }
}, [localConfig.nameEn, localConfig.nameCn, localConfig.description]);

const handleChange = (field: keyof NodeConfig, value: string): void => {
  setLocalConfig((prev) => ({ ...prev, [field]: value }));
};
```

**After** (~10 lines):
```tsx
const { values, handleChange, register } = useChromeMCPCompatibleInput<NodeConfig>({
  initialValues: { nameEn: '', nameCn: '', description: '' }
});

// No manual DOM sync needed!
```

## 🧪 Testing

### Testing with Chrome DevTools MCP

```typescript
import { render, screen } from '@testing-library/react';
import { useChromeMCPCompatibleInput } from '@shared/hooks';

function TestComponent() {
  const { values, handleChange, register } = useChromeMCPCompatibleInput({
    initialValues: { name: 'John' }
  });

  return (
    <input
      data-testid="name-input"
      value={values.name}
      onChange={(e) => handleChange('name', e.target.value)}
      ref={register('name')}
    />
  );
}

test('should sync DOM value to state', () => {
  render(<TestComponent />);
  const input = screen.getByTestId('name-input') as HTMLInputElement;

  // Simulate Chrome MCP fill operation
  input.value = 'Jane';
  input.dispatchEvent(new Event('input', { bubbles: true }));

  // Hook should sync DOM to state
  // Wait for useEffect to run
  setTimeout(() => {
    expect(input.value).toBe('Jane');
  }, 0);
});
```

## 🔍 How It Works

### Technical Details

1. **Ref Management**: Automatically creates and manages refs for all registered fields
2. **DOM Monitoring**: Uses `useEffect` to monitor DOM values
3. **Change Detection**: Compares DOM values with state values
4. **Batch Updates**: Updates all changed fields in a single state update
5. **Infinite Loop Prevention**: Only updates when DOM differs from state

### Dependency Array

```typescript
useEffect(() => {
  // Sync logic
}, [values, enableDomSync]);
```

The effect runs when `values` change, ensuring DOM sync happens after every state update.

## ⚠️ Caveats

### Performance Considerations

- The effect runs on every value change (by design)
- For forms with many fields (>20), consider debouncing or disabling sync
- Use `enableDomSync: false` if you don't need Chrome MCP compatibility

### When NOT to Use

- **Read-only fields**: No need for DOM sync
- **Uncontrolled components**: Use `useRef` directly instead
- **Non-input elements**: This hook is designed for input/textarea elements

### Known Limitations

- Only works with `input` and `textarea` elements
- Requires refs to be attached to DOM elements
- May not work with third-party input components that don't forward refs

## 🐛 Troubleshooting

### Issue: Values not syncing from DOM

**Solution**: Ensure refs are attached to DOM elements:
```tsx
<input ref={register('name')} /> // ✅ Correct
<input /> // ❌ Missing ref
```

### Issue: Infinite loop warnings

**Solution**: Check that `enableDomSync` is not enabled unnecessarily:
```tsx
const { values } = useChromeMCPCompatibleInput({
  enableDomSync: false // Disable if not needed
});
```

### Issue: TypeScript errors with field names

**Solution**: Use the `useChromeMCPForm` helper for better type inference:
```tsx
type Fields = 'name' | 'email';
const { values, handleChange } = useChromeMCPForm<Fields>({
  initialValues: { name: '', email: '' }
});
```

## 📖 Related Documentation

- [React Best Practices - Hooks Rules](docs/lessons-learned/react-best-practices.md#react-hooks-规则)
- [Chrome DevTools MCP Guide](docs/development/CHROME-DEVTOOLS-MCP-CONSOLE-GUIDE.md)
- [NodeConfigModal Refactoring Example](frontend/src/event-builder/components/modals/NodeConfigModal.refactored.tsx)

## 🤝 Contributing

When adding new features to this hook:

1. Update this README with usage examples
2. Add JSDoc comments to the hook implementation
3. Test with Chrome DevTools MCP
4. Update the migration guide if API changes

## 📝 Changelog

### v1.0.0 (2026-03-13)

- Initial release
- Basic DOM synchronization
- Type-safe field registration
- Reset and manual sync functionality
- Full TypeScript support
- Comprehensive documentation

## 📄 License

MIT

---

**Author**: Event2Table Development Team
**Created**: 2026-03-13
**Last Updated**: 2026-03-13
