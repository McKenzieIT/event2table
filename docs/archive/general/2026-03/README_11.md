# Form Component

## Overview

The Form component provides a comprehensive form solution with built-in validation, error handling, and accessibility support.

## Features

- **Field-Level Validation**: Individual field validation rules
- **Form-Level Validation**: Cross-field validation
- **Error Handling**: Automatic error display and management
- **Accessibility**: ARIA labels, error announcements
- **Integration**: Works seamlessly with react-hook-form
- **Type Safety**: Full TypeScript support

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `onSubmit` | `(data: T) => void \| Promise<void>` | - | Form submission handler |
| `defaultValues` | `Partial<T>` | - | Initial form values |
| `validationSchema` | `Schema` | - | Validation schema (Zod) |
| `children` | `ReactNode` | - | Form fields and content |

## Form Field Props

Common props for form field components:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` | - | Field name (required) |
| `label` | `string` | - | Field label |
| `required` | `boolean` | `false` | Is field required |
| `placeholder` | `string` | - | Placeholder text |
| `disabled` | `boolean` | `false` | Is field disabled |

## Usage Examples

### Basic Form

```tsx
import { Form, Input, Button } from '@ui-components/Form';

function Example() {
  const handleSubmit = (data) => {
    console.log(data);
  };

  return (
    <Form onSubmit={handleSubmit} defaultValues={{ name: '', email: '' }}>
      <Input name="name" label="Name" required />
      <Input name="email" label="Email" type="email" required />
      <Button type="submit">Submit</Button>
    </Form>
  );
}
```

### Form with Validation

```tsx
import { Form, Input } from '@ui-components/Form';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

function Example() {
  return (
    <Form
      onSubmit={handleSubmit}
      validationSchema={schema}
      defaultValues={{ email: '', password: '' }}
    >
      <Input name="email" label="Email" type="email" required />
      <Input name="password" label="Password" type="password" required />
      <Button type="submit">Login</Button>
    </Form>
  );
}
```

### Form with Error Handling

```tsx
<Form onSubmit={handleSubmit}>
  <Input
    name="email"
    label="Email"
    type="email"
    required
    helperText="We'll never share your email"
  />
  {errors.email && (
    <p className="error-text">{errors.email.message}</p>
  )}
</Form>
```

## Validation

### Built-in Validators

- `required`: Field must have a value
- `email`: Valid email format
- `min`: Minimum value/length
- `max`: Maximum value/length
- `pattern`: Regex pattern matching

### Custom Validation

```tsx
const schema = z.object({
  password: z.string()
    .min(8, 'At least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain number'),
});
```

## Accessibility

- Proper labeling for all fields
- Error announcements for screen readers
- Keyboard navigation support
- ARIA attributes: `aria-invalid`, `aria-describedby`, `aria-required`

## Best Practices

- Group related fields with fieldsets
- Provide clear error messages
- Use appropriate input types
- Test with screen readers
- Keep forms concise and focused
- Provide real-time validation feedback
