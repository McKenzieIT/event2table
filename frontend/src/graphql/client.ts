// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Apollo Client Configuration
 * 
 * GraphQL client for Event2Table application
 */

import { ApolloClient, InMemoryCache, createHttpLink, ApolloLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

// HTTP link to GraphQL endpoint
// Use relative URI to leverage Vite proxy in development
const httpLink = createHttpLink({
  uri: '/api/graphql',
});

// Auth link (optional - add authentication if needed)
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
const errorLink = new ApolloLink((operation, forward) => {
  return forward(operation).map(response => {
    // Check for errors with detailed logging
    if (response.errors) {
      console.group('❌ GraphQL Errors');
      console.error('Query:', operation.operationName);
      console.error('Variables:', JSON.stringify(operation.variables, null, 2));
      console.error('Error Count:', response.errors.length);

      response.errors.forEach((error, index) => {
        console.group(`Error #${index + 1}`);
        console.error('Message:', error.message);
        console.error('Path:', error.path);
        console.error('Locations:', error.locations);
        console.error('Extensions:', error.extensions);
        console.groupEnd();
      });

      console.groupEnd();
    }
    return response;
  });
});

// Create Apollo Client
export const client = new ApolloClient({
  link: ApolloLink.from([
    errorLink,
    authLink.concat(httpLink),
  ]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          // Cache games list
          games: {
            keyArgs: ['limit', 'offset'],
            merge(existing, incoming) {
              return incoming;
            },
          },
          // Cache events list
          events: {
            keyArgs: ['gameGid', 'category'],
            merge(existing, incoming) {
              return incoming;
            },
          },
        },
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
});

export default client;
