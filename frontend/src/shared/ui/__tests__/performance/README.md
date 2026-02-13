# @shared/ui Performance Test Suite

Comprehensive performance testing suite for the @shared/ui component library, based on Vercel React Best Practices.

## Overview

This test suite validates that the component library meets production-ready performance standards through:

1. **Re-render Tests** - Validates React.memo effectiveness
2. **Rendering Performance Tests** - Measures rendering times for large component counts
3. **Memory Leak Tests** - Detects memory leaks in complex components
4. **Bundle Size Analysis** - Analyzes the bundle size impact

## Test Files

### 1. RerenderTest.tsx
Tests React.memo optimization by measuring component re-renders when parent components update.

**Tests:**
- Button: Should not re-render when parent state changes
- Card: Sub-components should not cascade re-renders
- Input: Should only re-render when value changes
- Badge: Should not re-render when parent updates
- Table: Rows should not re-render on sort changes

**Run:**
```bash
npm test -- RerenderTest
```

### 2. RenderingPerformanceTest.tsx
Measures actual rendering times using `performance.mark()`.

**Benchmarks:**
- Button: 100 components < 100ms, 1000 components < 500ms
- Card: 50 cards < 200ms
- Input: 100 inputs < 150ms
- Table: 100 rows < 200ms, sort < 50ms
- Badge: 500 badges < 100ms
- Modal: mount < 50ms
- Dashboard: complex UI < 300ms

**Run:**
```bash
npm test -- RenderingPerformanceTest
```

### 3. MemoryLeakTest.tsx
Detects memory leaks through event listener cleanup and proper unmounting.

**Checks:**
- Modal event listener cleanup
- Body scroll restoration
- Focus restoration
- Table row cleanup
- Card child unmounting
- Strict Mode compatibility
- Ref cleanup

**Run:**
```bash
npm test -- MemoryLeakTest
```

### 4. BundleSizeTest.ts
Analyzes bundle size and generates recommendations.

**Output:**
- Component source sizes
- Bundle sizes
- Total size analysis
- Optimization recommendations

**Run:**
```bash
npx tsx src/shared/ui/__tests__/performance/BundleSizeTest.ts
```

### 5. GenerateReport.ts
Generates a comprehensive performance test report.

**Output:**
- Bundle size analysis
- Performance checklist results
- Expected metrics comparison
- Memory leak detection results
- Recommendations
- Production readiness assessment

**Run:**
```bash
npx tsx src/shared/ui/__tests__/performance/GenerateReport.ts
```

## Running All Tests

### Quick Test (Individual Tests)
```bash
# Run re-render tests
npm test -- RerenderTest

# Run performance tests
npm test -- RenderingPerformanceTest

# Run memory leak tests
npm test -- MemoryLeakTest
```

### Full Test Suite
```bash
# Run all performance tests and generate report
./src/shared/ui/__tests__/performance/run-performance-tests.sh
```

## Expected Results

Based on Vercel React Best Practices, the component library should achieve:

### Bundle Size
- Total: < 50KB (excellent), < 100KB (acceptable), > 100KB (needs optimization)
- Individual components: < 20KB each

### Rendering Performance
- Simple components (Button, Badge): < 1ms per component
- Medium components (Input, Card): < 2ms per component
- Complex components (Table, Modal): < 5ms per component

### Memory Management
- Zero memory leaks on mount/unmount
- Proper event listener cleanup
- No lingering references after unmount

### React.memo Effectiveness
- No unnecessary re-renders when props don't change
- Custom comparison functions working correctly
- Memoized sub-components not cascading updates

## Performance Optimizations Applied

### Re-render Optimization (MEDIUM)
- ✅ React.memo on all components
- ✅ Custom comparison functions
- ✅ Memoized sub-components

### Advanced Patterns (LOW)
- ✅ Advanced event handler refs (Modal)
- ✅ useCallback for stable handlers

### JavaScript Performance (LOW-MEDIUM)
- ✅ Array join for className (reduces temporary strings)

### Rendering Performance (MEDIUM)
- ✅ Functional setState pattern
- ✅ Conditional rendering optimization

## Production Readiness Criteria

The component library is considered production-ready when:

1. **Performance Score**: ≥ 80/100
2. **Bundle Size**: < 100KB total
3. **Memory Leaks**: Zero detected
4. **Rendering Times**: All within target thresholds
5. **React.memo**: Effective on all components

## Troubleshooting

### Tests Failing?

1. **Re-render tests failing**: Check if props are being compared correctly in React.memo
2. **Performance tests failing**: May need to optimize component rendering logic
3. **Memory leak tests failing**: Check cleanup in useEffect returns
4. **Bundle size too large**: Consider code splitting or lazy loading

### Performance Score Low?

Review the checklist in `GenerateReport.ts` to see which optimizations are missing.

### Memory Leaks Detected?

Check that:
- Event listeners are removed in useEffect cleanup
-Refs are nulled on unmount
- Child components unmount properly
- No closures retaining references

## Continuous Monitoring

For production apps, consider:

1. **Real User Monitoring (RUM)**: Track actual performance in production
2. **Bundle Analysis**: Use webpack-bundle-analyzer or vite-plugin-inspect
3. **Performance Budgets**: Set thresholds in CI/CD
4. **Automated Testing**: Run performance tests on every PR

## Contributing

When adding new components:

1. Add React.memo if props don't change frequently
2. Add performance tests to this suite
3. Update bundle size analysis
4. Document any performance trade-offs

## References

- [Vercel React Best Practices](https://github.com/vercel/next.js/tree/canary/packages/react-best-practices)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [Web Performance APIs](https://developer.mozilla.org/en-US/docs/Web/API/Performance)

## License

MIT
