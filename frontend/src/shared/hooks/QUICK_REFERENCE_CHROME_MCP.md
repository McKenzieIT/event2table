# useChromeMCPCompatibleInput - Quick Reference

## 🚀 30-Second Setup

```tsx
import { useChromeMCPCompatibleInput } from '@shared/hooks';

const { values, handleChange, register } = useChromeMCPCompatibleInput({
  initialValues: { name: '', email: '' }
});

// Use in your JSX
<Input
  value={values.name}
  onChange={(e) => handleChange('name', e.target.value)}
  ref={register('name')}
/>
```

## 📋 Common Patterns

### Pattern 1: Simple Form
```tsx
const { values, handleChange, register } = useChromeMCPCompatibleInput({
  initialValues: { username: '', password: '' }
});
```

### Pattern 2: With Change Callback
```tsx
const { values, handleChange, register } = useChromeMCPCompatibleInput({
  initialValues: { email: '' },
  onValuesChange: (values) => console.log('Changed:', values)
});
```

### Pattern 3: With Reset
```tsx
const { values, handleChange, register, resetValues } = useChromeMCPCompatibleInput({
  initialValues: { name: '' }
});

// Reset to initial values
resetValues();

// Reset to new values
resetValues({ name: 'John' });
```

### Pattern 4: Type-Safe Fields
```tsx
type FormFields = 'name' | 'email' | 'phone';
const { values, handleChange, register } = useChromeMCPForm<FormFields>({
  initialValues: { name: '', email: '', phone: '' }
});
```

## 🎯 Return Values

| Property | Type | Usage |
|----------|------|-------|
| `values` | `T` | Current form values |
| `handleChange` | `(field, value) => void` | Update field value |
| `register` | `(field) => RefObject` | Get ref for field |
| `resetValues` | `(values?) => void` | Reset form |
| `getDomValue` | `(field) => string` | Get DOM value |
| `syncFromDom` | `() => void` | Manual sync |

## ⚡ Before vs After

### Before (60 lines)
```tsx
const [values, setValues] = useState({ name: '' });
const nameRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  if (!nameRef.current) return;
  const domValue = nameRef.current.value;
  if (domValue !== values.name) {
    setValues(prev => ({ ...prev, name: domValue }));
  }
}, [values.name]);

<input
  value={values.name}
  onChange={(e) => setValues({...values, name: e.target.value})}
  ref={nameRef}
/>
```

### After (10 lines)
```tsx
const { values, handleChange, register } = useChromeMCPCompatibleInput({
  initialValues: { name: '' }
});

<input
  value={values.name}
  onChange={(e) => handleChange('name', e.target.value)}
  ref={register('name')}
/>
```

## 🔧 Troubleshooting

### Problem: Values not syncing
**Solution**: Attach ref to input element
```tsx
<input ref={register('name')} /> {/* ✅ Correct */}
```

### Problem: TypeScript errors
**Solution**: Use `useChromeMCPForm` helper
```tsx
type Fields = 'name' | 'email';
const { values } = useChromeMCPForm<Fields>({...});
```

### Problem: Performance issues
**Solution**: Disable sync if not needed
```tsx
const { values } = useChromeMCPCompatibleInput({
  enableDomSync: false
});
```

## 📚 Full Documentation

See: `frontend/src/shared/hooks/README_CHROME_MCP.md`

## 🎓 When to Use

✅ **Use when**:
- Form inputs need Chrome MCP compatibility
- Multiple form fields to manage
- Need automatic DOM → State sync
- Want type-safe field access

❌ **Don't use when**:
- Read-only fields
- Uncontrolled components
- Non-input elements
- Single input only

## 🔗 Related Files

- Implementation: `frontend/src/shared/hooks/useChromeMCPCompatibleInput.ts`
- Documentation: `frontend/src/shared/hooks/README_CHROME_MCP.md`
- Example: `frontend/src/event-builder/components/modals/NodeConfigModal.refactored.tsx`

---

**Last Updated**: 2026-03-13
**Version**: 1.0.0
