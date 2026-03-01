# REST API归档说明

## 归档日期
2026-02-21

## 归档原因
已完全迁移到GraphQL API

## GraphQL API
- Schema: backend/gql_api/schema.py
- Queries: backend/gql_api/queries/
- Mutations: backend/gql_api/mutations/
- Types: backend/gql_api/types/
- 文档: http://localhost:5001/api/graphiql

## 已归档模块

### 核心业务模块
| 模块 | 原文件 | GraphQL实现 |
|------|--------|-------------|
| Games | games.py | game, games, searchGames / createGame, updateGame, deleteGame |
| Events | events.py | event, events, searchEvents / createEvent, updateEvent, deleteEvent |
| Parameters | parameters.py | parameter, parameters, searchParameters / createParameter, updateParameter, deleteParameter |
| Categories | categories.py | category, categories, searchCategories / createCategory, updateCategory, deleteCategory |
| Dashboard | dashboard.py | dashboardStats, gameStats, allGameStats |
| Templates | templates.py | template, templates, searchTemplates / createTemplate, updateTemplate, deleteTemplate |
| Nodes | nodes.py | node, nodes / createNode, updateNode, deleteNode |
| Flows | flows.py | flow, flows / createFlow, updateFlow, deleteFlow |
| EventParameters | event_parameters.py | eventParameterExtended, paramHistory, paramConfig, validationRules / updateEventParameter, deleteEventParameter, setParamConfig, rollbackEventParameter, createValidationRule |
| JoinConfigs | join_configs.py | joinConfig, joinConfigs / createJoinConfig, updateJoinConfig, deleteJoinConfig |

### 不需要迁移的模块
| 模块 | 原因 |
|------|------|
| hql_generation.py | 命令型操作，REST更合适 |
| hql_preview_v2.py | 命令型操作，REST更合适 |
| field_builder.py | 单表简单CRUD，迁移收益低 |
| monitoring.py | 运维监控API，无数据库 |
| legacy_api.py | 已废弃 |
| v1_adapter.py | 兼容性适配层 |

## GraphQL Schema总览

### Query (30个)
- game, games, searchGames
- event, events, searchEvents
- category, categories, searchCategories
- parameter, parameters, searchParameters
- dashboardStats, gameStats, allGameStats
- template, templates, searchTemplates
- node, nodes
- flow, flows
- eventParameterExtended, paramHistory, paramConfig, validationRules
- joinConfig, joinConfigs

### Mutation (29个)
- createGame, updateGame, deleteGame
- createEvent, updateEvent, deleteEvent
- createParameter, updateParameter, deleteParameter
- createCategory, updateCategory, deleteCategory
- createTemplate, updateTemplate, deleteTemplate
- createNode, updateNode, deleteNode
- createFlow, updateFlow, deleteFlow
- updateEventParameter, deleteEventParameter, setParamConfig, rollbackEventParameter, createValidationRule
- createJoinConfig, updateJoinConfig, deleteJoinConfig

## 测试覆盖
- 总测试数: 27
- 通过: 27
- 失败: 0

## 注意事项
1. 归档文件仅供参考，不应被导入或使用
2. 所有新功能应使用GraphQL API
3. 如需修改，请在GraphQL实现中进行
