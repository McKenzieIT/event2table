/**
 * GraphQL Module
 *
 * Re-export all GraphQL functionality from shared module
 * This directory is kept for backward compatibility
 *
 * All GraphQL operations are now defined in @shared/graphql/
 */

// Re-export client
export { client, apolloClient } from '../shared/graphql/client';

// Re-export queries
export * from './queries';

// Re-export mutations
export * from '../shared/graphql/mutations';

// Re-export hooks
export * from '../shared/graphql/hooks';

// Re-export subscription hooks
export * from '../shared/graphql/subscriptionHooks';

// Re-export subscriptions
export * from '../shared/graphql/subscriptions';

// Re-export batch mutations
export * from '../shared/graphql/batchMutations';

// Re-export config
export { apolloClient as configApolloClient, performanceConfig, complexityLimits } from '../shared/graphql/config';