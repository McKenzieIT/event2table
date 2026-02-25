/**
 * Apollo Client Configuration
 *
 * GraphQL client for Event2Table application
 * Enhanced configuration with error handling, retry logic, and type policies
 */

import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { RetryLink } from '@apollo/client/link/retry';
import type { ApolloQueryResult } from '@apollo/client';
import type { FetchResult } from '@apollo/client';
import type { DocumentNode } from 'graphql';

// HTTP link to GraphQL endpoint
const httpLink = createHttpLink({
  uri: 'http://127.0.0.1:5001/api/graphql',
  credentials: 'same-origin',
});

// Auth link - add authentication headers if needed
const authLink = setContext((_, { headers }) => {
  // Get authentication token from local storage if it exists
  const token = localStorage.getItem('authToken');

  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    }
  };
});

// Error handling link
const errorLink = onError(({ graphQLErrors, networkError, operation, forward }) => {
  // GraphQL errors
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path, extensions }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`,
        extensions
      );

      // Handle specific error codes
      if (extensions?.code === 'UNAUTHENTICATED') {
        // Redirect to login or refresh token
        console.log('User is not authenticated');
      }
    });
  }

  // Network errors
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);

    // Handle network error (e.g., server is down)
    if ('statusCode' in networkError && networkError.statusCode === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken');
    }
  }

  return forward(operation);
});

// Retry link for failed requests
const retryLink = new RetryLink({
  delay: {
    initial: 300,
    max: 3000,
    jitter: true,
  },
  attempts: {
    max: 3,
    retryIf: (error, _operation) => {
      // Retry on network errors
      return !!error && 'statusCode' in error && error.statusCode !== 401;
    },
  },
});

// Create Apollo Client with enhanced configuration
export const client: ApolloClient<any> = new ApolloClient({
  link: from([
    retryLink,
    errorLink,
    authLink.concat(httpLink),
  ]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          // Cache games list with pagination
          games: {
            keyArgs: ['limit', 'offset'],
            merge: (existing, incoming, args) => {
              if (!args) return incoming;

              const { offset = 0 } = args;
              const merged = existing ? existing.slice(0) : [];

              for (let i = 0; i < incoming.length; ++i) {
                merged[offset + i] = incoming[i];
              }

              return merged;
            },
          },

          // Cache events list with pagination
          events: {
            keyArgs: ['gameGid', 'category'],
            merge: (existing, incoming, args) => {
              if (!args) return incoming;

              const { offset = 0 } = args;
              const merged = existing ? existing.slice(0) : [];

              for (let i = 0; i < incoming.length; ++i) {
                merged[offset + i] = incoming[i];
              }

              return merged;
            },
          },

          // Cache parameters list
          parameters: {
            keyArgs: ['eventId', 'activeOnly'],
            merge: (existing, incoming) => {
              return incoming;
            },
          },

          // Cache common parameters
          commonParameters: {
            keyArgs: false,
            merge: (existing, incoming) => {
              return incoming;
            },
          },

          // Cache filtered parameters
          filteredParameters: {
            keyArgs: ['gameGid', 'fieldType', 'search'],
            merge: (existing, incoming) => {
              return incoming;
            },
          },
        },
      },
      Game: {
        keyFields: ['gid'],
        fields: {
          events: {
            merge: (existing, incoming) => {
              return incoming;
            },
          },
        },
      },
      Event: {
        keyFields: ['id'],
      },
      Parameter: {
        keyFields: ['id'],
      },
      Category: {
        keyFields: ['id'],
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
      errorPolicy: 'all',
    },
    query: {
      fetchPolicy: 'cache-first',
      errorPolicy: 'all',
    },
    mutate: {
      errorPolicy: 'all',
    },
  },
  connectToDevTools: import.meta.env.DEV,
});

export default client;
