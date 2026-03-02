// GraphQL查询和变更定义
// 统一管理所有GraphQL操作

import { gql } from '@apollo/client';

// ============================================================================
// 游戏管理 (Games)
// ============================================================================

export const GET_GAMES = gql`
  query GetGames($limit: Int, $offset: Int) {
    games(limit: $limit, offset: $offset) {
      id
      gid
      name
      ods_db
      iconPath
      eventCount
      parameterCount
      createdAt
      updatedAt
    }
  }
`;

export const GET_GAME = gql`
  query GetGame($gid: Int!) {
    game(gid: $gid) {
      id
      gid
      name
      ods_db
      iconPath
      createdAt
      updatedAt
    }
  }
`;

export const SEARCH_GAMES = gql`
  query SearchGames($query: String!) {
    searchGames(query: $query) {
      id
      gid
      name
      ods_db
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

// ============================================================================
// 事件管理 (Events)
// ============================================================================

export const GET_EVENTS = gql`
  query GetEvents($game_gid: Int!, $category: String, $limit: Int, $offset: Int) {
    events(game_gid: $game_gid, category: $category, limit: $limit, offset: $offset) {
      id
      eventName
      eventNameCn
      gameGid
      categoryId
      categoryName
      paramCount
      createdAt
      updatedAt
    }
  }
`;

export const GET_EVENT = gql`
  query GetEvent($id: Int!) {
    event(id: $id) {
      id
      eventName
      eventNameCn
      gameGid
      categoryId
      categoryName
      paramCount
      createdAt
      updatedAt
    }
  }
`;

export const SEARCH_EVENTS = gql`
  query SearchEvents($query: String!, $game_gid: Int) {
    searchEvents(query: $query, game_gid: $game_gid) {
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
  query GetParameters($event_id: Int!, $activeOnly: Boolean) {
    parameters(event_id: $event_id, activeOnly: $activeOnly) {
      id
      paramName
      paramType
      jsonPath
      isActive
      createdAt
      updatedAt
    }
  }
`;

export const GET_PARAMETER = gql`
  query GetParameter($id: Int!) {
    parameter(id: $id) {
      id
      paramName
      paramType
      jsonPath
      isActive
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
      description
      createdAt
      updatedAt
    }
  }
`;

export const GET_CATEGORY = gql`
  query GetCategory($id: Int!) {
    category(id: $id) {
      id
      name
      description
      createdAt
      updatedAt
    }
  }
`;

export const SEARCH_CATEGORIES = gql`
  query SearchCategories($query: String!) {
    searchCategories(query: $query) {
      id
      name
      description
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
  query GetFlows($game_gid: Int, $flow_type: String, $limit: Int, $offset: Int) {
    flows(game_gid: $game_gid, flow_type: $flow_type, limit: $limit, offset: $offset) {
      id
      name
      flowType
      gameGid
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
      name
      flowType
      gameGid
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
      activeGames
      activeEvents
    }
  }
`;

export const GET_GAME_STATS = gql`
  query GetGameStats($game_gid: Int!) {
    gameStats(game_gid: $game_gid) {
      totalEvents
      activeEvents
      totalParameters
      totalFlows
    }
  }
`;

export const GET_ALL_GAME_STATS = gql`
  query GetAllGameStats($limit: Int) {
    allGameStats(limit: $limit) {
      gameGid
      gameName
      totalEvents
      activeEvents
      totalParameters
      totalFlows
    }
  }
`;
