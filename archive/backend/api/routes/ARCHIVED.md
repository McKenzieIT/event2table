# Archived REST API Modules

## Overview

This directory contains REST API modules that have been archived after being successfully replaced by GraphQL APIs. These modules are no longer maintained but are preserved for reference purposes.

**Archive Date**: 2026-03-01
**Reason**: Successfully migrated to GraphQL API
**Status**: Safe to delete after 6 months (2026-09-01)

---

## Archived Modules

### 1. Dashboard API

**File**: `dashboard.py`
**Archived**: 2026-03-01

#### Why Archived?

The Dashboard REST API has been completely replaced by GraphQL queries:

| REST Endpoint | GraphQL Query | Status |
|--------------|---------------|---------|
| `GET /api/dashboard/stats` | `dashboardStats` | ✅ Migrated |
| `GET /api/dashboard/game-stats?game_gid={id}` | `gameStats` | ✅ Migrated |
| `GET /api/dashboard/all-game-stats` | `allGameStats` | ✅ Migrated |

#### Migration Example

**Before (REST)**:
```javascript
const response = await fetch('/api/dashboard/stats');
const data = await response.json();
```

**After (GraphQL)**:
```javascript
const { data } = useQuery(GetDashboardStatsDocument);
```

#### GraphQL Implementation

```graphql
query GetDashboardStats {
  dashboardStats {
    totalGames
    totalEvents
    totalParameters
    totalCategories
    eventsLast7Days
    parametersLast7Days
  }
}
```

---

### 2. Templates API

**File**: `templates.py`
**Archived**: 2026-03-01

#### Why Archived?

The Templates REST API has been completely replaced by GraphQL queries:

| REST Endpoint | GraphQL Query | Status |
|--------------|---------------|---------|
| `GET /api/templates` | `templates` | ✅ Migrated |
| `GET /api/templates/{id}` | `template(id: $id)` | ✅ Migrated |
| `POST /api/templates` | `createTemplate` mutation | ✅ Migrated |
| `PUT /api/templates/{id}` | `updateTemplate` mutation | ✅ Migrated |
| `DELETE /api/templates/{id}` | `deleteTemplate` mutation | ✅ Migrated |
| `GET /api/templates/search` | `searchTemplates` | ✅ Migrated |

#### Migration Example

**Before (REST)**:
```javascript
const response = await fetch('/api/templates?game_gid=10000147');
const data = await response.json();
```

**After (GraphQL)**:
```javascript
const { data } = useQuery(GetTemplatesDocument, {
  variables: { gameGid: 10000147 }
});
```

#### GraphQL Implementation

```graphql
query GetTemplates($gameGid: Int!) {
  templates(gameGid: $gameGid) {
    id
    name
    description
    gameGid
    createdAt
  }
}
```

---

### 3. Nodes API

**File**: `nodes.py`
**Archived**: 2026-03-01

#### Why Archived?

The Nodes REST API has been completely replaced by GraphQL queries:

| REST Endpoint | GraphQL Query | Status |
|--------------|---------------|---------|
| `GET /api/event-nodes` | `nodes` | ✅ Migrated |
| `GET /api/event-nodes/{id}` | `node(id: $id)` | ✅ Migrated |
| `POST /api/event-nodes` | `createNode` mutation | ✅ Migrated |
| `PUT /api/event-nodes/{id}` | `updateNode` mutation | ✅ Migrated |
| `DELETE /api/event-nodes/{id}` | `deleteNode` mutation | ✅ Migrated |

**Note**: Canvas functionality now uses the dedicated `/event_node_builder/api` endpoints for specialized operations.

#### Migration Example

**Before (REST)**:
```javascript
const response = await fetch('/api/event-nodes?game_gid=10000147');
const data = await response.json();
```

**After (GraphQL)**:
```javascript
const { data } = useQuery(GetNodesDocument, {
  variables: { gameGid: 10000147 }
});
```

#### GraphQL Implementation

```graphql
query GetNodes($gameGid: Int!) {
  nodes(gameGid: $gameGid) {
    id
    name
    description
    event {
      id
      name
    }
    fields {
      name
      type
      jsonPath
    }
  }
}
```

---

## Benefits of Migration

### 1. **Type Safety**
- GraphQL provides strong typing with TypeScript
- Auto-generated types prevent bugs
- Better IDE autocomplete

### 2. **Reduced Over-fetching**
- Clients request exactly what they need
- Smaller payload sizes
- Faster page loads

### 3. **Single Endpoint**
- All data through `/graphql`
- Simpler backend architecture
- Easier to maintain

### 4. **Better Developer Experience**
- GraphiQL explorer for testing
- Self-documenting API
- Real-time schema validation

---

## Rollback Plan

If needed, these modules can be restored:

```bash
# Copy back to active routes
cp archive/backend/api/routes/dashboard.py backend/api/routes/
cp archive/backend/api/routes/templates.py backend/api/routes/
cp archive/backend/api/routes/nodes.py backend/api/routes/

# Update backend/api/__init__.py
# Add imports back to the import list
```

However, **this is not recommended** as:
1. Frontend has fully migrated to GraphQL
2. REST APIs are no longer maintained
3. GraphQL provides better performance and DX

---

## Related Documentation

- [REST API Removal Plan](../../../docs/api/REST_API_REMOVAL_PLAN.md)
- [GraphQL API Documentation](../../../docs/api/README.md)
- [Migration Guide](../../../docs/development/GRAPHQL_MIGRATION_GUIDE.md)

---

## Deletion Timeline

| Milestone | Date |
|-----------|------|
| Archived | 2026-03-01 |
| Verification Period | 2026-03-01 to 2026-06-01 |
| Safe to Delete | 2026-09-01 |

**Decision**: Delete these files after 6 months if no issues arise.

---

## Contact

For questions about these archived modules, contact the development team.
