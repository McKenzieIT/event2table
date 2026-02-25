/**
 * GraphQL Mutations
 * 
 * Mutation definitions for Event2Table GraphQL API
 */

import { gql } from '@apollo/client';

/**
 * Create a new game
 */
export const CREATE_GAME = gql`
  mutation CreateGame($gid: Int!, $name: String!, $odsDb: String!) {
    createGame(gid: $gid, name: $name, odsDb: $odsDb) {
      ok
      game {
        gid
        name
        odsDb
      }
      errors
    }
  }
`;

/**
 * Update an existing game
 */
export const UPDATE_GAME = gql`
  mutation UpdateGame($gid: Int!, $name: String, $odsDb: String) {
    updateGame(gid: $gid, name: $name, odsDb: $odsDb) {
      ok
      game {
        gid
        name
        odsDb
      }
      errors
    }
  }
`;

/**
 * Delete a game
 */
export const DELETE_GAME = gql`
  mutation DeleteGame($gid: Int!, $confirm: Boolean) {
    deleteGame(gid: $gid, confirm: $confirm) {
      ok
      message
      errors
    }
  }
`;

/**
 * Create a new event
 */
export const CREATE_EVENT = gql`
  mutation CreateEvent(
    $gameGid: Int!
    $eventName: String!
    $eventNameCn: String!
    $categoryId: Int!
    $includeInCommonParams: Boolean
  ) {
    createEvent(
      gameGid: $gameGid
      eventName: $eventName
      eventNameCn: $eventNameCn
      categoryId: $categoryId
      includeInCommonParams: $includeInCommonParams
    ) {
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

/**
 * Update an existing event
 */
export const UPDATE_EVENT = gql`
  mutation UpdateEvent(
    $id: Int!
    $eventNameCn: String
    $categoryId: Int
    $includeInCommonParams: Boolean
  ) {
    updateEvent(
      id: $id
      eventNameCn: $eventNameCn
      categoryId: $categoryId
      includeInCommonParams: $includeInCommonParams
    ) {
      ok
      event {
        id
        eventNameCn
      }
      errors
    }
  }
`;

/**
 * Delete an event
 */
export const DELETE_EVENT = gql`
  mutation DeleteEvent($id: Int!) {
    deleteEvent(id: $id) {
      ok
      message
      errors
    }
  }
`;

/**
 * Create a new parameter
 */
export const CREATE_PARAMETER = gql`
  mutation CreateParameter(
    $eventId: Int!
    $paramName: String!
    $paramNameCn: String
    $isActive: Boolean
    $jsonPath: String
    $templateId: Int
  ) {
    createParameter(
      eventId: $eventId
      paramName: $paramName
      paramNameCn: $paramNameCn
      isActive: $isActive
      jsonPath: $jsonPath
      templateId: $templateId
    ) {
      ok
      parameter {
        id
        eventId
        paramName
        paramNameCn
        isActive
        jsonPath
      }
      errors
    }
  }
`;

/**
 * Update an existing parameter
 */
export const UPDATE_PARAMETER = gql`
  mutation UpdateParameter(
    $id: Int!
    $paramNameCn: String
    $isActive: Boolean
    $jsonPath: String
    $templateId: Int
  ) {
    updateParameter(
      id: $id
      paramNameCn: $paramNameCn
      isActive: $isActive
      jsonPath: $jsonPath
      templateId: $templateId
    ) {
      ok
      parameter {
        id
        paramNameCn
        isActive
        jsonPath
      }
      errors
    }
  }
`;

/**
 * Delete a parameter
 */
export const DELETE_PARAMETER = gql`
  mutation DeleteParameter($id: Int!) {
    deleteParameter(id: $id) {
      ok
      message
      errors
    }
  }
`;

/**
 * Create a new category
 */
export const CREATE_CATEGORY = gql`
  mutation CreateCategory($name: String!) {
    createCategory(name: $name) {
      ok
      category {
        id
        name
      }
      errors
    }
  }
`;

/**
 * Update an existing category
 */
export const UPDATE_CATEGORY = gql`
  mutation UpdateCategory($id: Int!, $name: String!) {
    updateCategory(id: $id, name: $name) {
      ok
      category {
        id
        name
      }
      errors
    }
  }
`;

/**
 * Delete a category
 */
export const DELETE_CATEGORY = gql`
  mutation DeleteCategory($id: Int!) {
    deleteCategory(id: $id) {
      ok
      message
      errors
    }
  }
`;

// ============================================
// HQL Mutations
// ============================================

/**
 * Generate HQL from events
 */
export const GENERATE_HQL = gql`
  mutation GenerateHQL($eventIds: [Int!]!, $mode: String, $options: String) {
    generateHql(eventIds: $eventIds, mode: $mode, options: $options) {
      ok
      hql
      errors
    }
  }
`;

/**
 * Save HQL as a template
 */
export const SAVE_HQL_TEMPLATE = gql`
  mutation SaveHQLTemplate($name: String!, $content: String!, $category: String, $description: String) {
    saveHqlTemplate(name: $name, content: $content, category: $category, description: $description) {
      ok
      templateId
      errors
    }
  }
`;

/**
 * Delete an HQL template
 */
export const DELETE_HQL_TEMPLATE = gql`
  mutation DeleteHQLTemplate($templateId: Int!) {
    deleteHqlTemplate(templateId: $templateId) {
      ok
      errors
    }
  }
`;

// ============================================
// Event Node Builder Mutations
// ============================================

/**
 * Batch add fields to canvas
 */
export const BATCH_ADD_FIELDS_TO_CANVAS = gql`
  mutation BatchAddFieldsToCanvas($eventId: Int!, $fieldType: FieldTypeEnum!) {
    batchAddFieldsToCanvas(eventId: $eventId, fieldType: $fieldType) {
      success
      message
      result {
        success
        message
        totalCount
        successCount
        failedCount
        errors
      }
    }
  }
`;

/**
 * Change parameter type
 */
export const CHANGE_PARAMETER_TYPE = gql`
  mutation ChangeParameterType($parameterId: Int!, $newType: ParameterTypeEnum!) {
    changeParameterType(parameterId: $parameterId, newType: $newType) {
      success
      message
      parameter {
        id
        paramName
        paramNameCn
        paramType
      }
    }
  }
`;

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
