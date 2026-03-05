# RequireGameContext Component - Usage Guide

## Overview

The `RequireGameContext` component provides a unified "please select a game first" prompt for pages that require a game context. It improves UX by clearly informing users why they cannot access certain features.

## Files Created

- **Component**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/components/RequireGameContext.tsx`
- **Styles**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/components/RequireGameContext.css`
- **Export**: Added to `/Users/mckenzie/Documents/event2table/frontend/src/shared/components/index.ts`

## Installation

The component is already exported from `@shared/components`, so you can import it directly:

```typescript
import { RequireGameContext } from '@shared/components';
```

## Usage Examples

### Example 1: Event Node Builder

```typescript
import { RequireGameContext } from '@shared/components';
import { useOutletContext } from 'react-router-dom';

function EventNodeBuilder() {
  const { currentGame } = useOutletContext<{ currentGame?: Game }>();

  return (
    <RequireGameContext gameId={currentGame?.gid}>
      {/* Your existing Event Node Builder content */}
      <div className="event-node-builder">
        {/* ... */}
      </div>
    </RequireGameContext>
  );
}
```

### Example 2: Canvas

```typescript
import { RequireGameContext } from '@shared/components';
import { useOutletContext } from 'react-router-dom';

function Canvas() {
  const { currentGame } = useOutletContext<{ currentGame?: Game }>();

  return (
    <RequireGameContext gameId={currentGame?.gid}>
      {/* Your existing Canvas content */}
      <div className="canvas">
        {/* ... */}
      </div>
    </RequireGameContext>
  );
}
```

### Example 3: With Custom Game Context

If you store game context differently:

```typescript
import { RequireGameContext } from '@shared/components';
import { useCurrentGame } from '@/hooks/useCurrentGame';

function MyFeaturePage() {
  const { currentGame } = useCurrentGame();

  return (
    <RequireGameContext gameId={currentGame?.gid}>
      {/* Feature content */}
    </RequireGameContext>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `children` | `React.ReactNode` | Yes | Content to render if game context exists |
| `gameId` | `string \| number \| null \| undefined` | No | Game ID to check. Shows prompt if falsy |

## Behavior

### When `gameId` is provided:
- Renders the `children` content normally

### When `gameId` is `null`, `undefined`, or empty string:
- Displays a centered prompt card with:
  - 🎮 Icon and title "请先选择游戏"
  - Description: "您需要先选择一个游戏才能使用此功能。"
  - "前往游戏列表" button that navigates to `/games`

## Styling

The component uses:
- `.glass-card` class for the glassmorphism effect (already defined in your app)
- CSS variables: `--color-primary`, `--color-text-secondary`
- Responsive layout with flexbox centering

## Customization

If you need to customize the prompt message or styling, you can:

1. **Modify the component directly** (if changes are app-wide):
   ```typescript
   // Edit RequireGameContext.tsx
   <h2>🎮 Custom Title</h2>
   <p>Custom description here.</p>
   ```

2. **Extend the component** (for page-specific customization):
   ```typescript
   function CustomRequireGameContext({ children, gameId }: RequireGameContextProps) {
     if (!gameId) {
       return (
         <div className="custom-prompt">
           {/* Custom prompt */}
         </div>
       );
     }
     return <>{children}</>;
   }
   ```

## Testing

To test the component:

1. **Without game context**:
   - Visit `/event-builder` or `/canvas` without selecting a game
   - Should see the prompt card

2. **With game context**:
   - Select a game first
   - Visit the pages
   - Should see normal content

## TypeScript Support

The component is fully typed with TypeScript:

```typescript
interface RequireGameContextProps {
  children: React.ReactNode;
  gameId?: string | number | null;
}
```

## Migration Checklist

To add this component to existing pages:

- [ ] Import `RequireGameContext` from `@shared/components`
- [ ] Identify where `currentGame` or `game_gid` is accessed
- [ ] Wrap the page content with `<RequireGameContext gameId={...}>`
- [ ] Remove any existing "no game selected" handling (if redundant)
- [ ] Test the page with and without game context
- [ ] Verify navigation to `/games` works correctly

## Related Components

- `NavLinkWithGameContext` - Similar functionality for navigation links
- `SelectGamePrompt` - Alternative prompt component in `@shared/ui`
- `ErrorBoundary` - Error handling wrapper

## Benefits

1. **Consistent UX**: Unified "no game selected" prompt across all pages
2. **Clear Communication**: Users understand why they can't access features
3. **Easy Integration**: Just wrap existing content
4. **Type-Safe**: Full TypeScript support
5. **Reusable**: Can be used in any game-dependent feature
