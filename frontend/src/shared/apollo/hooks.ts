/**
 * Custom GraphQL Hooks
 *
 * React hooks for GraphQL operations
 * Provides convenient wrappers around Apollo Client hooks
 */

import { useQuery, useMutation, useLazyQuery } from '@apollo/client/react';
import {
  GET_GAMES,
  GET_GAME,
  SEARCH_GAMES,
  GET_EVENTS,
  GET_EVENT,
  SEARCH_EVENTS,
  GET_CATEGORIES,
  GET_CATEGORY,
  GET_PARAMETERS,
  GET_PARAMETER,
  SEARCH_PARAMETERS,
  GET_FILTERED_PARAMETERS,
  GET_COMMON_PARAMETERS,
  DETECT_PARAMETER_CHANGES,
  GET_EVENT_FIELDS,
  GET_DASHBOARD_STATS,
  GET_GAME_STATS,
} from '@shared/graphql/queries';
import {
  CREATE_GAME,
  UPDATE_GAME,
  DELETE_GAME,
  CREATE_EVENT,
  UPDATE_EVENT,
  DELETE_EVENT,
  CREATE_PARAMETER,
  UPDATE_PARAMETER,
  DELETE_PARAMETER,
  CREATE_CATEGORY,
  UPDATE_CATEGORY,
  DELETE_CATEGORY,
  CHANGE_PARAMETER_TYPE,
  AUTO_SYNC_COMMON_PARAMETERS,
  BATCH_ADD_FIELDS_TO_CANVAS,
  GENERATE_HQL,
  SAVE_HQL_TEMPLATE,
  DELETE_HQL_TEMPLATE,
  CREATE_NODE,
  UPDATE_NODE,
  DELETE_NODE,
  CREATE_FLOW,
  UPDATE_FLOW,
  DELETE_FLOW,
  CREATE_TEMPLATE,
  UPDATE_TEMPLATE,
  DELETE_TEMPLATE,
  UPDATE_EVENT_PARAMETER,
  DELETE_EVENT_PARAMETER,
  SET_PARAM_CONFIG,
  ROLLBACK_EVENT_PARAMETER,
  CREATE_VALIDATION_RULE,
  CREATE_JOIN_CONFIG,
  UPDATE_JOIN_CONFIG,
  DELETE_JOIN_CONFIG,
} from '@shared/graphql/mutations';

// =============================================================================
// Games Hooks
// =============================================================================

export function useGames(limit: number = 20, offset: number = 0) {
  return useQuery(GET_GAMES, {
    variables: { limit, offset },
    fetchPolicy: 'cache-first',
  });
}

export function useGame(gid: number) {
  return useQuery(GET_GAME, {
    variables: { gid },
    fetchPolicy: 'cache-first',
  });
}

export function useSearchGames(query: string) {
  return useQuery(SEARCH_GAMES, {
    variables: { query },
    skip: !query,
    fetchPolicy: 'cache-first',
  });
}

export function useCreateGame() {
  return useMutation(CREATE_GAME, {
    refetchQueries: [{ query: GET_GAMES }],
    awaitRefetchQueries: true,
  });
}

export function useUpdateGame() {
  return useMutation(UPDATE_GAME, {
    refetchQueries: ({ gameId }) => [
      { query: GET_GAME, variables: { id: gameId } },
      { query: GET_GAMES },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteGame() {
  return useMutation(DELETE_GAME, {
    refetchQueries: [{ query: GET_GAMES }],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Events Hooks
// =============================================================================

export function useEvents(gameGid: number, category?: string, limit: number = 50, offset: number = 0) {
  return useQuery(GET_EVENTS, {
    variables: { gameGid, category, limit, offset },
    skip: !gameGid,
    fetchPolicy: 'cache-first',
  });
}

export function useEvent(id: number) {
  return useQuery(GET_EVENT, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useSearchEvents(query: string, gameGid?: number) {
  return useQuery(SEARCH_EVENTS, {
    variables: { query, gameGid },
    skip: !query,
    fetchPolicy: 'cache-first',
  });
}

export function useCreateEvent() {
  return useMutation(CREATE_EVENT, {
    refetchQueries: ({ data }) => [
      { query: GET_EVENTS, variables: { gameGid: data?.createEvent?.event?.gameGid } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useUpdateEvent() {
  return useMutation(UPDATE_EVENT, {
    refetchQueries: ({ eventId }) => [
      { query: GET_EVENT, variables: { id: eventId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteEvent() {
  return useMutation(DELETE_EVENT, {
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Categories Hooks
// =============================================================================

export function useCategories(limit: number = 50, offset: number = 0) {
  return useQuery(GET_CATEGORIES, {
    variables: { limit, offset },
    fetchPolicy: 'cache-first',
  });
}

export function useCategory(id: number) {
  return useQuery(GET_CATEGORY, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useSearchCategories(query: string) {
  return useQuery(SEARCH_CATEGORIES, {
    variables: { query },
    skip: !query,
    fetchPolicy: 'cache-first',
  });
}

export function useCreateCategory() {
  return useMutation(CREATE_CATEGORY, {
    refetchQueries: [{ query: GET_CATEGORIES }],
    awaitRefetchQueries: true,
  });
}

export function useUpdateCategory() {
  return useMutation(UPDATE_CATEGORY, {
    refetchQueries: ({ categoryId }) => [
      { query: GET_CATEGORY, variables: { id: categoryId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteCategory() {
  return useMutation(DELETE_CATEGORY, {
    refetchQueries: [{ query: GET_CATEGORIES }],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Parameters Hooks
// =============================================================================

export function useParameters(eventId: number, activeOnly: boolean = true) {
  return useQuery(GET_PARAMETERS, {
    variables: { eventId, activeOnly },
    skip: !eventId,
    fetchPolicy: 'cache-first',
  });
}

export function useParameter(id: number) {
  return useQuery(GET_PARAMETER, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useSearchParameters(query: string, eventId: number) {
  return useQuery(SEARCH_PARAMETERS, {
    variables: { query, eventId },
    skip: !query || !eventId,
    fetchPolicy: 'cache-first',
  });
}

export function useCreateParameter() {
  return useMutation(CREATE_PARAMETER, {
    refetchQueries: ({ data }) => [
      { query: GET_PARAMETERS, variables: { eventId: data?.createParameter?.parameter?.eventId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useUpdateParameter() {
  return useMutation(UPDATE_PARAMETER, {
    refetchQueries: ({ parameterId }) => [
      { query: GET_PARAMETER, variables: { id: parameterId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteParameter() {
  return useMutation(DELETE_PARAMETER, {
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Parameter Management Hooks (Enhanced)
// =============================================================================

export function useFilteredParameters(
  gameGid: number,
  mode: 'ALL' | 'COMMON' | 'NON_COMMON' = 'ALL',
  eventId?: number
) {
  return useQuery(GET_FILTERED_PARAMETERS, {
    variables: { gameGid, mode, eventId },
    skip: !gameGid,
    fetchPolicy: 'cache-and-network',
    pollInterval: 30000, // 30秒轮询
  });
}

export function useCommonParameters(gameGid: number, threshold: number = 0.8) {
  return useQuery(GET_COMMON_PARAMETERS, {
    variables: { gameGid, threshold },
    skip: !gameGid,
    fetchPolicy: 'cache-and-network',
  });
}

export function useDetectParameterChanges(gameGid: number) {
  return useQuery(DETECT_PARAMETER_CHANGES, {
    variables: { gameGid },
    skip: !gameGid,
    fetchPolicy: 'cache-and-network',
    pollInterval: 30000, // 30秒轮询
  });
}

export function useChangeParameterType() {
  return useMutation(CHANGE_PARAMETER_TYPE, {
    refetchQueries: ({ gameGid }) => [
      { query: GET_FILTERED_PARAMETERS, variables: { gameGid, mode: 'ALL' } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useAutoSyncCommonParameters() {
  return useMutation(AUTO_SYNC_COMMON_PARAMETERS, {
    refetchQueries: ({ gameGid }) => [
      { query: GET_COMMON_PARAMETERS, variables: { gameGid } },
      { query: GET_FILTERED_PARAMETERS, variables: { gameGid, mode: 'ALL' } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useBatchAddFieldsToCanvas() {
  return useMutation(BATCH_ADD_FIELDS_TO_CANVAS, {
    refetchQueries: ({ eventId }) => [
      { query: GET_EVENT_FIELDS, variables: { eventId } },
    ],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Dashboard Hooks
// =============================================================================

export function useDashboardStats() {
  return useQuery(GET_DASHBOARD_STATS, {
    fetchPolicy: 'cache-and-network',
    pollInterval: 60000, // 1分钟轮询
  });
}

export function useGameStats(gameGid: number) {
  return useQuery(GET_GAME_STATS, {
    variables: { gameGid },
    skip: !gameGid,
    fetchPolicy: 'cache-and-network',
    pollInterval: 60000,
  });
}

// =============================================================================
// Event Node Builder Hooks
// =============================================================================

export function useEventFields(eventId: number, fieldType: 'ALL' | 'PARAMS' | 'NON_COMMON' | 'COMMON' | 'BASE' = 'ALL') {
  return useQuery(GET_EVENT_FIELDS, {
    variables: { eventId, fieldType },
    skip: !eventId,
    fetchPolicy: 'cache-first',
  });
}

// =============================================================================
// HQL Hooks
// =============================================================================

export function useGenerateHql() {
  return useMutation(GENERATE_HQL, {
    refetchQueries: () => [],
  });
}

export function useSaveHqlTemplate() {
  return useMutation(SAVE_HQL_TEMPLATE, {
    refetchQueries: ({ templateId }) => [
      { query: GET_TEMPLATES },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteHqlTemplate() {
  return useMutation(DELETE_HQL_TEMPLATE, {
    refetchQueries: () => [
      { query: GET_TEMPLATES },
    ],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Templates Hooks
// =============================================================================

export function useTemplates(gameGid?: number, category?: string, search?: string, limit: number = 20, offset: number = 0) {
  return useQuery(GET_TEMPLATES, {
    variables: { gameGid, category, search, limit, offset },
    fetchPolicy: 'cache-first',
  });
}

export function useTemplate(id: number) {
  return useQuery(GET_TEMPLATE, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useCreateTemplate() {
  return useMutation(CREATE_TEMPLATE, {
    refetchQueries: () => [
      { query: GET_TEMPLATES },
    ],
    awaitRefetchQueries: true,
  });
}

export function useUpdateTemplate() {
  return useMutation(UPDATE_TEMPLATE, {
    refetchQueries: ({ templateId }) => [
      { query: GET_TEMPLATE, variables: { id: templateId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteTemplate() {
  return useMutation(DELETE_TEMPLATE, {
    refetchQueries: () => [
      { query: GET_TEMPLATES },
    ],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Nodes and Flows Hooks
// =============================================================================

export function useNodes(gameGid?: number, nodeType?: string, limit: number = 50, offset: number = 0) {
  return useQuery(GET_NODES, {
    variables: { gameGid, nodeType, limit, offset },
    fetchPolicy: 'cache-first',
  });
}

export function useNode(id: number) {
  return useQuery(GET_NODE, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useFlows(gameGid?: number, flowType?: string, limit: number = 50, offset: number = 0) {
  return useQuery(GET_FLOWS, {
    variables: { gameGid, flowType, limit, offset },
    fetchPolicy: 'cache-first',
  });
}

export function useFlow(id: number) {
  return useQuery(GET_FLOW, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useCreateNode() {
  return useMutation(CREATE_NODE, {
    refetchQueries: () => [
      { query: GET_NODES },
    ],
    awaitRefetchQueries: true,
  });
}

export function useUpdateNode() {
  return useMutation(UPDATE_NODE, {
    refetchQueries: ({ nodeId }) => [
      { query: GET_NODE, variables: { id: nodeId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteNode() {
  return useMutation(DELETE_NODE, {
    refetchQueries: () => [
      { query: GET_NODES },
    ],
    awaitRefetchQueries: true,
  });
}

export function useCreateFlow() {
  return useMutation(CREATE_FLOW, {
    refetchQueries: () => [
      { query: GET_FLOWS },
    ],
    awaitRefetchQueries: true,
  });
}

export function useUpdateFlow() {
  return useMutation(UPDATE_FLOW, {
    refetchQueries: ({ flowId }) => [
      { query: GET_FLOW, variables: { id: flowId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteFlow() {
  return useMutation(DELETE_FLOW, {
    refetchQueries: () => [
      { query: GET_FLOWS },
    ],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Event Parameter Extended Hooks
// =============================================================================

export function useUpdateEventParameter() {
  return useMutation(UPDATE_EVENT_PARAMETER, {
    refetchQueries: ({ parameterId }) => [
      { query: GET_EVENT_PARAMETER_EXTENDED, variables: { id: parameterId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteEventParameter() {
  return useMutation(DELETE_EVENT_PARAMETER, {
    refetchQueries: ({ paramId }) => [
      { query: GET_PARAM_HISTORY, variables: { paramId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useSetParamConfig() {
  return useMutation(SET_PARAM_CONFIG, {
    refetchQueries: ({ paramId }) => [
      { query: GET_PARAM_CONFIG, variables: { paramId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useRollbackEventParameter() {
  return useMutation(ROLLBACK_EVENT_PARAMETER, {
    refetchQueries: ({ paramId }) => [
      { query: GET_EVENT_PARAMETER_EXTENDED, variables: { id: paramId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useCreateValidationRule() {
  return useMutation(CREATE_VALIDATION_RULE, {
    refetchQueries: ({ paramId }) => [
      { query: GET_VALIDATION_RULES, variables: { paramId } },
    ],
    awaitRefetchQueries: true,
  });
}

// =============================================================================
// Join Config Hooks
// =============================================================================

export function useJoinConfigs(gameId: number, joinType?: string, limit: number = 50, offset: number = 0) {
  return useQuery(GET_JOIN_CONFIGS, {
    variables: { gameId, joinType, limit, offset },
    fetchPolicy: 'cache-first',
  });
}

export function useJoinConfig(id: number) {
  return useQuery(GET_JOIN_CONFIG, {
    variables: { id },
    fetchPolicy: 'cache-first',
  });
}

export function useCreateJoinConfig() {
  return useMutation(CREATE_JOIN_CONFIG, {
    refetchQueries: () => [
      { query: GET_JOIN_CONFIGS },
    ],
    awaitRefetchQueries: true,
  });
}

export function useUpdateJoinConfig() {
  return useMutation(UPDATE_JOIN_CONFIG, {
    refetchQueries: ({ configId }) => [
      { query: GET_JOIN_CONFIG, variables: { id: configId } },
    ],
    awaitRefetchQueries: true,
  });
}

export function useDeleteJoinConfig() {
  return useMutation(DELETE_JOIN_CONFIG, {
    refetchQueries: () => [
      { query: GET_JOIN_CONFIGS },
    ],
    awaitRefetchQueries: true,
  });
}
