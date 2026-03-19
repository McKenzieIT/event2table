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

// HTTP link to GraphQL endpoint
// Use relative URI to leverage Vite proxy in development
const httpLink = createHttpLink({
  uri: '/api/graphql',
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

// Error handling link with detailed logging
const errorLink = onError(({ graphQLErrors, networkError, operation, forward, response }) => {
  // GraphQL errors with detailed context
  if (graphQLErrors) {
    console.group('❌ GraphQL Errors');
    console.error('Query:', operation.operationName);
    console.error('Variables:', JSON.stringify(operation.variables, null, 2));
    console.error('Error Count:', graphQLErrors.length);

    graphQLErrors.forEach((error, index) => {
      console.group(`Error #${index + 1}`);
      console.error('Message:', error.message);
      console.error('Path:', error.path);
      console.error('Locations:', error.locations);
      console.error('Extensions:', error.extensions);

      // Log validation errors with details
      if (error.extensions?.code === 'GRAPHQL_VALIDATION_FAILED') {
        console.error('Validation Failed - Check query syntax');
      }

      // Handle specific error codes
      if (error.extensions?.code === 'UNAUTHENTICATED') {
        console.warn('User is not authenticated - Redirecting to login');
        // Redirect to login or refresh token
      }

      if (error.extensions?.code === 'FORBIDDEN') {
        console.warn('Access forbidden - Insufficient permissions');
      }

      console.groupEnd();
    });

    console.groupEnd();
  }

  // Network errors with detailed context
  if (networkError) {
    console.group('❌ Network Error');
    console.error('Query:', operation.operationName);
    console.error('Variables:', JSON.stringify(operation.variables, null, 2));
    console.error('Error:', networkError);
    console.error('Error Message:', networkError.message);

    // Extract status code if available
    const statusCode = (networkError as { statusCode?: number }).statusCode;
    if (statusCode) {
      console.error('Status Code:', statusCode);

      // Handle specific status codes
      if (statusCode === 401) {
        console.warn('Unauthorized - Clearing auth token');
        localStorage.removeItem('authToken');
      } else if (statusCode === 403) {
        console.warn('Forbidden - Insufficient permissions');
      } else if (statusCode === 400) {
        console.warn('Bad Request - Check query syntax and variables');
      } else if (statusCode === 500) {
        console.error('Internal Server Error - Server-side problem');
      } else if (statusCode === 502) {
        console.error('Bad Gateway - Server may be down or unreachable');
      } else if (statusCode === 503) {
        console.error('Service Unavailable - Server overloaded or maintenance');
      }
    }

    // Log response body if available
    const result = (networkError as { result?: unknown }).result;
    if (result) {
      console.error('Response Body:', result);
    }

    console.groupEnd();
  }

  // Log partial responses (when errorPolicy: 'all')
  if (response && response.errors && response.data) {
    console.group('⚠️ Partial Response');
    console.warn('Query:', operation.operationName);
    console.warn('Partial Data:', response.data);
    console.warn('Errors:', response.errors);
    console.groupEnd();
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
export const client = new ApolloClient({
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

              const { offset = 0 } = args as { offset?: number };
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

              const { offset = 0 } = args as { offset?: number };
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
