# Performance Audit Report

**Generated**: 2026-03-06 12:56:02
**Mode**: QUICK
**Project**: /Users/mckenzie/Documents/event2table
**Issues Found**: 597

## 📊 Executive Summary

- **High Priority**: 531 issue(s)
- **Medium Priority**: 31 issue(s)
- **Low Priority**: 35 issue(s)

## 🔍 Performance Issues


### Frontend

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventForm.tsx`
- **Message**: Array methods found (1 .map, 0 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usecallback
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/Dashboard.tsx`
- **Message**: useEffect found without useCallback for dependencies
- **Suggestion**: Use useCallback for functions passed to useEffect dependencies to stabilize references

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/ImportEvents.tsx`
- **Message**: Array methods found (1 .map, 0 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/event-builder/components/HQLPreview.tsx`
- **Message**: Exported component "HQLPreview" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(HQLPreview)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/event-builder/components/ErrorBoundary.tsx`
- **Message**: Exported component "EventNodeBuilderErrorBoundary" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(EventNodeBuilderErrorBoundary)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/event-builder/components/WhereBuilder/WhereConditionItem.tsx`
- **Message**: Exported component "WhereConditionItem" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(WhereConditionItem)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/event-builder/components/HQLPreviewV2/CacheIndicator.tsx`
- **Message**: Exported component "CacheIndicator" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(CacheIndicator)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/event-builder/components/HQLPreviewWrapper/HQLPreviewWrapper.tsx`
- **Message**: Exported component "HQLPreviewWrapper" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(HQLPreviewWrapper)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/CanvasErrorBoundary.tsx`
- **Message**: Exported component "CanvasErrorBoundary" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(CanvasErrorBoundary)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/components/ErrorBoundary.tsx`
- **Message**: Exported component "ErrorBoundary" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(ErrorBoundary)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/components/VirtualList/VirtualTable.tsx`
- **Message**: Exported component "VirtualTable" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(VirtualTable)

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/PageLoader/PageLoader.tsx`
- **Message**: Exported component "PageLoader" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(PageLoader)

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Radio/Radio.tsx`
- **Message**: Array methods found (1 .map, 2 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Card/Card.tsx`
- **Message**: Array methods found (0 .map, 5 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Input/Input.tsx`
- **Message**: Array methods found (0 .map, 3 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Toast/Toast.tsx`
- **Message**: Array methods found (1 .map, 3 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Checkbox/Checkbox.tsx`
- **Message**: Array methods found (0 .map, 2 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Spinner/Spinner.tsx`
- **Message**: Array methods found (0 .map, 1 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/TextArea/TextArea.tsx`
- **Message**: Array methods found (0 .map, 3 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Button/Button.tsx`
- **Message**: Array methods found (0 .map, 1 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/ErrorState/ErrorState.tsx`
- **Message**: Exported component "ErrorState" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(ErrorState)

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Table/Table.tsx`
- **Message**: Array methods found (0 .map, 7 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Switch/Switch.tsx`
- **Message**: Array methods found (0 .map, 2 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Breadcrumb/Breadcrumb.test.tsx`
- **Message**: Exported component "component" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(component)

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Modal/Modal.archive.tsx`
- **Message**: Array methods found (0 .map, 5 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/BaseModal/BaseModal.tsx`
- **Message**: Array methods found (0 .map, 2 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usecallback
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/BaseModal/BaseModal.tsx`
- **Message**: useEffect found without useCallback for dependencies
- **Suggestion**: Use useCallback for functions passed to useEffect dependencies to stabilize references

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/Badge/Badge.tsx`
- **Message**: Array methods found (0 .map, 1 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/RerenderTest.tsx`
- **Message**: Array methods found (1 .map, 0 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usecallback
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/RerenderTest.tsx`
- **Message**: useEffect found without useCallback for dependencies
- **Suggestion**: Use useCallback for functions passed to useEffect dependencies to stabilize references

#### Missing React Memo
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/MemoryLeakTest.tsx`
- **Message**: Large component file (11955 chars) without React.memo
- **Suggestion**: Consider wrapping with React.memo to prevent unnecessary re-renders

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/MemoryLeakTest.tsx`
- **Message**: Array methods found (2 .map, 0 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usecallback
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/MemoryLeakTest.tsx`
- **Message**: useEffect found without useCallback for dependencies
- **Suggestion**: Use useCallback for functions passed to useEffect dependencies to stabilize references

#### Missing React Memo
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/RenderingPerformanceTest.tsx`
- **Message**: Large component file (12603 chars) without React.memo
- **Suggestion**: Consider wrapping with React.memo to prevent unnecessary re-renders

#### Potential Missing Usememo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/RenderingPerformanceTest.tsx`
- **Message**: Array methods found (2 .map, 0 .filter, 0 .reduce) without useMemo
- **Suggestion**: If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])

#### Potential Missing Usecallback
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/ui/__tests__/performance/RenderingPerformanceTest.tsx`
- **Message**: useEffect found without useCallback for dependencies
- **Suggestion**: Use useCallback for functions passed to useEffect dependencies to stabilize references

#### Exported Component Without Memo
- **Severity**: LOW
- **File**: `/Users/mckenzie/Documents/event2table/frontend/src/features/events/AddEventModalGraphQL.tsx`
- **Message**: Exported component "AddEventModalGraphQL" without React.memo
- **Suggestion**: Consider wrapping: export default React.memo(AddEventModalGraphQL)


### Backend

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/sql_builder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/data_access.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/common.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/performance.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/events.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/schemas.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/gql_api/schema_parameter_management.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/event_node_builder/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/cache/cache_warmup.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/bulk_operations/bulk_routes.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/field_builder/field_builder_service.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/canvas/canvas.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/hql_history_service.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/parameters/param_library_manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/parameters/event_param_manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/parameters/parameter_service.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/core/incremental_generator.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/core/dml_generator.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/builders/union_builder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/builders/join_builder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/validators/syntax_validator.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/services/hql/validators/test_performance_analyzer_extended.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/gql_api/mutations/hql_mutations.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/gql_api/dataloaders/parameter_management_loader.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/gql_api/dataloaders/game_loader.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/gql_api/dataloaders/optimized_loaders.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/gql_api/resolvers/parameter_resolvers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pycodestyle.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/six.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/typing_extensions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/typing_extensions.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/flask/app.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/aiohttp/multipart.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/aiohttp/web_middlewares.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/aiohttp/client.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/aiohttp/client_reqrep.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/cmdline.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/connection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/connection.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/cluster.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/cluster.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/jinja2/compiler.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/jinja2/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/jinja2/environment.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/jinja2/filters.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/locust/argument_parser.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/pywsgi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/subprocess.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/select.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/_config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/et_xmlfile/incremental_tree.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/werkzeug/serving.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/werkzeug/test.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/werkzeug/urls.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/sentry_sdk/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/click/_termui_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pydocstyle/config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pydocstyle/checker.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gunicorn/config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gunicorn/arbiter.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/requests/sessions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/requests/models.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/requests/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/build.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/options.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/types.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/typeanal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/typeops.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/stats.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/messages.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/applytype.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/constraints.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/metastore.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/checkexpr.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/checker.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/semanal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/subtypes.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/rich/live.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pluggy/_manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/yaml/scanner.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/urllib3/connection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/installer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_scripts.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/dist.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/_distutils_hack/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/bitarray/test_bitarray.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/psutil/_pswindows.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/psutil/_common.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/psutil/_pssunos.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/coverage/numbits.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/coverage/sqldata.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/coverage/debug.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/coverage/report.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/yarl/_parse.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zmq/asyncio.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/conftest.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/dateutil/rrule.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/stevedore/_cache.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/_pytest/terminal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/_pytest/main.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/_pytest/cacheprovider.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/_pytest/mark/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zope/interface/adapter.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zope/interface/interface.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zope/interface/declarations.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zope/interface/tests/test_adapter.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zope/interface/tests/test_interface.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/generic.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/common.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/frame.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/apply.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/pytables.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/html.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/sql.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/sql.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/stata.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/test_algos.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/_config/config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/plotting/_matplotlib/tools.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/plotting/_matplotlib/core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/resample/test_resample_api.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/io/test_sql.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/interchange/test_spec_conformance.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/groupby/test_timegrouper.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/groupby/test_indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/computation/test_eval.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/indexing/test_loc.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/plotting/frame/test_frame_subplots.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/groupby/transform/test_transform.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/frame/methods/test_between_time.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/io/pytables/test_select.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/io/pytables/test_store.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/tests/io/formats/style/test_style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/parsers/base_parser.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/formats/style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/formats/html.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/formats/excel.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/formats/style_render.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/excel/_base.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/io/json/_json.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/reshape/merge.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/reshape/reshape.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/reshape/pivot.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/methods/describe.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/groupby/generic.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/groupby/indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/groupby/groupby.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/internals/managers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/computation/eval.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/computation/expr.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/indexes/multi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pandas/core/indexes/base.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zmq/tests/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/zmq/ssh/tunnel.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/rx/internal/enumerable.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/command/editable_wheel.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_distutils/filelist.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_distutils/dist.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_vendor/importlib_metadata/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_vendor/importlib_metadata/_itertools.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_vendor/wheel/macosx_libfile.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_vendor/more_itertools/more.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/setuptools/_vendor/more_itertools/recipes.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/urllib3/util/url.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/utils/extend_schema.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/type/definition.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/execution/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/execution/executor.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/validation/validation.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/validation/tests/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/validation/rules/overlapping_fields_can_be_merged.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/execution/executors/thread.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/type/tests/test_enum_type.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/language/tests/test_parser.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/graphql/language/tests/test_ast.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/test/teststubgen.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/mypy/test/helpers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/build_env.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/pygments/style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/requests/sessions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/requests/models.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/requests/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/rich/live.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/urllib3/poolmanager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/urllib3/util/url.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_vendor/urllib3/packages/six.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/utils/filesystem.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/cli/req_command.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/operations/prepare.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/vcs/git.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/index/package_finder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/index/package_finder.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/commands/show.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/commands/install.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pip/_internal/resolution/legacy/resolver.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/charset_normalizer/cli/__main__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/linalg/_linalg.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/ma/extras.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/ma/core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/fromnumeric.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/_add_newdocs.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/tests/test_public_api.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/f2py/crackfortran.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/f2py/capi_maps.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/recfunctions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/_arraysetops_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/_npyio_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/_function_base_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/_datasource.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/matrixlib/defmatrix.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/tests/test_io.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/lib/tests/test_format.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/f2py/tests/test_crackfortran.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_simd.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_umath.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_numeric.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_ufunc.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_multiarray.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_nditer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/_core/tests/test_cpu_features.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/ma/tests/test_core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/numpy/linalg/tests/test_linalg.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/bandit/core/manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/bandit/plugins/injection_shell.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/bandit/plugins/django_sql_injection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/bandit/cli/main.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gunicorn/http/wsgi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/sentry_sdk/integrations/strawberry.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/sentry_sdk/integrations/pymongo.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/sentry_sdk/integrations/ariadne.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/sentry_sdk/integrations/wsgi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/werkzeug/wrappers/response.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/werkzeug/sansio/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/werkzeug/debug/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/tests/test__threadpool.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/tests/test__monkey.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/tests/test__selectors.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/libev/corecffi.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/gevent/resolver/dnspython.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/locust/user/task.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/core.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/cluster.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/asyncio/connection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/asyncio/connection.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/asyncio/cluster.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/_parsers/helpers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/_parsers/helpers.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/_parsers/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/timeseries/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/graph/query_result.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/search/aggregation.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/search/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/redis/commands/json/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/flake8/plugins/finder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/c_like.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/crystal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/_php_builtins.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/scripting.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/ruby.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/make.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/sql.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/lexers/sql.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv/lib/python3.13/site-packages/pygments/formatters/img.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/api/routes/join_configs_old_backup.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/api/routes/cache.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/api/routes/legacy_api.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/api/routes/hql_preview_v2.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/api/routes/hql_generation.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/event_node_repository.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/hql_history_repository.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/flow_repository.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/field_recommendation_repository.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/category_repository.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/join_config_repository.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/parameters.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pycodestyle.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/six.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/typing_extensions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/typing_extensions.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/flask/app.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/aiohttp/multipart.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/aiohttp/web_middlewares.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/aiohttp/client.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/aiohttp/client_reqrep.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/cmdline.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/connection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/connection.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/cluster.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/cluster.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/jinja2/compiler.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/jinja2/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/jinja2/environment.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/jinja2/filters.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/locust/argument_parser.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/pywsgi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/subprocess.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/select.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/_config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/et_xmlfile/incremental_tree.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/importlib_metadata/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/importlib_metadata/_itertools.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/werkzeug/serving.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/werkzeug/test.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/werkzeug/urls.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/sentry_sdk/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/click/_termui_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gunicorn/config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gunicorn/arbiter.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/requests/sessions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/requests/models.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/requests/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/build.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/options.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/types.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/typeanal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/typeops.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/stats.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/messages.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/applytype.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/constraints.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/metastore.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/checkexpr.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/checker.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/semanal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/subtypes.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/rich/live.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pluggy/_manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/yaml/scanner.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/urllib3/connection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/installer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_scripts.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/dist.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/_distutils_hack/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/bitarray/test_bitarray.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/psutil/_pswindows.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/psutil/_common.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/psutil/_pssunos.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/coverage/numbits.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/coverage/cmdline.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/coverage/sqldata.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/coverage/debug.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/coverage/report.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/yarl/_parse.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zmq/asyncio.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/conftest.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/dateutil/rrule.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/stevedore/_cache.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/_pytest/terminal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/_pytest/main.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/_pytest/cacheprovider.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/_pytest/mark/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zope/interface/adapter.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zope/interface/interface.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zope/interface/declarations.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zope/interface/tests/test_adapter.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zope/interface/tests/test_interface.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/missing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/generic.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/series.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/common.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/frame.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/apply.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/pytables.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/html.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/sql.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/sql.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/stata.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/test_algos.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/_config/config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/plotting/_matplotlib/tools.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/plotting/_matplotlib/core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/resample/test_resample_api.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/io/test_sql.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/interchange/test_spec_conformance.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/groupby/test_timegrouper.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/groupby/test_indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/computation/test_eval.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/indexing/test_loc.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/plotting/frame/test_frame_subplots.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/groupby/transform/test_transform.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/frame/methods/test_between_time.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/io/pytables/test_select.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/io/pytables/test_store.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/tests/io/formats/style/test_style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/parsers/base_parser.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/formats/style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/formats/html.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/formats/excel.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/io/formats/style_render.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/reshape/merge.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/reshape/reshape.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/reshape/pivot.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/methods/describe.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/groupby/generic.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/groupby/indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/groupby/groupby.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/internals/array_manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/internals/managers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/computation/eval.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/computation/expr.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/indexes/multi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pandas/core/indexes/base.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zmq/tests/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/zmq/ssh/tunnel.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/rx/internal/enumerable.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/command/editable_wheel.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_distutils/filelist.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_distutils/dist.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_vendor/importlib_metadata/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_vendor/importlib_metadata/_itertools.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_vendor/wheel/macosx_libfile.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_vendor/more_itertools/more.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/setuptools/_vendor/more_itertools/recipes.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/urllib3/util/url.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/utils/extend_schema.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/type/definition.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/execution/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/execution/executor.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/validation/validation.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/validation/tests/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/validation/rules/overlapping_fields_can_be_merged.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/execution/executors/thread.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/type/tests/test_enum_type.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/language/tests/test_parser.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/graphql/language/tests/test_ast.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/test/teststubgen.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/mypy/test/helpers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/build_env.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/pygments/style.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/requests/sessions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/requests/models.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/requests/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/rich/live.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/urllib3/poolmanager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/resolvelib/resolvers/resolution.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/urllib3/util/url.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_vendor/urllib3/packages/six.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/utils/filesystem.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/cli/req_command.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/operations/prepare.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/vcs/git.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/index/package_finder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/index/package_finder.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/commands/show.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/commands/install.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pip/_internal/resolution/legacy/resolver.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/charset_normalizer/cli/__main__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/distutils/npy_pkg_config.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/distutils/system_info.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/distutils/exec_command.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/linalg/_linalg.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/ma/extras.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/ma/core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/fromnumeric.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/_add_newdocs.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/tests/test_public_api.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/f2py/crackfortran.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/f2py/capi_maps.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/recfunctions.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/_arraysetops_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/_npyio_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/_function_base_impl.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/_datasource.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/matrixlib/defmatrix.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/tests/test_io.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/lib/tests/test_format.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/f2py/tests/test_crackfortran.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_simd.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_indexing.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_umath.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_numeric.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_ufunc.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_multiarray.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_nditer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/_core/tests/test_cpu_features.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/ma/tests/test_core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/numpy/linalg/tests/test_linalg.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/bandit/core/manager.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/bandit/plugins/injection_shell.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/bandit/plugins/django_sql_injection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/bandit/cli/main.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gunicorn/http/wsgi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/sentry_sdk/integrations/strawberry.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/sentry_sdk/integrations/pymongo.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/sentry_sdk/integrations/ariadne.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/sentry_sdk/integrations/wsgi.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/werkzeug/wrappers/response.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/werkzeug/sansio/utils.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/werkzeug/debug/__init__.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/tests/test__threadpool.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/tests/test__monkey.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/tests/test__selectors.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/libev/corecffi.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/gevent/resolver/dnspython.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/locust/user/task.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/core.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/core.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/cluster.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/asyncio/connection.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/asyncio/connection.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/asyncio/cluster.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/_parsers/helpers.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/_parsers/helpers.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/_parsers/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/timeseries/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/graph/query_result.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/search/aggregation.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/search/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/redis/commands/json/commands.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/flake8/plugins/finder.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/c_like.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/crystal.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/_php_builtins.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/scripting.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/ruby.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/make.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/sql.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/lexers/sql.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/venv.py39.backup/lib/python3.9/site-packages/pygments/formatters/img.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/tests/integration/test_parameters_ers_migration.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/tests/performance/test_cache_performance_simple.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/integration/test_hql_history_module_integration.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/integration/database/test_game_gid_migration.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/integration/security/test_hql_generator_security.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/integration/security/test_sql_injection_prevention.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/integration/test_category_seed.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/integration/test_migrations.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/integration/test_init_db_with_categories.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/api/test_hql_history_enhancements.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/api/test_api_comprehensive.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/skills/test_parallel_audit.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/services/field_builder/test_field_builder_service.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/services/hql/test_dml_generator.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/services/hql/test_hql_preview_v2_api.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/services/parameters/test_batch_queries.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/services/parameters/test_parameters_performance.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/test/unit/services/parameters/test_common_params.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/database/database.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/cache_hierarchical.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/intelligent_warmer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/cache_system.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/cache_warmer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Missing Cache Decorator
- **Severity**: MEDIUM
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/protection.py`
- **Message**: Query function without @cached decorator
- **Suggestion**: Add @cached decorator to improve performance

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/utils/formatters.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/utils/converters.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/tests/test_integration_complete.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/tests/test_intelligent_warmer.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries

#### Potential N Plus 1 Query
- **Severity**: HIGH
- **File**: `/Users/mckenzie/Documents/event2table/backend/core/cache/tests/test_bloom_filter_enhanced.py`
- **Message**: Possible N+1 query detected: database query inside loop
- **Suggestion**: Use eager loading (JOIN) or prefetch to avoid N+1 queries


## 💡 Recommendations

Based on the detected issues, here are the top priorities:

1. **Fix 531 potential_n_plus_1_query issues**

1. **Fix 29 missing_cache_decorator issues**

1. **Fix 18 potential_missing_usememo issues**

1. **Fix 12 exported_component_without_memo issues**

1. **Fix 5 potential_missing_usecallback issues**
