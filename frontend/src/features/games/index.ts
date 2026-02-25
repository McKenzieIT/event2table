/**
 * Games Feature Module
 *
 * Centralized exports for all games-related functionality
 */

// Types
export * from './types';

// API
export * from './api';

// Hooks
export * from './hooks';

// Components - GraphQL versions
export { default as GameManagementModal } from './GameManagementModalGraphQL';
export { default as AddGameModal } from './AddGameModalGraphQL';

// Legacy REST API versions (archived)
// export { default as GameManagementModal } from './GameManagementModal';
// export { default as AddGameModal } from './AddGameModal';
