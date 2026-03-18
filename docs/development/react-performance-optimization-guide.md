# React Performance Optimization Guide

**Version**: 1.0.0
**Last Updated**: 2026-03-18
**Target**: 20-30% performance improvement, 70%+ re-render reduction

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Optimization Techniques](#core-optimization-techniques)
3. [Component-Specific Optimizations](#component-specific-optimizations)
4. [Performance Testing](#performance-testing)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Install dependencies
npm install --save-dev @testing-library/react-hooks

# Install performance monitoring tools
npm install --save-dev webpack-bundle-analyzer

# Install virtual scrolling library
npm install react-window
```

### Basic Usage

```typescript
// 1. Wrap components with React.memo
export default memo(MyComponent);

// 2. Use useCallback for event handlers
const handleClick = useCallback(() => {
  console.log('Clicked');
}, []);

// 3. Use useMemo for expensive computations
const filteredItems = useMemo(() => {
  return items.filter(item => item.active);
}, [items]);

// 4. Monitor performance
import { usePerformanceMonitor } from '@shared/utils/performanceMonitor';

function MyComponent() {
  usePerformanceMonitor('MyComponent');
  return <div>...</div>;
}
```

---

## Core Optimization Techniques

### 1. React.memo with Custom Comparison

**When to use**: Components that re-render with the same props

```typescript
// ✅ Good: Custom comparison function
function arePropsEqual(prevProps, nextProps) {
  return (
    prevProps.id === nextProps.id &&
    prevProps.name === nextProps.name &&
    prevProps.data.length === nextProps.data.length
  );
}

export default memo(MyComponent, arePropsEqual);

// ❌ Bad: No comparison (shallow comparison may not work for complex objects)
export default memo(MyComponent);
```

**Performance gain**: 70-80% fewer re-renders

---

### 2. useCallback for Stable References

**When to use**: Event handlers passed to child components

```typescript
// ✅ Good: Stable callback reference
const handleClick = useCallback((id: number) => {
  setSelectedId(id);
}, []); // No dependencies = always same reference

const handleSave = useCallback(async () => {
  await saveData(data);
}, [data]); // Dependencies = recreates only when data changes

// ❌ Bad: Unstable reference (new function on every render)
const handleClick = (id: number) => {
  setSelectedId(id);
};
```

**Performance gain**: 60-70% fewer child re-renders

---

### 3. useMemo for Expensive Computations

**When to use**: Filtering, sorting, statistics calculations

```typescript
// ✅ Good: Memoized filter
const filteredGames = useMemo(() => {
  if (!searchTerm) return games;
  return games.filter(game =>
    game.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [games, searchTerm]);

// ✅ Good: Memoized statistics
const stats = useMemo(() => {
  const totalGames = games.length;
  const totalEvents = games.reduce((sum, game) => sum + game.eventCount, 0);
  return { totalGames, totalEvents };
}, [games]);

// ❌ Bad: Unnecessary memoization for simple values
const count = useMemo(() => items.length, [items]); // Just use items.length directly
```

**Performance gain**: 50-60% faster computations

---

### 4. Virtual Scrolling for Large Lists

**When to use**: Lists with 100+ items

```typescript
import OptimizedVirtualList from '@shared/components/VirtualList/OptimizedVirtualList';

<OptimizedVirtualList
  items={games}
  renderItem={(game) => <GameListItem game={game} />}
  itemHeight={50}
  height={600}
  overscan={5}
/>
```

**Performance gain**: 90%+ faster rendering for 1000+ items

---

### 5. Lazy Loading for Modals

**When to use**: Modal components not shown on initial page load

```typescript
import { LazyGameManagementModal } from '@shared/utils/lazyModals';

function App() {
  return (
    <Suspense fallback={<ModalSpinner />}>
      <LazyGameManagementModal isOpen={isOpen} onClose={handleClose} />
    </Suspense>
  );
}
```

**Performance gain**: 40-50% faster initial page load

---

## Component-Specific Optimizations

### Modal Components

#### GameManagementModalGraphQL

```typescript
// ✅ Debounced search (300ms)
useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedSearchQuery(searchQuery);
  }, 300);

  return () => clearTimeout(timer);
}, [searchQuery]);

// ✅ Memoized game list
const games = useMemo(() => {
  return debouncedSearchQuery ? searchData?.searchGames : data?.games;
}, [debouncedSearchQuery, searchData, data?.games]);

// ✅ Lazy form rendering
{showCreateForm && (
  <MemoizedGameForm
    onSubmit={handleCreateGame}
    onCancel={handleCloseCreateForm}
    loading={creating}
  />
)}
```

**Performance targets**:
- Initial render: < 100ms
- Search response: < 300ms
- Form open: < 50ms

---

#### EventManagementModalGraphQL

```typescript
// ✅ Chrome MCP compatible input handling
const { values: searchValues, handleChange: handleSearchChange } =
  useChromeMCPCompatibleInput<{ searchTerm: string }>({
    initialValues: { searchTerm: '' }
  });

// ✅ Optimized event list filtering
const filteredEvents = useMemo(() => {
  if (!events.length) return [];
  if (searchValues.searchTerm && searchData?.searchEvents) {
    return events; // Already filtered by GraphQL
  }
  return events.filter((event: Event) =>
    event.eventName?.toLowerCase().includes(searchValues.searchTerm.toLowerCase())
  );
}, [events, searchValues.searchTerm, searchData]);
```

**Performance targets**:
- Initial render: < 100ms
- Event selection: < 10ms
- Search response: < 300ms

---

### Canvas Components

#### CustomNode

```typescript
// ✅ Custom comparison for React.memo
function arePropsEqual(prevProps, nextProps) {
  return (
    prevProps.selected === nextProps.selected &&
    prevProps.data.label === nextProps.data.label &&
    prevProps.data.fieldCount === nextProps.data.fieldCount
  );
}

// ✅ Memoized field list (limited to 5 items)
const displayFields = useMemo(() => {
  if (!data.baseFields || data.baseFields.length === 0) return [];
  return data.baseFields.slice(0, 5).map((field, idx) => ({
    id: idx,
    name: field.alias || field.name,
    type: field.type === "param" ? "参数" : "基础"
  }));
}, [data.baseFields]);
```

**Performance targets**:
- Single node render: < 50ms
- Canvas with 100 nodes: < 2000ms
- Selection change: < 10ms

---

### Form Components

#### EventForm

```typescript
// ✅ Chrome MCP compatible input handling
const { values, handleChange, register, resetValues } =
  useChromeMCPCompatibleInput<EventFormData>({
    initialValues: {
      event_name: '',
      event_name_cn: '',
      category_id: '',
      game_gid: effectiveGameGid || '',
      include_in_common_params: '1'
    },
  });

// ✅ Optimized input handling with error clearing
const handleInputChange = React.useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
  const { name, value } = e.target;
  handleChange(name as keyof EventFormData, value);
  if (errors[name as keyof FormErrors]) {
    setErrors(prev => ({ ...prev, [name]: null }));
  }
}, [handleChange, errors]);
```

**Performance targets**:
- Initial render: < 80ms
- Input response: < 16ms (60fps)
- Form submission: < 100ms

---

### List Components

#### GamesListGraphQL

```typescript
// ✅ Memoized search filtering
const filteredGames = useMemo(() => {
  if (!searchTerm) return games;
  return games.filter((game: GameType) =>
    game.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    game.gid?.toString().includes(searchTerm)
  );
}, [games, searchTerm]);

// ✅ Memoized statistics calculation
const stats = useMemo(() => {
  const totalGames = games.length;
  const totalEvents = games.reduce((sum, game) => sum + (game?.eventCount || 0), 0);
  const totalParams = games.reduce((sum, game) => sum + (game?.parameterCount || 0), 0);
  return { totalGames, totalEvents, totalParams };
}, [games]);

// ✅ Stable callback references
const handleGameClick = useCallback((game: GameType) => {
  selectGame({ id: game.gid, gid: game.gid, name: game.name, ods_db: game.odsDb });
  success(`已切换到游戏: ${game.name}`);
}, [selectGame, success]);
```

**Performance targets**:
- Initial render (100 games): < 500ms
- Search filtering (1000 games): < 50ms
- Statistics calculation: < 10ms

---

## Performance Testing

### Unit Tests

```typescript
import { renderHook, act } from '@testing-library/react-hooks';

describe('Performance Tests', () => {
  test('Component should not re-render with same props', () => {
    const renderSpy = jest.fn();
    const MockComponent = React.memo(() => {
      renderSpy();
      return <div>Test</div>;
    });

    const { rerender } = render(<MockComponent />);
    expect(renderSpy).toHaveBeenCalledTimes(1);

    rerender(<MockComponent />);
    expect(renderSpy).toHaveBeenCalledTimes(1); // Should not re-render
  });

  test('Callback should be stable across renders', () => {
    const { result } = renderHook(() => {
      const [count, setCount] = useState(0);
      const handleClick = useCallback(() => setCount(c => c + 1), []);
      return { count, handleClick };
    });

    const firstCallback = result.current.handleClick;

    act(() => {
      result.current.handleClick();
    });

    expect(result.current.handleClick).toBe(firstCallback);
  });
});
```

### Integration Tests

```typescript
test('Large list should render quickly', () => {
  const mockGames = Array.from({ length: 1000 }, (_, i) => ({
    gid: i,
    name: `Game ${i}`,
    odsDb: 'ieu_ods'
  }));

  const startTime = performance.now();
  render(<GamesListGraphQL games={mockGames} />);
  const endTime = performance.now();

  expect(endTime - startTime).toBeLessThan(1000);
});
```

### Performance Monitoring

```typescript
import { usePerformanceMonitor } from '@shared/utils/performanceMonitor';

function MyComponent() {
  usePerformanceMonitor('MyComponent', 16.67); // Warn if render takes > 16.67ms

  return <div>...</div>;
}

// Log performance metrics
import { logPerformanceMetrics } from '@shared/utils/performanceMonitor';

logPerformanceMetrics('MyComponent');
// Output:
// 📊 MyComponent:
//   Render Count: 5
//   Avg Render Time: 12.34ms
//   Last Render Time: 11.23ms
//   Total Render Time: 61.70ms
```

---

## Best Practices

### 1. Profile Before Optimizing

```typescript
// ❌ Bad: Optimizing without profiling
const MyComponent = memo(() => {
  const memoizedValue = useMemo(() => expensiveCalculation(), [deps]);
  return <div>{memoizedValue}</div>;
});

// ✅ Good: Profile first, then optimize bottlenecks
import { usePerformanceMonitor } from '@shared/utils/performanceMonitor';

const MyComponent = () => {
  usePerformanceMonitor('MyComponent');

  // Only memoize if profiling shows it's slow
  const value = expensiveCalculation();

  return <div>{value}</div>;
};
```

### 2. Avoid Premature Memoization

```typescript
// ❌ Bad: Memoizing simple values
const count = useMemo(() => items.length, [items]);
const fullName = useMemo(() => `${firstName} ${lastName}`, [firstName, lastName]);

// ✅ Good: Direct computation for simple values
const count = items.length;
const fullName = `${firstName} ${lastName}`;

// ✅ Good: Memoize only expensive operations
const filteredItems = useMemo(() => {
  return items.filter(item => item.active).sort((a, b) => a.id - b.id);
}, [items]);
```

### 3. Use Custom Comparison Functions

```typescript
// ❌ Bad: Shallow comparison for complex objects
export default memo(MyComponent);

// ✅ Good: Custom comparison for specific props
function arePropsEqual(prevProps, nextProps) {
  return (
    prevProps.id === nextProps.id &&
    prevProps.data.length === nextProps.data.length
  );
}

export default memo(MyComponent, arePropsEqual);
```

### 4. Optimize GraphQL Queries

```typescript
// ❌ Bad: Fetching all fields
const GET_GAMES = gql`
  query GetGames {
    games {
      gid
      name
      odsDb
      eventCount
      parameterCount
      description
      createdAt
      updatedAt
      createdBy
      updatedBy
    }
  }
`;

// ✅ Good: Fetching only required fields
const GET_GAMES = gql`
  query GetGames {
    games {
      gid
      name
      odsDb
      eventCount
      parameterCount
    }
  }
`;
```

### 5. Use Code Splitting

```typescript
// ❌ Bad: Loading all components upfront
import GameManagementModal from './features/games/GameManagementModalGraphQL';
import EventManagementModal from './features/events/EventManagementModalGraphQL';

// ✅ Good: Lazy loading modals
import { LazyGameManagementModal, LazyEventManagementModal } from '@shared/utils/lazyModals';
```

---

## Troubleshooting

### Issue: Component Still Re-renders Despite memo()

**Cause**: Props are changing (new object/array references)

**Solution**:
```typescript
// ❌ Bad: Creating new object on every render
<Component data={{ id: 1, name: 'Test' }} />

// ✅ Good: Using useMemo for props
const data = useMemo(() => ({ id: 1, name: 'Test' }), []);
<Component data={data} />

// ✅ Good: Using useState for stable data
const [data] = useState({ id: 1, name: 'Test' });
<Component data={data} />
```

---

### Issue: Callback Causes Child Re-renders

**Cause**: Callback reference changes on every render

**Solution**:
```typescript
// ❌ Bad: Inline function
<ChildComponent onClick={() => handleClick(id)} />

// ✅ Good: useCallback with stable dependencies
const handleClick = useCallback((id: number) => {
  setSelectedId(id);
}, []);
<ChildComponent onClick={handleClick} />
```

---

### Issue: Slow List Rendering

**Cause**: Rendering all items at once

**Solution**:
```typescript
// ❌ Bad: Rendering all items
{items.map(item => <ListItem key={item.id} item={item} />)}

// ✅ Good: Virtual scrolling
<OptimizedVirtualList
  items={items}
  renderItem={(item) => <ListItem item={item} />}
  itemHeight={50}
  height={600}
/>
```

---

### Issue: Memory Leaks

**Cause**: Not cleaning up subscriptions/timers

**Solution**:
```typescript
// ❌ Bad: Not cleaning up
useEffect(() => {
  const timer = setInterval(() => {
    console.log('Tick');
  }, 1000);
}, []);

// ✅ Good: Cleaning up
useEffect(() => {
  const timer = setInterval(() => {
    console.log('Tick');
  }, 1000);

  return () => clearInterval(timer);
}, []);
```

---

## Performance Checklist

### Component Level
- [ ] Wrapped with React.memo (if needed)
- [ ] Custom comparison function (if needed)
- [ ] useCallback for event handlers
- [ ] useMemo for expensive computations
- [ ] Chrome MCP compatible input handling
- [ ] Performance monitoring enabled

### List Level
- [ ] Virtual scrolling for 100+ items
- [ ] Memoized filtering/sorting
- [ ] Pagination implemented
- [ ] Lazy loading for images

### GraphQL Level
- [ ] Only fetching required fields
- [ ] Using cache-first policy
- [ ] Optimistic updates for mutations
- [ ] Query batching implemented

### Bundle Level
- [ ] Code splitting for routes
- [ ] Lazy loading for modals
- [ ] Tree shaking enabled
- [ ] Bundle size monitored

---

## Resources

### Official Documentation
- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [React.memo Reference](https://react.dev/reference/react/memo)
- [useCallback Reference](https://react.dev/reference/react/useCallback)
- [useMemo Reference](https://react.dev/reference/react/useMemo)

### Tools
- [React DevTools Profiler](https://react.dev/learn/react-developer-tools)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance)
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [react-window](https://github.com/bvaughn/react-window)

### Internal Resources
- [Performance Optimization Report](/output/REACT-PERFORMANCE-OPTIMIZATION-FINAL-REPORT.md)
- [React Best Practices](/docs/lessons-learned/react-best-practices.md)
- [Testing Guide](/docs/testing/react-testing-guide.md)

---

**Last Updated**: 2026-03-18
**Maintained By**: Event2Table Development Team
