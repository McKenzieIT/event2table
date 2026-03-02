# REST API归档迁移日志

## 迁移执行时间
2026-03-01

## 迁移操作
将 `backend/api/_archived/` 目录移动到 `archive/backend/api/_archived_rest_api/`

## 迁移原因
1. **清理代码库**: 归档文件不应保留在活跃的开发目录中
2. **减少维护负担**: 避免开发者误用已废弃的API
3. **明确架构边界**: 归档文件与活跃代码分离

## 迁移内容
- **文件数量**: 19个文件
- **目录大小**: 204KB
- **主要内容**: 10个已迁移到GraphQL的REST API模块

## 已归档模块列表
1. games.py - 游戏管理API
2. events.py - 事件管理API
3. parameters.py - 参数管理API
4. categories.py - 分类管理API
5. dashboard.py - 仪表盘API
6. templates.py - 模板管理API
7. nodes.py - 节点管理API
8. flows.py - 流程管理API
9. event_parameters.py - 事件参数API
10. join_configs.py - Join配置API

## GraphQL替代方案
所有已归档的REST API功能均已完整迁移到GraphQL API:
- **Schema**: `backend/gql_api/schema.py`
- **Queries**: `backend/gql_api/queries/`
- **Mutations**: `backend/gql_api/mutations/`
- **Types**: `backend/gql_api/types/`
- **文档**: http://localhost:5001/api/graphiql

## 注意事项
⚠️ **重要提示**:
1. 归档文件仅供参考,不应被导入或使用
2. 所有新功能应使用GraphQL API
3. 如需修改,请在GraphQL实现中进行
4. 归档文件不参与测试和构建流程

## 后续行动
- [ ] 更新项目文档,说明归档文件位置
- [ ] 通知团队成员归档文件已移动
- [ ] 在代码审查中检查是否有误用归档文件的情况
- [ ] 考虑在未来版本中完全删除归档文件

## 相关文档
- [REST API与GraphQL双轨制分析报告](../../docs/REST_GRAPHQL_ANALYSIS.md)
- [GraphQL迁移指南](../../docs/GRAPHQL_MIGRATION_GUIDE.md)
