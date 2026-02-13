# @shared/ui - Cyberpunk Lab Component Library

Production-ready React component library with a refined cyberpunk lab aesthetic.

## Design Philosophy

**Theme**: "Refined Cyberpunk Lab" - Conservative, professional tech aesthetic with subtle cyberpunk elements

### Core Design Principles

1. **Traditional Grid Layout**: 12-column grid system, not asymmetric
2. **Subtle Animations**: Slide-up fade-in (not holographic, to avoid performance risks)
3. **Hover-First Interactions**: Glow effects only on hover (not continuous pulse)
4. **Professional Aesthetic**: Refined tech look, suitable for data tools
5. **Dark Theme Optimized**: OLED-optimized black backgrounds with cyan accents

### Color Palette

| Role | Color | Usage |
|------|-------|-------|
| Primary (Cyan) | `#06B6D4` | CTAs, active states, links |
| Background | `#000000` | Main background (OLED-optimized) |
| Surface | `rgba(15, 23, 42, 0.6)` | Cards, modals |
| Text Primary | `#F1F5F9` | Headlines, important text |
| Text Secondary | `#94A3B8` | Labels, descriptions |
| Text Tertiary | `#64748B` | Disabled states |
| Success | `#22C55E` | Success states |
| Warning | `#F59E0B` | Warning states |
| Danger | `#EF4444` | Error states |

## Installation

```bash
# Components are already included in the project
# Import from @shared/ui
```

## Usage

```javascript
import { Button, Card, Input, Table, Modal, Badge } from '@shared/ui';

function MyPage() {
  return (
    <Card>
      <Card.Header>
        <Card.Title>Data Generator</Card.Title>
      </Card.Header>
      <Card.Body>
        <Input label="Game Name" placeholder="Enter name..." />
        <Button variant="primary">Generate</Button>
      </Card.Body>
    </Card>
  );
}
```

## Components

### Button

Primary action buttons with hover glow effects.

**Variants**: `primary`, `secondary`, `ghost`, `danger`
**Sizes**: `sm`, `md`, `lg`

```jsx
<Button variant="primary" onClick={handleClick}>
  Generate HQL
</Button>

<Button variant="danger" loading={isLoading}>
  Delete
</Button>

<Button size="lg" icon={Icon}>
  With Icon
</Button>
```

**Features**:
- Hover glow effect (cyan for primary, red for danger)
- Loading spinner
- Icon support
- Disabled state

### Card

Glassmorphism cards with subtle borders and shadows.

**Variants**: `default`, `outlined`, `elevated`
**Padding**: `sm`, `md`, `lg`, `none`

```jsx
<Card hoverable glowing>
  <Card.Header>
    <Card.Title>Card Title</Card.Title>
  </Card.Header>
  <Card.Body>
    Card content goes here
  </Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

**Features**:
- Glassmorphism effect (backdrop-filter blur)
- Hover lift effect
- Optional continuous glow
- Subcomponents: Header, Body, Footer, Title

### Input

Form inputs with focus glow and validation states.

**Types**: `text`, `password`, `number`, `email`

```jsx
<Input
  label="Game Name"
  placeholder="Enter game name..."
  value={value}
  onChange={(e) => setValue(e.target.value)}
  helperText="This field is required"
  required
/>

<Input
  label="Password"
  type="password"
  error="Password must be at least 8 characters"
/>
```

**Features**:
- Focus glow effect (cyan)
- Validation states (error, success)
- Helper text
- Icon support
- Required indicator

### Table

Data tables with subtle row hover effects.

**Variants**: `default`, `bordered`, `compact`
**Sizes**: `sm`, `md`, `lg`

```jsx
<Table striped hoverable>
  <Table.Header>
    <Table.Row>
      <Table.Head sortable>Game Name</Table.Head>
      <Table.Head align="center">Events</Table.Head>
      <Table.Head align="right">Last Update</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {games.map((game) => (
      <Table.Row key={game.id}>
        <Table.Cell>{game.name}</Table.Cell>
        <Table.Cell align="center">{game.events}</Table.Cell>
        <Table.Cell align="right">{game.updatedAt}</Table.Cell>
      </Table.Row>
    ))}
  </Table.Body>
</Table>
```

**Features**:
- Zebra striping (optional)
- Subtle row hover (background color change, not full highlight)
- Sortable columns with indicators
- Responsive overflow
- Clickable rows

### Modal

Dialog modals with backdrop blur and slide-up animation.

**Sizes**: `sm`, `md`, `lg`, `xl`, `full`
**Variants**: `default`, `danger`, `warning`

```jsx
const [isOpen, setIsOpen] = useState(false);

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Delete"
  variant="danger"
  showFooter
  footerActions={
    <>
      <Button variant="ghost" onClick={() => setIsOpen(false)}>Cancel</Button>
      <Button variant="danger" onClick={handleDelete}>Delete</Button>
    </>
  }
>
  <p>Are you sure you want to delete this game?</p>
  <p>This action cannot be undone.</p>
</Modal>
```

**Features**:
- Backdrop blur effect
- Slide-up entrance animation
- Focus trap
- ESC key to close
- Custom footer actions
- Mobile responsive (bottom sheet)

### Badge

Status badges with glowing accents.

**Variants**: `default`, `primary`, `success`, `warning`, `danger`, `info`

```jsx
<Badge variant="success" dot>Active</Badge>
<Badge variant="warning">Draft</Badge>
<Badge variant="primary" pill>New</Badge>
```

**Features**:
- Colored dot indicator
- Pill shape (optional)
- Hover glow effect
- Status-based colors

## Component Showcase

View all components in the interactive showcase:

```bash
# Access at: /component-showcase
import ComponentShowcase from '@shared/ui/__showcase__/ComponentShowcase';
```

The showcase demonstrates:
- All component variants
- Interactive states
- Animation timing
- Usage examples

## Theming

### CSS Custom Properties

Override theme tokens in your application:

```css
:root {
  /* Colors */
  --color-primary: #06B6D4;
  --color-primary-light: #22D3EE;

  /* Backgrounds */
  --bg-primary: #000000;
  --bg-secondary: rgba(15, 23, 42, 0.6);
  --bg-tertiary: rgba(15, 23, 42, 0.8);

  /* Text */
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-tertiary: #64748B;

  /* Borders */
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-default: rgba(6, 182, 212, 0.2);
}
```

### Dark Mode

All components are dark-mode optimized by default. To support light mode:

```css
[data-theme="light"] {
  --bg-primary: #FFFFFF;
  --text-primary: #0F172A;
  /* ... override other tokens */
}
```

## Best Practices

### 1. Component Composition

Use subcomponents for cleaner code:

```jsx
// Good
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Body>Content</Card.Body>
</Card>

// Avoid
<Card className="custom-header">...</Card>
```

### 2. Variant Selection

- **Primary**: Main CTAs (one per page)
- **Secondary**: Alternative actions
- **Ghost**: Low-emphasis actions
- **Danger**: Destructive actions

### 3. Loading States

Always provide feedback for async actions:

```jsx
const [loading, setLoading] = useState(false);

const handleClick = async () => {
  setLoading(true);
  try {
    await apiCall();
  } finally {
    setLoading(false);
  }
};

<Button loading={loading} onClick={handleClick}>
  Submit
</Button>
```

### 4. Accessibility

All components support:
- Keyboard navigation
- ARIA attributes
- Focus management
- Screen reader support

### 5. Performance

- Animations use CSS transforms (GPU-accelerated)
- No continuous animations (hover-only)
- Lazy loading for modals
- Virtual scrolling for large tables

## Migration Guide

### From Existing Components

1. **Identify the component type** (Button, Card, etc.)
2. **Import from @shared/ui**
3. **Update props** to match new API
4. **Verify styling and interactions**

Example migration:

```jsx
// Before
<button className="btn btn-primary" onClick={action}>
  Click
</button>

// After
import { Button } from '@shared/ui';

<Button variant="primary" onClick={action}>
  Click
</Button>
```

## File Structure

```
@shared/ui/
├── Button/
│   ├── Button.jsx
│   └── Button.css
├── Card/
│   ├── Card.jsx
│   └── Card.css
├── Input/
│   ├── Input.jsx
│   └── Input.css
├── Table/
│   ├── Table.jsx
│   └── Table.css
├── Modal/
│   ├── Modal.jsx
│   └── Modal.css
├── Badge/
│   ├── Badge.jsx
│   └── Badge.css
├── __showcase__/
│   ├── ComponentShowcase.jsx
│   └── ComponentShowcase.css
├── index.ts
└── README.md
```

## Contributing

### Adding New Components

1. Create component directory: `ComponentName/`
2. Create `ComponentName.jsx` and `ComponentName.css`
3. Follow existing patterns (variants, sizes, forwardRef)
4. Add to `index.ts` exports
5. Add showcase example
6. Update this README

### Component Template

```jsx
import React from 'react';
import './ComponentName.css';

const ComponentName = React.forwardRef(({
  // props
}, ref) => {
  return (
    <div ref={ref} className="cyber-component">
      {/* implementation */}
    </div>
  );
});

export default ComponentName;
```

## Performance Notes

- **Animation Performance**: All animations use `transform` and `opacity` (GPU-accelerated)
- **Bundle Size**: Component library is tree-shakeable
- **Lazy Loading**: Modal uses React Portal for optimal rendering
- **CSS-in-JS**: Using vanilla CSS for better runtime performance

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT

## Credits

Design system based on "Cyberpunk Lab" theme - A refined, professional tech aesthetic with subtle cyberpunk elements.

---

**Version**: 1.0.0
**Last Updated**: 2025-02-11
**Maintainer**: DWD Generator Team
