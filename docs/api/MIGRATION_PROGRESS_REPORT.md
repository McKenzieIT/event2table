# 前端迁移进度报告

生成时间: 2026-03-03 19:43:11

## REST API使用情况

发现 12 个REST API端点仍在使用:

### /api/categories
调用次数: 1

- analytics/components/categories/CategoryManagementModal.tsx

### /api/categories/batch
调用次数: 1

- analytics/pages/CategoriesList.tsx

### /api/common-params/batch
调用次数: 1

- analytics/pages/CommonParamsList.tsx

### /api/common-params/sync
调用次数: 1

- analytics/pages/CommonParamsList.tsx

### /api/events/batch
调用次数: 1

- analytics/pages/EventsList.tsx

### /api/events/import
调用次数: 1

- analytics/pages/ImportEvents.tsx

### /api/flows
调用次数: 2

- features/canvas/components/Toolbar.tsx
- analytics/pages/Dashboard.tsx

### /api/flows/execute
调用次数: 1

- features/canvas/hooks/useFlowExecute.ts

### /api/games
调用次数: 11

- features/canvas/hooks/useGameData.ts
- features/games/GameManagementModal.tsx
- features/games/hooks/useGameData.ts
- shared/components/GameForm/GameForm.tsx
- shared/hooks/useGameContext.ts
- shared/api/errorHandler.ts
- event-builder/pages/EventNodeBuilder.tsx
- migration/GAMES_MIGRATION_EXAMPLE.ts
- migration/GAMES_MIGRATION_EXAMPLE.ts
- analytics/components/game-selection/GameSelectionSheet.tsx
- analytics/pages/Dashboard.tsx

### /api/generate
调用次数: 1

- analytics/pages/Generate.tsx

### /api/hql/results
调用次数: 1

- analytics/pages/HqlResults.tsx

### /api/preview-excel
调用次数: 1

- analytics/pages/ImportEvents.tsx

## GraphQL使用情况

发现 64 个GraphQL操作:

- DETECT_PARAMETER_CHANGES: 1次
- GET_ALL_GAME_STATS: 1次
- GET_ALL_PARAMETERS_BY_GAME: 1次
- GET_CATEGORIES: 4次
- GET_CATEGORY: 2次
- GET_COMMON_PARAMETERS: 2次
- GET_DASHBOARD_STATS: 2次
- GET_EVENT: 3次
- GET_EVENTS: 4次
- GET_EVENT_FIELDS: 1次
- GET_FILTERED_PARAMETERS: 1次
- GET_FLOW: 2次
- GET_FLOWS: 2次
- GET_GAME: 2次
- GET_GAMES: 5次
- GET_GAME_STATS: 2次
- GET_JOIN_CONFIG: 1次
- GET_JOIN_CONFIGS: 1次
- GET_NODE: 1次
- GET_NODES: 1次
- GET_PARAMETER: 2次
- GET_PARAMETERS: 3次
- GET_PARAMETERS_MANAGEMENT: 2次
- GET_TEMPLATE: 1次
- GET_TEMPLATES: 1次
- SEARCH_CATEGORIES: 2次
- SEARCH_EVENTS: 2次
- SEARCH_GAMES: 3次
- SEARCH_PARAMETERS: 2次
- mutation:AUTO_SYNC_COMMON_PARAMETERS: 1次
- mutation:BATCH_ADD_FIELDS_TO_CANVAS: 1次
- mutation:CHANGE_PARAMETER_TYPE: 2次
- mutation:CREATE_CATEGORY: 2次
- mutation:CREATE_EVENT: 2次
- mutation:CREATE_FLOW: 1次
- mutation:CREATE_GAME: 5次
- mutation:CREATE_JOIN_CONFIG: 1次
- mutation:CREATE_NODE: 1次
- mutation:CREATE_PARAMETER: 2次
- mutation:CREATE_TEMPLATE: 1次
- mutation:CREATE_VALIDATION_RULE: 1次
- mutation:DELETE_CATEGORY: 2次
- mutation:DELETE_EVENT: 3次
- mutation:DELETE_EVENT_PARAMETER: 1次
- mutation:DELETE_FLOW: 1次
- mutation:DELETE_GAME: 4次
- mutation:DELETE_HQL_TEMPLATE: 2次
- mutation:DELETE_JOIN_CONFIG: 1次
- mutation:DELETE_NODE: 1次
- mutation:DELETE_PARAMETER: 2次
- mutation:DELETE_TEMPLATE: 1次
- mutation:GENERATE_HQL: 2次
- mutation:ROLLBACK_EVENT_PARAMETER: 1次
- mutation:SAVE_HQL_TEMPLATE: 2次
- mutation:SET_PARAM_CONFIG: 1次
- mutation:UPDATE_CATEGORY: 2次
- mutation:UPDATE_EVENT: 2次
- mutation:UPDATE_EVENT_PARAMETER: 1次
- mutation:UPDATE_FLOW: 1次
- mutation:UPDATE_GAME: 5次
- mutation:UPDATE_JOIN_CONFIG: 1次
- mutation:UPDATE_NODE: 1次
- mutation:UPDATE_PARAMETER: 2次
- mutation:UPDATE_TEMPLATE: 1次
## 迁移进度

- 总API调用: 140
- GraphQL: 117 (83.6%)
- REST API: 23 (16.4%)
- **迁移进度: 83.6%**
