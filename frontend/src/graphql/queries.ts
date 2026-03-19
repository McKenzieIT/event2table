/**
 * GraphQL Queries
 *
 * Re-export all GraphQL operations from shared module
 * This file is kept for backward compatibility
 *
 * All GraphQL operations are now defined in @shared/graphql/operations
 */

export {
  // Games
  GET_GAMES,
  GET_GAME,
  SEARCH_GAMES,
  // Events
  GET_EVENTS,
  GET_EVENT,
  SEARCH_EVENTS,
  // Parameters
  GET_PARAMETERS,
  GET_PARAMETER,
  SEARCH_PARAMETERS,
  GET_EVENT_FIELDS,
  GET_COMMON_PARAMETERS,
  GET_PARAMETERS_MANAGEMENT,
  GET_PARAMETER_CHANGES,
  GET_ALL_PARAMETERS_BY_GAME,
  // Categories
  GET_CATEGORIES,
  GET_CATEGORY,
  SEARCH_CATEGORIES,
  // Flows
  GET_FLOWS,
  GET_FLOW,
  // Dashboard
  GET_DASHBOARD_STATS,
  GET_GAME_STATS,
  GET_ALL_GAME_STATS,
  // Templates
  GET_TEMPLATES,
  GET_TEMPLATE,
  // Nodes
  GET_NODES,
} from '../shared/graphql/operations';
