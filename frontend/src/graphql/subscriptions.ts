/**
 * GraphQL Subscriptions
 * 
 * GraphQL订阅定义,用于实时数据更新
 */

import { gql } from '@apollo/client';

/**
 * Subscribe to event updates
 */
export const ON_EVENT_UPDATED = gql`
  subscription OnEventUpdated($gameGid: Int!) {
    eventUpdated(gameGid: $gameGid) {
      id
      eventName
      eventNameCn
      categoryId
      categoryName
      paramCount
      updatedAt
    }
  }
`;

/**
 * Subscribe to parameter updates
 */
export const ON_PARAMETER_UPDATED = gql`
  subscription OnParameterUpdated($eventId: Int!) {
    parameterUpdated(eventId: $eventId) {
      id
      eventId
      paramName
      paramNameCn
      paramType
      isActive
      updatedAt
    }
  }
`;

/**
 * Subscribe to game updates
 */
export const ON_GAME_UPDATED = gql`
  subscription OnGameUpdated($gid: Int!) {
    gameUpdated(gid: $gid) {
      gid
      name
      odsDb
      eventCount
      parameterCount
      updatedAt
    }
  }
`;

/**
 * Subscribe to category updates
 */
export const ON_CATEGORY_UPDATED = gql`
  subscription OnCategoryUpdated($gameGid: Int!) {
    categoryUpdated(gameGid: $gameGid) {
      id
      name
      description
      eventCount
      updatedAt
    }
  }
`;

/**
 * Subscribe to HQL generation updates
 */
export const ON_HQL_GENERATED = gql`
  subscription OnHQLGenerated($gameGid: Int!) {
    hqlGenerated(gameGid: $gameGid) {
      id
      eventName
      hql
      status
      createdAt
    }
  }
`;

/**
 * Subscribe to all events in a game
 */
export const ON_GAME_EVENTS_CHANGED = gql`
  subscription OnGameEventsChanged($gameGid: Int!) {
    gameEventsChanged(gameGid: $gameGid) {
      changeType
      event {
        id
        eventName
        eventNameCn
      }
    }
  }
`;
