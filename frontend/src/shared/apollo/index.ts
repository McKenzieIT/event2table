/**
 * Apollo GraphQL Module
 *
 * Main export point for Apollo Client configuration and hooks
 * Provides ApolloProvider, client instance, and React hooks
 */

import { ApolloProvider } from '@apollo/client/react';
import { client } from './client';

// Export ApolloProvider for wrapping the app
export { ApolloProvider };

// Export client instance
export { client };

// Export Apollo Client hooks for convenience
export { useQuery, useMutation, useLazyQuery, useSubscription } from '@apollo/client/react';

// Export custom hooks
export * from './hooks';
