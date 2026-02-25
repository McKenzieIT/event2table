import { gql } from '@apollo/client';

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

export const DELETE_GAME = gql`
  mutation DeleteGame($gid: Int!, $confirm: Boolean) {
    deleteGame(gid: $gid, confirm: $confirm) {
      ok
      message
      errors
    }
  }
`;

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

export const DELETE_EVENT = gql`
  mutation DeleteEvent($id: Int!) {
    deleteEvent(id: $id) {
      ok
      message
      errors
    }
  }
`;

export const CREATE_PARAMETER = gql`
  mutation CreateParameter(
    $eventId: Int!
    $paramName: String!
    $paramNameCn: String
    $paramType: String
    $paramDescription: String
    $jsonPath: String
  ) {
    createParameter(
      eventId: $eventId
      paramName: $paramName
      paramNameCn: $paramNameCn
      paramType: $paramType
      paramDescription: $paramDescription
      jsonPath: $jsonPath
    ) {
      ok
      parameter {
        id
        eventId
        paramName
        paramNameCn
        paramType
        paramDescription
        jsonPath
      }
      errors
    }
  }
`;

export const UPDATE_PARAMETER = gql`
  mutation UpdateParameter(
    $id: Int!
    $paramNameCn: String
    $paramType: String
    $paramDescription: String
    $jsonPath: String
    $isActive: Boolean
  ) {
    updateParameter(
      id: $id
      paramNameCn: $paramNameCn
      paramType: $paramType
      paramDescription: $paramDescription
      jsonPath: $jsonPath
      isActive: $isActive
    ) {
      ok
      parameter {
        id
        paramNameCn
        paramType
        paramDescription
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

export const DELETE_CATEGORY = gql`
  mutation DeleteCategory($id: Int!) {
    deleteCategory(id: $id) {
      ok
      message
      errors
    }
  }
`;

export const CHANGE_PARAMETER_TYPE = gql`
  mutation ChangeParameterType(
    $paramId: Int!
    $newType: String!
    $updateAllEvents: Boolean
  ) {
    changeParameterType(
      paramId: $paramId
      newType: $newType
      updateAllEvents: $updateAllEvents
    ) {
      ok
      parameter {
        id
        paramName
        paramType
        version
      }
      affectedEvents {
        id
        eventName
      }
      errors
    }
  }
`;

export const AUTO_SYNC_COMMON_PARAMETERS = gql`
  mutation AutoSyncCommonParameters(
    $gameGid: Int!
    $minEventCount: Int
    $dryRun: Boolean
  ) {
    autoSyncCommonParameters(
      gameGid: $gameGid
      minEventCount: $minEventCount
      dryRun: $dryRun
    ) {
      ok
      syncedParameters {
        paramName
        paramType
        eventCount
        syncedEvents {
          id
          eventName
        }
      }
      errors
      summary {
        totalProcessed
        syncedCount
        skippedCount
      }
    }
  }
`;

export const BATCH_ADD_FIELDS_TO_CANVAS = gql`
  mutation BatchAddFieldsToCanvas(
    $eventId: Int!
    $fieldType: String!
    $fieldNames: [String!]
  ) {
    batchAddFieldsToCanvas(
      eventId: $eventId
      fieldType: $fieldType
      fieldNames: $fieldNames
    ) {
      ok
      fields {
        fieldType
        fieldName
        displayName
        paramId
      }
      count
      errors
    }
  }
`;

export const GENERATE_HQL = gql`
  mutation GenerateHQL($eventIds: [Int!]!, $mode: String, $options: String) {
    generateHql(eventIds: $eventIds, mode: $mode, options: $options) {
      ok
      hql
      errors
    }
  }
`;

export const SAVE_HQL_TEMPLATE = gql`
  mutation SaveHQLTemplate(
    $name: String!
    $content: String!
    $category: String
    $description: String
  ) {
    saveHqlTemplate(
      name: $name
      content: $content
      category: $category
      description: $description
    ) {
      ok
      templateId
      errors
    }
  }
`;

export const DELETE_HQL_TEMPLATE = gql`
  mutation DeleteHQLTemplate($templateId: Int!) {
    deleteHqlTemplate(templateId: $templateId) {
      ok
      errors
    }
  }
`;

export const CREATE_NODE = gql`
  mutation CreateNode(
    $gameGid: Int!
    $nodeType: String!
    $name: String!
    $config: String
  ) {
    createNode(
      gameGid: $gameGid
      nodeType: $nodeType
      name: $name
      config: $config
    ) {
      ok
      node {
        id
        name
        nodeType
      }
      errors
    }
  }
`;

export const UPDATE_NODE = gql`
  mutation UpdateNode($id: Int!, $name: String, $config: String) {
    updateNode(id: $id, name: $name, config: $config) {
      ok
      node {
        id
        name
      }
      errors
    }
  }
`;

export const DELETE_NODE = gql`
  mutation DeleteNode($id: Int!) {
    deleteNode(id: $id) {
      ok
      message
      errors
    }
  }
`;

export const CREATE_FLOW = gql`
  mutation CreateFlow(
    $gameGid: Int!
    $flowType: String!
    $name: String!
    $nodes: [Int!]
  ) {
    createFlow(
      gameGid: $gameGid
      flowType: $flowType
      name: $name
      nodes: $nodes
    ) {
      ok
      flow {
        id
        name
        flowType
      }
      errors
    }
  }
`;

export const UPDATE_FLOW = gql`
  mutation UpdateFlow($id: Int!, $name: String, $nodes: [Int!]) {
    updateFlow(id: $id, name: $name, nodes: $nodes) {
      ok
      flow {
        id
        name
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
