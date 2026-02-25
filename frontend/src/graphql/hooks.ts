/**
 * Custom GraphQL Hooks
 *
 * React hooks for GraphQL operations
 */

import { useQuery, useMutation } from '@apollo/client/react';
import {
  GET_GAMES,
  GET_GAME,
  SEARCH_GAMES,
  GET_EVENTS,
  GET_EVENT,
  SEARCH_EVENTS,
  GET_CATEGORIES,
  GET_CATEGORY,
  SEARCH_CATEGORIES,
  GET_PARAMETERS,
  GET_PARAMETER,
  SEARCH_PARAMETERS,
  GET_DASHBOARD_STATS,
  GET_GAME_STATS,
  GET_ALL_GAME_STATS,
  GET_FLOWS,
  GET_FLOW,
  GET_ALL_PARAMETERS_BY_GAME,
} from './queries';
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
  GENERATE_HQL,
  SAVE_HQL_TEMPLATE,
  DELETE_HQL_TEMPLATE,
} from './mutations';

/**
 * Hook to fetch games list
 */
export function useGames(limit: number = 20, offset: number = 0) {
  return useQuery(GET_GAMES, {
    variables: { limit, offset },
  });
}

/**
 * Hook to fetch a single game
 */
export function useGame(gid: number) {
  return useQuery(GET_GAME, {
    variables: { gid },
    skip: !gid,
  });
}

/**
 * Hook to search games
 */
export function useSearchGames(query: string) {
  return useQuery(SEARCH_GAMES, {
    variables: { query },
    skip: !query,
  });
}

/**
 * Hook to fetch events for a game
 */
export function useEvents(gameGid: number, limit: number = 50, offset: number = 0) {
  return useQuery(GET_EVENTS, {
    variables: { gameGid, limit, offset },
    skip: !gameGid,
  });
}

/**
 * Hook to fetch a single event
 */
export function useEvent(id: number) {
  return useQuery(GET_EVENT, {
    variables: { id },
    skip: !id,
  });
}

/**
 * Hook to search events
 */
export function useSearchEvents(query: string, gameGid?: number) {
  return useQuery(SEARCH_EVENTS, {
    variables: { query, gameGid },
    skip: !query,
  });
}

/**
 * Hook to fetch categories list
 */
export function useCategories(limit: number = 50, offset: number = 0) {
  return useQuery(GET_CATEGORIES, {
    variables: { limit, offset },
  });
}

/**
 * Hook to fetch a single category
 */
export function useCategory(id: number) {
  return useQuery(GET_CATEGORY, {
    variables: { id },
    skip: !id,
  });
}

/**
 * Hook to search categories
 */
export function useSearchCategories(query: string) {
  return useQuery(SEARCH_CATEGORIES, {
    variables: { query },
    skip: !query,
  });
}

/**
 * Hook to fetch parameters for an event
 */
export function useParameters(eventId: number, activeOnly: boolean = true) {
  return useQuery(GET_PARAMETERS, {
    variables: { eventId, activeOnly },
    skip: !eventId,
  });
}

/**
 * Hook to fetch a single parameter
 */
export function useParameter(id: number) {
  return useQuery(GET_PARAMETER, {
    variables: { id },
    skip: !id,
  });
}

/**
 * Hook to search parameters
 */
export function useSearchParameters(query: string, eventId?: number) {
  return useQuery(SEARCH_PARAMETERS, {
    variables: { query, eventId },
    skip: !query,
  });
}

/**
 * Hook to create a game
 */
export function useCreateGame() {
  return useMutation(CREATE_GAME, {
    refetchQueries: [
      { query: GET_GAMES, variables: { limit: 20, offset: 0 } },
    ],
  });
}

/**
 * Hook to update a game
 */
export function useUpdateGame() {
  return useMutation(UPDATE_GAME);
}

/**
 * Hook to delete a game
 */
export function useDeleteGame() {
  return useMutation(DELETE_GAME, {
    refetchQueries: [
      { query: GET_GAMES, variables: { limit: 20, offset: 0 } },
    ],
  });
}

/**
 * Hook to create an event
 */
export function useCreateEvent() {
  return useMutation(CREATE_EVENT);
}

/**
 * Hook to update an event
 */
export function useUpdateEvent() {
  return useMutation(UPDATE_EVENT);
}

/**
 * Hook to delete an event
 */
export function useDeleteEvent() {
  return useMutation(DELETE_EVENT);
}

/**
 * Hook to create a parameter
 */
export function useCreateParameter() {
  return useMutation(CREATE_PARAMETER);
}

/**
 * Hook to update a parameter
 */
export function useUpdateParameter() {
  return useMutation(UPDATE_PARAMETER);
}

/**
 * Hook to delete a parameter
 */
export function useDeleteParameter() {
  return useMutation(DELETE_PARAMETER);
}

/**
 * Hook to create a category
 */
export function useCreateCategory() {
  return useMutation(CREATE_CATEGORY, {
    refetchQueries: [
      { query: GET_CATEGORIES, variables: { limit: 50, offset: 0 } },
    ],
  });
}

/**
 * Hook to update a category
 */
export function useUpdateCategory() {
  return useMutation(UPDATE_CATEGORY);
}

/**
 * Hook to delete a category
 */
export function useDeleteCategory() {
  return useMutation(DELETE_CATEGORY, {
    refetchQueries: [
      { query: GET_CATEGORIES, variables: { limit: 50, offset: 0 } },
    ],
  });
}

// ============================================
// HQL Hooks
// ============================================

/**
 * Hook to generate HQL from events
 */
export function useGenerateHQL() {
  return useMutation(GENERATE_HQL);
}

/**
 * Hook to save HQL as a template
 */
export function useSaveHQLTemplate() {
  return useMutation(SAVE_HQL_TEMPLATE);
}

/**
 * Hook to delete an HQL template
 */
export function useDeleteHQLTemplate() {
  return useMutation(DELETE_HQL_TEMPLATE);
}

// ============================================
// Dashboard Hooks
// ============================================

/**
 * Hook to fetch dashboard statistics
 */
export function useDashboardStats() {
  return useQuery(GET_DASHBOARD_STATS);
}

/**
 * Hook to fetch game statistics
 */
export function useGameStats(gameGid: number) {
  return useQuery(GET_GAME_STATS, {
    variables: { gameGid },
    skip: !gameGid,
  });
}

/**
 * Hook to fetch all game statistics
 */
export function useAllGameStats(limit: number = 20) {
  return useQuery(GET_ALL_GAME_STATS, {
    variables: { limit },
  });
}

// ============================================
// Flows Hooks
// ============================================

/**
 * Hook to fetch flows
 */
export function useFlows(gameGid?: number, flowType?: string, limit: number = 50, offset: number = 0) {
  return useQuery(GET_FLOWS, {
    variables: { gameGid, flowType, limit, offset },
  });
}

/**
 * Hook to fetch a single flow
 */
export function useFlow(id: number) {
  return useQuery(GET_FLOW, {
    variables: { id },
    skip: !id,
  });
}

// ============================================
// Categories Hooks (Extended)
// ============================================

/**
 * Hook to fetch categories for a specific game
 */
export function useCategoriesByGame(gameGid: number, limit: number = 50, offset: number = 0) {
  return useQuery(GET_CATEGORIES, {
    variables: { limit, offset },
    context: {
      headers: {
        'X-Game-GID': gameGid.toString()
      }
    },
    skip: !gameGid,
  });
}

/**
 * Hook to fetch all parameters for a game
 */
export function useAllParametersByGame(gameGid: number) {
  return useQuery(GET_ALL_PARAMETERS_BY_GAME, {
    variables: { gameGid },
    skip: !gameGid,
  });
}
