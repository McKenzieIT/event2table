// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
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

// 错误处理链接 - 带详细日志
const errorLink = onError(({ graphQLErrors, networkError, operation, forward, response }) => {
  // GraphQL错误 - 详细上下文
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

      // 记录验证错误详情
      if (error.extensions?.code === 'GRAPHQL_VALIDATION_FAILED') {
        console.error('Validation Failed - Check query syntax');
      }

      // 处理特定错误码
      if (error.extensions?.code === 'UNAUTHENTICATED') {
        console.warn('User is not authenticated - Redirecting to login');
      }

      if (error.extensions?.code === 'FORBIDDEN') {
        console.warn('Access forbidden - Insufficient permissions');
      }

      console.groupEnd();
    });

    console.groupEnd();
  }

  // 网络错误 - 详细上下文
  if (networkError) {
    console.group('❌ Network Error');
    console.error('Query:', operation.operationName);
    console.error('Variables:', JSON.stringify(operation.variables, null, 2));
    console.error('Error:', networkError);
    console.error('Error Message:', networkError.message);

    // 提取状态码（如果可用）
    const statusCode = (networkError as any).statusCode;
    if (statusCode) {
      console.error('Status Code:', statusCode);

      // 处理特定状态码
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

    // 记录响应体（如果可用）
    const result = (networkError as any).result;
    if (result) {
      console.error('Response Body:', result);
    }

    console.groupEnd();
  }

  // 记录部分响应（当errorPolicy: 'all'时）
  if (response && response.errors && response.data) {
    console.group('⚠️ Partial Response');
    console.warn('Query:', operation.operationName);
    console.warn('Partial Data:', response.data);
    console.warn('Errors:', response.errors);
    console.groupEnd();
  }

  return forward(operation);
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
