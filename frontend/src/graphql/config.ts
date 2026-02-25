/**
 * GraphQL配置
 *
 * 性能优化配置
 */

import { ApolloClient, InMemoryCache, createHttpLink, from } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { onError } from '@apollo/client/link/error';
import { RetryLink } from '@apollo/client/link/retry';

// HTTP链接配置
const httpLink = createHttpLink({
  uri: '/api/graphql',
  credentials: 'same-origin',
});

// 认证链接
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    }
  };
});

// 错误处理链接
const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}`
      );
    });
  }

  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});

// 重试链接
const retryLink = new RetryLink({
  delay: {
    initial: 300,
    max: 3000,
    jitter: true,
  },
  attempts: {
    max: 3,
    retryIf: (error, _operation) => !!error,
  },
});

// 缓存配置
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        // 游戏列表分页
        games: {
          keyArgs: ['limit', 'offset'],
          merge(existing, incoming, { args }) {
            if (!args) return incoming;
            
            const { offset = 0 } = args;
            const merged = existing ? existing.slice(0) : [];
            
            for (let i = 0; i < incoming.length; ++i) {
              merged[offset + i] = incoming[i];
            }
            
            return merged;
          },
        },
        // 事件列表分页
        events: {
          keyArgs: ['gameGid', 'category'],
          merge(existing, incoming, { args }) {
            if (!args) return incoming;
            
            const { offset = 0 } = args;
            const merged = existing ? existing.slice(0) : [];
            
            for (let i = 0; i < incoming.length; ++i) {
              merged[offset + i] = incoming[i];
            }
            
            return merged;
          },
        },
      },
    },
    Game: {
      keyFields: ['gid'],
      fields: {
        events: {
          merge(existing, incoming) {
            return incoming;
          },
        },
      },
    },
    Event: {
      keyFields: ['id'],
    },
  },
});

// 创建Apollo Client
export const apolloClient = new ApolloClient({
  link: from([
    retryLink,
    errorLink,
    authLink.concat(httpLink),
  ]),
  cache,
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
  connectToDevTools: process.env.NODE_ENV === 'development',
});

// 性能监控配置
export const performanceConfig = {
  // 查询超时时间（毫秒）
  queryTimeout: 30000,
  
  // 缓存时间（毫秒）
  cacheTime: 5 * 60 * 1000, // 5分钟
  
  // 分页大小
  pageSize: 20,
  
  // 预加载配置
  prefetch: {
    enabled: true,
    delay: 200, // 延迟预加载（毫秒）
  },
  
  // 批量请求配置
  batch: {
    enabled: true,
    maxBatchSize: 10,
    batchInterval: 10, // 批量请求间隔（毫秒）
  },
};

// 查询复杂度限制
export const complexityLimits = {
  maxDepth: 10,
  maxFields: 100,
  maxAliases: 10,
};

export default apolloClient;
