# Code Audit Report

**Date**: 2026-03-14 09:35:30
**Duration**: 9.26 seconds
**Total Issues**: 53

## Executive Summary

- **Critical**: 2
- **High**: 39
- **Medium**: 0
- **Low**: 12
- **Info**: 0

## Issues by Category

### quality

#### 5 - N+1 query problem: Database query 'fetchone' inside loop

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:523`

**Suggestion**: Refactor to use JOIN or batch query with IN (...) to avoid N+1 performance issue

**Code**:
```python
for item in items:
    fetchone(...)  # ← N+1 query
```

---

#### 5 - N+1 query problem: Database query 'fetchone' inside loop

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:691`

**Suggestion**: Refactor to use JOIN or batch query with IN (...) to avoid N+1 performance issue

**Code**:
```python
for item in items:
    fetchone(...)  # ← N+1 query
```

---

#### 4 - Query method missing @cached decorator: GameService._get_event_count

**File**: `/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py:304`

**Suggestion**: Add @cached(ttl=300-1800) decorator to cache query results and reduce database load

**Code**:
```python
def _get_event_count(...):
```

---

#### 4 - Query method missing @cached decorator: GameService._get_flow_count

**File**: `/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py:314`

**Suggestion**: Add @cached(ttl=300-1800) decorator to cache query results and reduce database load

**Code**:
```python
def _get_flow_count(...):
```

---

#### 4 - Potential N+1 pattern: fetch_one_as_dict() called 3 times in function

**File**: `/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py:419`

**Suggestion**: Consider refactoring to use a single JOIN query or batch operation with IN (...)

**Code**:
```python
# fetch_one_as_dict() called 3 times
```

---

#### 4 - Function batch_delete_games() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py:284`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return 0
```

---

#### 4 - Function batch_update_games() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py:578`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return 0
```

---

#### 4 - Function get_event_by_id() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/services/events/event_service.py:152`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return None
```

---

#### 4 - Function batch_delete() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:179`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return 0
```

---

#### 4 - Function update() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:210`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return None
```

---

#### 4 - Function batch_update_by_gid() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:270`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return 0
```

---

#### 4 - Function get_gids_by_list() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:399`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return [] or {} or ()
```

---

#### 4 - Function get_by_ids() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:422`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return [] or {} or ()
```

---

#### 4 - Function delete_batch() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:444`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return 0
```

---

#### 4 - Function create_batch() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:484`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return [] or {} or ()
```

---

#### 4 - Function get_with_parameters() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:222`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return None
```

---

#### 4 - Function update() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:527`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return None
```

---

#### 4 - Function get_by_ids() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:617`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return [] or {} or ()
```

---

#### 4 - Function create_batch() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:649`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return [] or {} or ()
```

---

#### 4 - Function delete_batch() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:719`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return 0
```

---

#### 4 - Function batch_find_by_names() returns empty/default value instead of implementing logic

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:846`

**Suggestion**: Implement the actual logic. Return meaningful values or raise appropriate exceptions.

**Code**:
```python
return [] or {} or ()
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:40`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [searchTerm, setSearchTerm] = useState('');
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:41`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [selectedCategory, setSelectedCategory] = useState('all');
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:42`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [selectedEvents, setSelectedEvents] = useState([]);
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:43`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [currentPage, setCurrentPage] = useState(1);
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:44`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:45`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [pageSize, setPageSize] = useState(10);
```

---

#### 4 - React Hook 'useQuery' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:51`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const { data, loading: isLoading, error: fetchError, refetch } = useQuery(GET_EVENTS, {
```

---

#### 4 - React Hook 'useState' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx:48`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const [searchTerm, setSearchTerm] = useState('');
```

---

#### 4 - React Hook 'useCallback' called inside nested structure (if/for/while)

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx:51`

**Suggestion**: Move all Hook calls to the top level of the component

**Code**:
```python
const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:90`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
return ['all', ...cats.map(c => c.name).filter(Boolean)];
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:97`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
return events.filter(event => {
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:129`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
return prev.filter(id => id !== eventId);
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:141`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
return filteredEvents.map(e => e.id);
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:252`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
{events.filter(e => e.categoryName).length}
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:260`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
{events.filter(e => !e.categoryName).length}
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:283`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
options={categories.map(cat => ({
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'EventsListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx:328`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
{filteredEvents.map(event => (
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'GamesListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx:71`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
return games.filter((game: GameType) =>
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'GamesListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx:80`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
const totalEvents = games.reduce((sum, game) => sum + (game?.eventCount || 0), 0);
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'GamesListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx:81`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
const totalParams = games.reduce((sum, game) => sum + (game?.parameterCount || 0), 0);
```

---

#### 2 - Expensive operation may benefit from useMemo in component 'GamesListGraphQL'

**File**: `/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx:241`

**Suggestion**: Wrap expensive operations with useMemo to cache results and prevent re-computation on every render

**Code**:
```python
filteredGames.map((game: GameType) => (
```

---

### architecture

#### 4 - Repository method GameRepository.find_by_ods_db() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:288`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def find_by_ods_db(self, ods_db...)
```

---

#### 4 - Repository method GameRepository.search_by_name() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:305`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def search_by_name(self, name_pattern...)
```

---

#### 4 - Repository method GameRepository.get_game_categories_summary() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:322`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_game_categories_summary(self, game_gid...)
```

---

#### 4 - Repository method GameRepository.get_game_for_update() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:367`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_game_for_update(self, game_id...)
```

---

#### 4 - Repository method GameRepository.get_by_ids() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py:407`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_by_ids(self, game_ids...)
```

---

#### 4 - Repository method EventRepository.get_with_parameters() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:190`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_with_parameters(self, event_id...)
```

---

#### 4 - Repository method EventRepository.get_event_statistics() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:415`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_event_statistics(self, event_id...)
```

---

#### 4 - Repository method EventRepository.get_by_ids() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:602`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_by_ids(self, event_ids...)
```

---

#### 4 - Repository method EventRepository.get_paginated() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:868`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_paginated(self, game_gid, page...)
```

---

#### 4 - Repository method EventRepository.find_detail_with_game() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:943`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def find_detail_with_game(self, event_id, game_gid...)
```

---

#### 4 - Repository method EventRepository.get_event_parameters() returns Dict instead of Entity

**File**: `/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py:968`

**Suggestion**: Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.

**Code**:
```python
def get_event_parameters(self, event_id...)
```

---

