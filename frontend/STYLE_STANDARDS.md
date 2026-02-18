# Frontend Style Standards

## CSS Variables

Always use CSS variables instead of hardcoded colors:

### Primary Colors
```css
var(--color-primary)    /* Cyan: #06B6D4 */
var(--color-secondary) /* Blue: #3B82F6 */
var(--color-success)    /* Green: #10B981 */
var(--color-error)      /* Red: #EF4444 */
var(--color-warning)    /* Yellow: #F59E0B */
```

### Event Builder Tokens
```css
var(--en-field-base)   /* #06B6D4 - 基础字段 */
var(--en-field-param)  /* #8B5CF6 - 参数字段 */
var(--en-field-derived)/* #10B981 - 派生字段 */
```

### Usage in JSX
```jsx
// ✅ Good - Use CSS variables
<div style={{ color: 'var(--color-primary)' }}>

// ❌ Bad - Hardcoded colors
<div style={{ color: '#06B6D4' }}>
```

## Duplicate Animations

Avoid duplicate keyframe definitions. Use centralized animations:

### Available Animations
Import from `src/styles/event-builder-animations.css`:
- `fadeIn`, `fadeOut`
- `slideIn`, `slideOut`, `slideDown`, `slideUp`
- `scaleIn`, `scaleOut`, `scaleUp`
- `pulse`, `glow`, `bounce`
- `shimmer`, `skeleton-loading`
- `toastSlideIn`, `toastSlideOut`

### Usage
```css
/* ✅ Good - Use animation token */
animation: var(--animation-fade-in);

/* ❌ Bad - Duplicate keyframes */
@keyframes fadeIn { ... }
```

## Button System

Use the shared Button component:

```jsx
// ✅ Good - Use shared Button
import Button from '@/shared/ui/Button';
<Button variant="cyber">Click</Button>

// ❌ Bad - Duplicate button styles
<button className="cyber-button btn">Click</button>
```

## Card System

Use the shared Card component:

```jsx
// ✅ Good - Use shared Card  
import Card from '@/shared/ui/Card';
<Card>Content</Card>

// ❌ Bad - Multiple card styles
<div className="card cyber-card stat-card">Content</div>
```

## ESLint Rules

The following rules help enforce these standards:

- `no-hardcoded-colors/no-hardcoded-colors` - Warns about hardcoded color values in JSX

Run linting:
```bash
npm run lint
```
