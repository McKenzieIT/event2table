# Event2Table 命名规范

## 1. 文件命名规范

### 1.1 Python 文件
- **模块文件**: 小写字母，单词间用下划线分隔
  - 正确: `event_repository.py`, `parameter_service.py`
  - 错误: `EventRepository.py`, `parameterService.py`

- **测试文件**: `test_{模块名}.py`
  - 正确: `test_event_repository.py`, `test_parameter_service.py`
  - 错误: `event_repository_test.py`

- **类型定义文件**: `types.py` 或 `{模块}_types.py`
  - 正确: `event_types.py`, `parameter_types.py`

### 1.2 前端文件
- **组件文件**: PascalCase
  - 正确: `EventList.vue`, `ParameterForm.vue`
  - 错误: `eventList.vue`, `parameter_form.vue`

- **工具文件**: camelCase
  - 正确: `eventUtils.ts`, `parameterHelper.ts`

## 2. 目录命名规范

### 2.1 后端目录
- **DDD分层目录**: 小写字母
  - `domain/` - 领域层
  - `application/` - 应用层
  - `infrastructure/` - 基础设施层
  - `api/` - API层

- **模块目录**: 小写字母，下划线分隔
  - `event_repository/`
  - `parameter_service/`

### 2.2 前端目录
- **功能目录**: kebab-case
  - `event-builder/`
  - `parameter-manager/`

- **组件目录**: PascalCase
  - `components/EventList/`

## 3. 代码命名规范

### 3.1 Python 类命名
- **类名**: PascalCase
  ```python
  class EventRepository:
  class ParameterService:
  ```

- **接口**: I前缀 + PascalCase
  ```python
  class IEventRepository(ABC):
  class IParameterService(ABC):
  ```

- **异常类**: 描述性名称 + Error/Exception
  ```python
  class EventNotFoundError(Exception):
  class InvalidParameterError(Exception):
  ```

### 3.2 Python 函数/方法命名
- **函数名**: snake_case
  ```python
  def get_event_by_id(event_id: int):
  def create_parameter(name: str):
  ```

- **私有方法**: 单下划线前缀
  ```python
  def _validate_event_data(self, data):
  def _convert_to_dict(self, entity):
  ```

- **保护方法**: 单下划线前缀
  ```python
  def _save_to_database(self, entity):
  ```

### 3.3 Python 变量命名
- **普通变量**: snake_case
  ```python
  event_name = "login"
  parameter_count = 10
  ```

- **常量**: 全大写，下划线分隔
  ```python
  MAX_PAGE_SIZE = 100
  DEFAULT_TIMEOUT = 30
  ```

- **类变量**: snake_case
  ```python
  class Event:
      default_category = "general"
  ```

### 3.4 TypeScript/JavaScript 命名
- **变量**: camelCase
  ```typescript
  const eventName = "login";
  let parameterCount = 10;
  ```

- **函数**: camelCase
  ```typescript
  function getEventById(eventId: number) {}
  const createParameter = (name: string) => {};
  ```

- **接口**: I前缀 + PascalCase
  ```typescript
  interface IEvent {
    id: number;
    name: string;
  }
  ```

- **类型别名**: PascalCase
  ```typescript
  type EventStatus = 'active' | 'inactive';
  ```

## 4. 数据库命名规范

### 4.1 表名
- **格式**: snake_case，复数形式
  - 正确: `log_events`, `event_params`, `games`
  - 错误: `LogEvents`, `eventParams`, `game`

### 4.2 列名
- **格式**: snake_case
  - 正确: `event_name`, `game_gid`, `created_at`
  - 错误: `eventName`, `gameGid`, `createdAt`

### 4.3 索引名
- **格式**: `idx_{表名}_{列名}`
  - 正确: `idx_log_events_game_gid`, `idx_event_params_event_id`

### 4.4 外键名
- **格式**: `fk_{表名}_{引用表名}`
  - 正确: `fk_event_params_log_events`

## 5. API 命名规范

### 5.1 RESTful API 路径
- **资源名**: 复数形式，kebab-case
  - 正确: `/api/events`, `/api/event-parameters`
  - 错误: `/api/Event`, `/api/eventParameters`

- **路径参数**: snake_case 或 camelCase（保持一致性）
  - 正确: `/api/events/{event_id}`, `/api/events/{eventId}`

### 5.2 查询参数
- **格式**: snake_case
  - 正确: `?game_gid=1001&page_size=20`
  - 错误: `?gameGid=1001&pageSize=20`

## 6. 版本标识规范

### 6.1 API 版本
- **格式**: `/api/v{major}/`
  - 正确: `/api/v1/events`, `/api/v2/events`
  - 错误: `/api/events/v1`, `/api/v2.0/events`

### 6.2 文件版本
- **格式**: `{原文件名}_v{version}.{扩展名}` 或 `{原文件名}_{日期}.{扩展名}`
  - 正确: `events_v2.py`, `games_20260223_backup.py`
  - 错误: `events-new.py`, `games_old.py`

## 7. 命名检查清单

### 7.1 新文件检查
- [ ] 文件名是否符合规范
- [ ] 目录名是否符合规范
- [ ] 类名是否符合规范
- [ ] 函数名是否符合规范
- [ ] 变量名是否符合规范

### 7.2 重构检查
- [ ] 是否有不符合规范的旧命名
- [ ] 是否需要创建迁移计划
- [ ] 是否更新了所有引用

---
创建日期: 2026-02-23
维护人: Event2Table团队
