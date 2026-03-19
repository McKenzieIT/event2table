// GraphQL查询和变更定义
// 统一管理所有GraphQL操作

import { gql } from '@apollo/client';

// ============================================================================
// 游戏管理 (Games)
// ============================================================================

export const GET_GAMES = gql`
  query GetGames($limit: Int, $offset: Int) {
    games(limit: $limit, offset: $offset) {
      gid
      name
      odsDb
      eventCount
      parameterCount
    }
  }
`;

export const GET_GAME = gql`
  query GetGame($gid: Int!) {
    game(gid: $gid) {
      gid
      name
      odsDb
      eventCount
      parameterCount
    }
  }
`;

export const SEARCH_GAMES = gql`
  query SearchGames($query: String!) {
    searchGames(query: $query) {
      gid
      name
      odsDb
    }
  }
`;

export const CREATE_GAME = gql`
  mutation CreateGame($gid: Int!, $name: String!, $ods_db: String!) {
    createGame(gid: $gid, name: $name, ods_db: $ods_db) {
      ok
      game {
        id
        gid
        name
        ods_db
        createdAt
      }
      errors
    }
  }
`;

export const UPDATE_GAME = gql`
  mutation UpdateGame($gid: Int!, $name: String, $ods_db: String) {
    updateGame(gid: $gid, name: $name, ods_db: $ods_db) {
      ok
      game {
        id
        gid
        name
        ods_db
        updatedAt
      }
      errors
    }
  }
`;

export const DELETE_GAME = gql`
  mutation DeleteGame($gid: Int!, $confirm: Boolean) {
    deleteGame(gid: $gid, confirm: $confirm) {
      ok
      message
      errors
    }
  }
`;

export const BATCH_DELETE_GAMES = gql`
  mutation BatchDeleteGames($ids: [Int!]!) {
    batchDeleteGames(ids: $ids) {
      ok
      deletedCount
      errors
    }
  }
`;

// ============================================================================
// 事件管理 (Events)
// ============================================================================

export const GET_EVENTS = gql`
  query GetEvents($gameGid: Int!, $category: String, $limit: Int, $offset: Int) {
    events(gameGid: $gameGid, category: $category, limit: $limit, offset: $offset) {
      id
      eventName
      eventNameCn
      categoryName
      paramCount
    }
  }
`;

export const GET_EVENT = gql`
  query GetEvent($id: Int!) {
    event(id: $id) {
      id
      gameGid
      eventName
      eventNameCn
      categoryId
      categoryName
      sourceTable
      targetTable
      paramCount
    }
  }
`;

export const SEARCH_EVENTS = gql`
  query SearchEvents($query: String!, $gameGid: Int) {
    searchEvents(query: $query, gameGid: $gameGid) {
      id
      eventName
      eventNameCn
      gameGid
    }
  }
`;

export const CREATE_EVENT = gql`
  mutation CreateEvent($game_gid: Int!, $event_name: String!, $event_name_cn: String, $category_id: Int) {
    createEvent(game_gid: $game_gid, event_name: $event_name, event_name_cn: $event_name_cn, category_id: $category_id) {
      ok
      event {
        id
        eventName
        eventNameCn
        gameGid
      }
      errors
    }
  }
`;

export const UPDATE_EVENT = gql`
  mutation UpdateEvent($id: Int!, $event_name: String, $event_name_cn: String, $category_id: Int) {
    updateEvent(id: $id, event_name: $event_name, event_name_cn: $event_name_cn, category_id: $category_id) {
      ok
      event {
        id
        eventName
        eventNameCn
      }
      errors
    }
  }
`;

export const DELETE_EVENT = gql`
  mutation DeleteEvent($id: Int!) {
    deleteEvent(id: $id) {
      ok
      message
      errors
    }
  }
`;

// ============================================================================
// 参数管理 (Parameters)
// ============================================================================

export const GET_PARAMETERS = gql`
  query GetParameters($eventId: Int!, $activeOnly: Boolean) {
    parameters(eventId: $eventId, activeOnly: $activeOnly) {
      id
      eventId
      paramName
      paramNameCn
      paramType
      paramDescription
      jsonPath
      isActive
      version
    }
  }
`;

export const GET_PARAMETER = gql`
  query GetParameter($id: Int!) {
    parameter(id: $id) {
      id
      eventId
      paramName
      paramNameCn
      paramType
      paramDescription
      jsonPath
      isActive
      version
    }
  }
`;

export const SEARCH_PARAMETERS = gql`
  query SearchParameters($query: String!, $eventId: Int) {
    searchParameters(query: $query, eventId: $eventId) {
      id
      eventId
      paramName
      paramNameCn
      paramType
    }
  }
`;

export const GET_EVENT_FIELDS = gql`
  query GetEventFields($eventId: Int!, $fieldType: FieldTypeEnum) {
    eventFields(eventId: $eventId, fieldType: $fieldType) {
      name
      displayName
      type
      category
      isCommon
      dataType
      jsonPath
      usageCount
    }
  }
`;

export const GET_COMMON_PARAMETERS = gql`
  query GetCommonParameters($gameGid: Int!, $threshold: Float) {
    commonParameters(gameGid: $gameGid, threshold: $threshold) {
      paramName
      paramType
      paramDescription
      occurrenceCount
      totalEvents
      threshold
      eventCodes
      isCommon
      commonalityScore
    }
  }
`;

export const GET_PARAMETERS_MANAGEMENT = gql`
  query GetParametersManagement($gameGid: Int!, $mode: ParameterFilterModeEnum, $eventId: Int) {
    parametersManagement(gameGid: $gameGid, mode: $mode, eventId: $eventId) {
      id
      eventId
      paramName
      paramNameCn
      paramType
      paramDescription
      jsonPath
      isActive
      version
      usageCount
      eventsCount
      isCommon
      eventCode
      eventName
      gameGid
      createdAt
      updatedAt
    }
  }
`;

export const GET_PARAMETER_CHANGES = gql`
  query GetParameterChanges($gameGid: Int!, $parameterId: Int, $limit: Int) {
    parameterChanges(gameGid: $gameGid, parameterId: $parameterId, limit: $limit) {
      id
      parameterId
      changeType
      oldValue
      newValue
      changedBy
      changedAt
    }
  }
`;

export const GET_ALL_PARAMETERS_BY_GAME = gql`
  query GetAllParametersByGame($gameGid: Int!) {
    parametersManagement(gameGid: $gameGid, mode: "all") {
      id
      paramName
      paramNameCn
      paramType
      paramDescription
      jsonPath
      isActive
      version
      usageCount
      eventsCount
      isCommon
      eventCode
      eventName
      gameGid
      createdAt
      updatedAt
    }
  }
`;

export const CREATE_PARAMETER = gql`
  mutation CreateParameter($event_id: Int!, $param_name: String!, $param_type: String!, $json_path: String) {
    createParameter(event_id: $event_id, param_name: $param_name, param_type: $param_type, json_path: $json_path) {
      ok
      parameter {
        id
        paramName
        paramType
        jsonPath
      }
      errors
    }
  }
`;

export const UPDATE_PARAMETER = gql`
  mutation UpdateParameter($id: Int!, $param_name: String, $param_type: String, $json_path: String, $is_active: Boolean) {
    updateParameter(id: $id, param_name: $param_name, param_type: $param_type, json_path: $json_path, is_active: $is_active) {
      ok
      parameter {
        id
        paramName
        paramType
        jsonPath
        isActive
      }
      errors
    }
  }
`;

export const DELETE_PARAMETER = gql`
  mutation DeleteParameter($id: Int!) {
    deleteParameter(id: $id) {
      ok
      message
      errors
    }
  }
`;

// ============================================================================
// 分类管理 (Categories)
// ============================================================================

export const GET_CATEGORIES = gql`
  query GetCategories($limit: Int, $offset: Int) {
    categories(limit: $limit, offset: $offset) {
      id
      name
      eventCount
    }
  }
`;

export const GET_CATEGORY = gql`
  query GetCategory($id: Int!) {
    category(id: $id) {
      id
      name
      eventCount
    }
  }
`;

export const SEARCH_CATEGORIES = gql`
  query SearchCategories($query: String!) {
    searchCategories(query: $query) {
      id
      name
      eventCount
    }
  }
`;

export const CREATE_CATEGORY = gql`
  mutation CreateCategory($name: String!, $description: String) {
    createCategory(name: $name, description: $description) {
      ok
      category {
        id
        name
        description
      }
      errors
    }
  }
`;

export const UPDATE_CATEGORY = gql`
  mutation UpdateCategory($id: Int!, $name: String, $description: String) {
    updateCategory(id: $id, name: $name, description: $description) {
      ok
      category {
        id
        name
        description
      }
      errors
    }
  }
`;

export const DELETE_CATEGORY = gql`
  mutation DeleteCategory($id: Int!) {
    deleteCategory(id: $id) {
      ok
      message
      errors
    }
  }
`;

// ============================================================================
// 流程管理 (Flows)
// ============================================================================

export const GET_FLOWS = gql`
  query GetFlows($gameGid: Int, $flowType: String, $limit: Int, $offset: Int) {
    flows(gameGid: $gameGid, flowType: $flowType, limit: $limit, offset: $offset) {
      id
      gameGid
      name
      flowType
      config
      createdAt
      updatedAt
    }
  }
`;

export const GET_FLOW = gql`
  query GetFlow($id: Int!) {
    flow(id: $id) {
      id
      gameGid
      name
      flowType
      config
      createdAt
      updatedAt
    }
  }
`;

export const CREATE_FLOW = gql`
  mutation CreateFlow($name: String!, $flow_type: String!, $game_gid: Int!, $config: String) {
    createFlow(name: $name, flow_type: $flow_type, game_gid: $game_gid, config: $config) {
      ok
      flow {
        id
        name
        flowType
        gameGid
      }
      errors
    }
  }
`;

export const UPDATE_FLOW = gql`
  mutation UpdateFlow($id: Int!, $name: String, $config: String) {
    updateFlow(id: $id, name: $name, config: $config) {
      ok
      flow {
        id
        name
        config
      }
      errors
    }
  }
`;

export const DELETE_FLOW = gql`
  mutation DeleteFlow($id: Int!) {
    deleteFlow(id: $id) {
      ok
      message
      errors
    }
  }
`;

// ============================================================================
// 仪表盘统计 (Dashboard)
// ============================================================================

export const GET_DASHBOARD_STATS = gql`
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
`;

export const GET_GAME_STATS = gql`
  query GetGameStats($gameGid: Int!) {
    gameStats(gameGid: $gameGid) {
      gameGid
      gameName
      eventCount
      parameterCount
      categoryCount
    }
  }
`;

export const GET_ALL_GAME_STATS = gql`
  query GetAllGameStats($limit: Int) {
    allGameStats(limit: $limit) {
      gameGid
      gameName
      eventCount
      parameterCount
      categoryCount
    }
  }
`;

// ============================================================================
// 模板管理 (Templates)
// ============================================================================

export const GET_TEMPLATES = gql`
  query GetTemplates($gameGid: Int, $category: String, $search: String, $limit: Int, $offset: Int) {
    templates(gameGid: $gameGid, category: $category, search: $search, limit: $limit, offset: $offset) {
      id
      name
      content
      category
      description
      createdAt
      updatedAt
    }
  }
`;

export const GET_TEMPLATE = gql`
  query GetTemplate($id: Int!) {
    template(id: $id) {
      id
      name
      content
      category
      description
      createdAt
      updatedAt
    }
  }
`;

export const CREATE_TEMPLATE = gql`
  mutation CreateTemplate($name: String!, $content: String!, $category: String, $description: String) {
    createTemplate(name: $name, content: $content, category: $category, description: $description) {
      ok
      template {
        id
        name
        content
        category
        description
        createdAt
      }
      errors
    }
  }
`;

export const UPDATE_TEMPLATE = gql`
  mutation UpdateTemplate($id: Int!, $name: String, $content: String, $category: String, $description: String) {
    updateTemplate(id: $id, name: $name, content: $content, category: $category, description: $description) {
      ok
      template {
        id
        name
        content
        category
        description
        updatedAt
      }
      errors
    }
  }
`;

export const DELETE_TEMPLATE = gql`
  mutation DeleteTemplate($id: Int!) {
    deleteTemplate(id: $id) {
      ok
      message
      errors
    }
  }
`;

// ============================================================================
// 节点管理 (Nodes)
// ============================================================================

export const GET_NODES = gql`
  query GetNodes($gameGid: Int, $nodeType: String, $limit: Int, $offset: Int) {
    nodes(gameGid: $gameGid, nodeType: $nodeType, limit: $limit, offset: $offset) {
      id
      gameGid
      nodeType
      nodeName
      config
      createdAt
      updatedAt
    }
  }
`;