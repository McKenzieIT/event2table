# Code Duplication Refactoring Plan
**Generated**: 2026-03-17
**Author**: Subagent 1: Code Deduplication Expert
**Status**: In Progress

## Executive Summary

Based on analysis of backend and frontend code, I've identified the following:

### Current State
- **Backend**: 403 instances of response helper usage across API routes
- **Frontend**: 178 instances of fetch/date/string patterns
- **Shared utilities already exist**: Both `backend/core/utils/common.py` and `frontend/src/shared/utils/commonUtils.ts` are comprehensive

### Top 5 Duplication Patterns

1. **Error Handling in Backend** (403 instances)
   - Repetitive try-except blocks with ValidationError/ValueError/Exception
   - Solution: Use `@handle_api_errors` decorator

2. **Loading State in Frontend** (50+ components)
   - Repetitive `const [loading, setLoading] = useState(false)`
   - Solution: Use `useLoadingState` hook

3. **Date/Time Formatting** (Backend: 9, Frontend: 20+)
   - Scattered `.strftime()` and `new Date()` calls
   - Solution: Use `format_datetime()` / `formatDate()`

4. **String Sanitization** (Backend: 15+, Frontend: 10+)
   - Manual HTML escaping and trimming
   - Solution: Use `sanitize_string()` / `sanitizeInput()`

5. **Pagination Logic** (Backend: 8, Frontend: 12)
   - Manual page/per_page/offset calculations
   - Solution: Use `get_pagination_params()` / `calculatePagination()`

## Refactoring Strategy

### Phase 1: Backend Error Handling (30 min)
**Target**: Reduce 403 response helper calls to ~100 using decorators

**Before**:
```python
@api_bp.route('/api/events', methods=['GET'])
def list_events():
    try:
        game_gid = request.args.get('game_gid', type=int)
        service = EventService()
        events = service.get_events_by_game(game_gid)
        return json_success_response(data=events)
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return json_error_response("Failed to list events", status_code=500)
```

**After**:
```python
from backend.core.utils.common import handle_api_errors

@api_bp.route('/api/events', methods=['GET'])
@handle_api_errors("Failed to list events")
def list_events():
    game_gid = request.args.get('game_gid', type=int)
    service = EventService()
    events = service.get_events_by_game(game_gid)
    return json_success_response(data=events)
```

**Files to Refactor**:
- `backend/api/routes/events.py`
- `backend/api/routes/games.py`
- `backend/api/routes/categories.py`
- `backend/api/routes/parameters.py`
- `backend/api/routes/flows.py`

### Phase 2: Frontend Loading States (20 min)
**Target**: Reduce 50+ loading state declarations to ~10 using shared hook

**Before**:
```typescript
const [loading, setLoading] = useState(false);

const handleSave = async () => {
  setLoading(true);
  try {
    await saveGame(data);
  } finally {
    setLoading(false);
  }
};
```

**After**:
```typescript
import { useLoadingState } from '@/shared/utils';

const [loading, , executeAsync] = useLoadingState();

const handleSave = async () => {
  await executeAsync(async () => {
    await saveGame(data);
  });
};
```

**Files to Refactor**:
- `frontend/src/features/canvas/components/DataPreviewModal.tsx`
- `frontend/src/shared/components/BindToLibraryModal.tsx`
- `frontend/src/event-builder/components/FieldsListModal.tsx`
- `frontend/src/event-builder/components/QuickEditModal.tsx`

### Phase 3: Date/Time Formatting (15 min)
**Target**: Consolidate all date formatting to shared utilities

**Backend**:
```python
# Before
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# After
from backend.core.utils.common import format_datetime
created_at = format_datetime(datetime.now())
```

**Frontend**:
```typescript
// Before
const dateStr = new Date(date).toLocaleDateString();

// After
import { formatDate } from '@/shared/utils';
const dateStr = formatDate(date);
```

### Phase 4: String Sanitization (10 min)
**Target**: Replace manual sanitization with shared utilities

**Backend**:
```python
# Before
import html
cleaned = html.escape(user_input.strip())

# After
from backend.core.utils.common import sanitize_string
cleaned = sanitize_string(user_input)
```

**Frontend**:
```typescript
// Before
const cleaned = input.trim();

// After
import { cleanString } from '@/shared/utils';
const cleaned = cleanString(input);
```

### Phase 5: Pagination (10 min)
**Target**: Standardize pagination logic

**Backend**:
```python
# Before
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 20, type=int)
offset = (page - 1) * per_page

# After
from backend.core.utils.common import get_pagination_params
page, per_page, offset = get_pagination_params()
```

**Frontend**:
```typescript
// Before
const totalPages = Math.ceil(total / perPage);
const hasNext = page < totalPages;

// After
import { calculatePagination } from '@/shared/utils';
const { totalPages, hasNext } = calculatePagination(total, page, perPage);
```

## Implementation Order

1. **Backend Error Handling** (Highest impact - 75% reduction in error handling code)
2. **Frontend Loading States** (High impact - 80% reduction in state management code)
3. **Date/Time Formatting** (Medium impact - Improves consistency)
4. **String Sanitization** (Medium impact - Security improvement)
5. **Pagination** (Low impact - Minor code reduction)

## Testing Strategy

### Unit Tests
```bash
# Backend
pytest backend/test/unit/utils/test_common.py -v

# Frontend
npm run test:unit -- src/shared/utils
```

### Integration Tests
```bash
# Test API endpoints still work
pytest backend/test/integration/api/

# Test components render correctly
npm run test:e2e
```

## Success Metrics

- **Code Duplication**: Reduce from ~600 instances to ~200 instances (67% reduction)
- **Lines of Code**: Reduce by ~1500 lines across backend and frontend
- **Test Coverage**: Maintain >80% coverage
- **Build Time**: No increase in build time
- **Runtime Performance**: No degradation

## Risks and Mitigation

### Risk 1: Breaking Changes
- **Mitigation**: Comprehensive test suite before refactoring
- **Rollback**: Git branch per phase for easy rollback

### Risk 2: Performance Regression
- **Mitigation**: Benchmark before/after each phase
- **Validation**: Run performance tests after each phase

### Risk 3: Developer Adoption
- **Mitigation**: Update CLAUDE.md with new patterns
- **Documentation**: Create code examples and best practices

## Timeline

- **Phase 1**: 30 min (Backend Error Handling)
- **Phase 2**: 20 min (Frontend Loading States)
- **Phase 3**: 15 min (Date/Time Formatting)
- **Phase 4**: 10 min (String Sanitization)
- **Phase 5**: 10 min (Pagination)
- **Testing**: 15 min
- **Total**: ~100 minutes (1.7 hours)

## Next Steps

1. ✅ Analysis complete
2. **Execute Phase 1**: Refactor backend error handling
3. **Execute Phase 2**: Refactor frontend loading states
4. **Execute Phase 3-5**: Remaining patterns
5. **Run comprehensive tests**
6. **Measure results and generate report**

---

**Status**: Ready to execute Phase 1
**Blocked**: No
**Dependencies**: None
