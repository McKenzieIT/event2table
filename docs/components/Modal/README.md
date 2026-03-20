# Modal Component

## Overview

The Modal component provides a flexible dialog overlay for displaying content that requires user attention or input.

## Features

- **Multiple Sizes**: small (400px), medium (600px), large (800px), full-screen
- **Keyboard Support**: ESC key to close, Tab navigation
- **Backdrop Options**: Click to close or dismiss
- **Customizable Content**: Header, body, and footer slots
- **Animation**: Smooth open/close transitions
- **Accessibility**: ARIA attributes and focus management

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `isOpen` | `boolean` | `false` | Controls modal visibility |
| `onClose` | `() => void` | - | Callback when modal is closed |
| `title` | `string` | - | Modal title (optional) |
| `size` | `'small' \| 'medium' \| 'large' \| 'full'` | `'medium'` | Modal size |
| `closeOnBackdropClick` | `boolean` | `true` | Close when clicking backdrop |
| `closeOnEsc` | `boolean` | `true` | Close when pressing ESC |
| `showCloseButton` | `boolean` | `true` | Show close button in header |
| `children` | `ReactNode` | - | Modal content |

## Usage Examples

### Basic Modal

```tsx
import { Modal } from '@ui-components/Modal';

function Example() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>Open Modal</button>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <p>This is a basic modal</p>
      </Modal>
    </>
  );
}
```

### Modal with Title and Actions

```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  size="small"
>
  <p>Are you sure you want to proceed?</p>
  <div className="flex gap-2 justify-end">
    <button onClick={() => setIsOpen(false)}>Cancel</button>
    <button onClick={handleConfirm}>Confirm</button>
  </div>
</Modal>
```

### Full-Screen Modal

```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  size="full"
>
  <h2>Full-Screen Content</h2>
  {/* Large content here */}
</Modal>
```

## Accessibility

- Focus is trapped within the modal when open
- First focusable element receives focus on open
- Focus returns to trigger element on close
- ARIA attributes: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`

## Best Practices

- Use modals sparingly - consider inline content first
- Provide clear close actions
- Ensure modal content is scannable
- Test keyboard navigation
- Keep modal content concise
