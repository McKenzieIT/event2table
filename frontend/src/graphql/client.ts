/**
 * Apollo Client Configuration
 * 
 * GraphQL client for Event2Table application
 */

import { ApolloClient, InMemoryCache, createHttpLink, ApolloLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

// HTTP link to GraphQL endpoint
const httpLink = createHttpLink({
  uri: 'http://localhost:5001/api/graphql',
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

// Error handling link
const errorLink = new ApolloLink((operation, forward) => {
  return forward(operation).map(response => {
    // Check for errors
    if (response.errors) {
      console.error('GraphQL Errors:', response.errors);
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
    },
    query: {
      fetchPolicy: 'cache-first',
    },
  },
});

export default client;
