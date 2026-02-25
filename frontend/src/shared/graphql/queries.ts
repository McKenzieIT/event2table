import { gql } from '@apollo/client';

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

export const GET_EVENTS = gql`
  query GetEvents($gameGid: Int!, $category: String, $limit: Int, $offset: Int) {
    events(gameGid: $gameGid, category: $category, limit: $limit, offset: $offset) {
      id
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

export const GET_FILTERED_PARAMETERS = gql`
  query GetFilteredParameters(
    $gameGid: Int!
    $fieldType: String!
    $search: String
    $limit: Int
    $offset: Int
  ) {
    filteredParameters(
      gameGid: $gameGid
      fieldType: $fieldType
      search: $search
      limit: $limit
      offset: $offset
    ) {
      id
      eventId
      eventName
      paramName
      paramNameCn
      paramType
      paramDescription
      jsonPath
      isActive
      version
      fieldType
    }
  }
`;

export const GET_COMMON_PARAMETERS = gql`
  query GetCommonParameters($gameGid: Int!, $limit: Int, $offset: Int) {
    commonParameters(gameGid: $gameGid, limit: $limit, offset: $offset) {
      paramName
      paramNameCn
      paramType
      eventCount
      sampleEvents {
        id
        eventName
        eventNameCn
      }
    }
  }
`;

export const DETECT_PARAMETER_CHANGES = gql`
  query DetectParameterChanges(
    $gameGid: Int!
    $sinceVersion: Int!
    $eventId: Int
  ) {
    detectParameterChanges(
      gameGid: $gameGid
      sinceVersion: $sinceVersion
      eventId: $eventId
    ) {
      paramId
      paramName
      oldVersion
      newVersion
      changeType
      changedFields
      timestamp
    }
  }
`;

export const GET_EVENT_FIELDS = gql`
  query GetEventFields($eventId: Int!) {
    eventFields(eventId: $eventId) {
      fieldType
      fieldName
      displayName
      jsonPath
      paramId
      isActive
    }
  }
`;

export const GET_DASHBOARD_STATS = gql`
  query GetDashboardStats {
    dashboardStats {
      totalGames
      totalEvents
      totalParameters
      totalCategories
      activeUsers
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
      templateCount
      lastUpdated
    }
  }
`;
