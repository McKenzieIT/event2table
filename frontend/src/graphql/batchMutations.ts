/**
 * GraphQL Batch Mutations
 * 
 * 批量操作的GraphQL mutations定义
 * 用于批量创建、更新、删除操作
 */

import { gql } from '@apollo/client';

/**
 * Batch delete events
 */
export const BATCH_DELETE_EVENTS = gql`
  mutation BatchDeleteEvents($ids: [Int!]!) {
    batchDeleteEvents(ids: $ids) {
      ok
      deletedCount
      message
      errors
    }
  }
`;

/**
 * Batch delete categories
 */
export const BATCH_DELETE_CATEGORIES = gql`
  mutation BatchDeleteCategories($ids: [Int!]!) {
    batchDeleteCategories(ids: $ids) {
      ok
      deletedCount
      message
      errors
    }
  }
`;

/**
 * Batch delete parameters
 */
export const BATCH_DELETE_PARAMETERS = gql`
  mutation BatchDeleteParameters($ids: [Int!]!) {
    batchDeleteParameters(ids: $ids) {
      ok
      deletedCount
      message
      errors
    }
  }
`;

/**
 * Batch update events
 */
export const BATCH_UPDATE_EVENTS = gql`
  mutation BatchUpdateEvents($updates: [EventUpdateInput!]!) {
    batchUpdateEvents(updates: $updates) {
      ok
      updatedCount
      message
      errors
    }
  }
`;

/**
 * Batch create parameters
 */
export const BATCH_CREATE_PARAMETERS = gql`
  mutation BatchCreateParameters($parameters: [ParameterInput!]!) {
    batchCreateParameters(parameters: $parameters) {
      ok
      createdCount
      message
      errors
      parameters {
        id
        paramName
        paramNameCn
      }
    }
  }
`;

/**
 * Batch assign category to events
 */
export const BATCH_ASSIGN_CATEGORY = gql`
  mutation BatchAssignCategory($eventIds: [Int!]!, $categoryId: Int!) {
    batchAssignCategory(eventIds: $eventIds, categoryId: $categoryId) {
      ok
      updatedCount
      message
      errors
    }
  }
`;
