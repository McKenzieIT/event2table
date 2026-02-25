// @ts-nocheck - TypeScript检查暂禁用
/**
 * Events Feature Module
 *
 * Centralized exports for all events-related functionality
 */

// Types - use shared types
export type { Event, Field } from '@shared/types';

// API
export * from './api';

// Hooks
export * from './hooks';

// Components
export * from './components';

// GraphQL Components
export { default as EventManagementModalGraphQL } from './EventManagementModalGraphQL';
export { default as AddEventModalGraphQL } from './AddEventModalGraphQL';
