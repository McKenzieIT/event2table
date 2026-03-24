// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * graphqlQueryOptimizer.test.ts
 * Unit tests for GraphQL Query Optimizer
 */

import { describe, it, expect, beforeEach } from 'vitest';

import { GraphQLQueryOptimizer } from './graphqlQueryOptimizer';

describe('GraphQLQueryOptimizer', () => {
  let optimizer: GraphQLQueryOptimizer;

  beforeEach(() => {
    optimizer = new GraphQLQueryOptimizer();
  });

  describe('analyzeQueryComplexity', () => {
    it('should analyze simple query complexity', () => {
      const query = `query {
        user {
          id
          name
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);

      expect(complexity).toHaveProperty('depth');
      expect(complexity).toHaveProperty('breadth');
      expect(complexity).toHaveProperty('fields');
      expect(complexity).toHaveProperty('score');
      expect(complexity.depth).toBeGreaterThan(0);
      expect(complexity.fields).toBeGreaterThan(0);
    });

    it('should calculate depth correctly', () => {
      const query = `query {
        user {
          profile {
            settings {
              theme
            }
          }
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);
      expect(complexity.depth).toBeGreaterThan(1);
    });

    it('should count fields correctly', () => {
      const query = `query {
        user {
          id
          name
          email
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);
      expect(complexity.fields).toBe(3); // id, name, email
    });

    it('should calculate complexity score', () => {
      const query = `query {
        user {
          id
          name
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);
      expect(complexity.score).toBeGreaterThan(0);
      expect(complexity.score).toBe(complexity.depth * 10 + complexity.breadth);
    });

    it('should ignore comments', () => {
      const query = `query {
        # This is a comment
        user {
          id
          # Another comment
          name
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);
      expect(complexity.fields).toBe(2); // id, name (comments not counted)
    });

    it('should handle empty query', () => {
      const complexity = optimizer.analyzeQueryComplexity('');
      expect(complexity.depth).toBe(0);
      expect(complexity.fields).toBe(0);
      expect(complexity.score).toBe(0);
    });
  });

  describe('isQueryTooComplex', () => {
    it('should return false for simple queries', () => {
      const query = `query {
        user {
          id
          name
        }
      }`;

      const isTooComplex = optimizer.isQueryTooComplex(query, 1000);
      expect(isTooComplex).toBe(false);
    });

    it('should return true for complex queries', () => {
      const deepQuery = `query {
        a {
          b {
            c {
              d {
                e {
                  f {
                    id
                  }
                }
              }
            }
          }
        }
      }`;

      const isTooComplex = optimizer.isQueryTooComplex(deepQuery, 50);
      expect(isTooComplex).toBe(true);
    });

    it('should use default max score', () => {
      const simpleQuery = `query {
        user {
          id
        }
      }`;

      expect(optimizer.isQueryTooComplex(simpleQuery)).toBe(false);
    });

    it('should respect custom max score', () => {
      const query = `query {
        user {
          id
          name
          email
        }
      }`;

      expect(optimizer.isQueryTooComplex(query, 1)).toBe(true);
      expect(optimizer.isQueryTooComplex(query, 1000)).toBe(false);
    });
  });

  describe('optimizeQuery', () => {
    it('should remove duplicate fields', () => {
      const query = `query {
        user {
          id
          name
          id
          email
          name
        }
      }`;

      const optimized = optimizer.optimizeQuery(query);
      const lines = optimized.split('\n').filter(l => l.trim() === 'id');

      expect(lines.length).toBe(1); // Only one 'id' field
    });

    it('should preserve query structure', () => {
      const query = `query {
        user {
          id
          name
        }
      }`;

      const optimized = optimizer.optimizeQuery(query);
      expect(optimized).toContain('query');
      expect(optimized).toContain('{');
      expect(optimized).toContain('}');
    });

    it('should preserve comments', () => {
      const query = `query {
        # Get user info
        user {
          id
          name
        }
      }`;

      const optimized = optimizer.optimizeQuery(query);
      expect(optimized).toContain('# Get user info');
    });

    it('should handle empty query', () => {
      const optimized = optimizer.optimizeQuery('');
      expect(optimized).toBe('');
    });

    it('should preserve query structure while removing duplicates', () => {
      const query = `query {
        user {
          id
          name
          email
        }
        profile {
          id
          bio
        }
      }`;

      const optimized = optimizer.optimizeQuery(query);
      expect(optimized).toContain('user');
      expect(optimized).toContain('profile');
      expect(optimized).toContain('id');
      expect(optimized).toContain('name');
      expect(optimized).toContain('email');
      expect(optimized).toContain('bio');
    });
  });

  describe('mergeQueries', () => {
    it('should merge two queries', () => {
      const queries = [
        {
          query: `query GetUser {
            user {
              id
              name
            }
          }`,
          variables: { userId: 1 }
        },
        {
          query: `query GetPosts {
            posts {
              id
              title
            }
          }`,
          variables: { limit: 10 }
        }
      ];

      const merged = optimizer.mergeQueries(queries);

      expect(merged.query).toContain('query MergedQuery');
      expect(merged.query).toContain('GetUser:');
      expect(merged.query).toContain('GetPosts:');
      expect(merged.variables.userId).toBe(1);
      expect(merged.variables.limit).toBe(10);
    });

    it('should merge variables correctly', () => {
      const queries = [
        {
          query: `query Q1 { user { id } }`,
          variables: { a: 1, b: 2 }
        },
        {
          query: `query Q2 { post { id } }`,
          variables: { c: 3 }
        }
      ];

      const merged = optimizer.mergeQueries(queries);

      expect(merged.variables).toEqual({ a: 1, b: 2, c: 3 });
    });

    it('should handle queries without names', () => {
      const queries = [
        {
          query: `query {
            user { id }
          }`
        },
        {
          query: `query {
            post { id }
          }`
        }
      ];

      const merged = optimizer.mergeQueries(queries);

      expect(merged.query).toContain('Query0:');
      expect(merged.query).toContain('Query1:');
    });

    it('should handle queries without variables', () => {
      const queries = [
        {
          query: `query { user { id } }`
        },
        {
          query: `query { post { id } }`
        }
      ];

      const merged = optimizer.mergeQueries(queries);

      expect(merged.variables).toEqual({});
    });

    it('should merge multiple queries', () => {
      const queries = [
        { query: `query Q1 { user { id } }` },
        { query: `query Q2 { post { id } }` },
        { query: `query Q3 { comment { id } }` }
      ];

      const merged = optimizer.mergeQueries(queries);

      expect(merged.query).toContain('Q1:');
      expect(merged.query).toContain('Q2:');
      expect(merged.query).toContain('Q3:');
    });
  });

  describe('trackFieldUsage', () => {
    it('should track field usage', () => {
      optimizer.trackFieldUsage('User', 'id');
      optimizer.trackFieldUsage('User', 'name');
      optimizer.trackFieldUsage('User', 'id'); // Track again

      const stats = optimizer.getFieldUsageStats();

      expect(stats['User.id']).toBe(2);
      expect(stats['User.name']).toBe(1);
    });

    it('should track multiple types', () => {
      optimizer.trackFieldUsage('User', 'id');
      optimizer.trackFieldUsage('Post', 'id');
      optimizer.trackFieldUsage('Comment', 'id');

      const stats = optimizer.getFieldUsageStats();

      expect(stats['User.id']).toBe(1);
      expect(stats['Post.id']).toBe(1);
      expect(stats['Comment.id']).toBe(1);
    });

    it('should return empty stats initially', () => {
      const stats = optimizer.getFieldUsageStats();
      expect(Object.keys(stats).length).toBe(0);
    });
  });

  describe('generateOptimizationSuggestions', () => {
    it('should suggest for deep queries', () => {
      const deepQuery = `query {
        a {
          b {
            c {
              d {
                e {
                  f {
                    id
                  }
                }
              }
            }
          }
        }
      }`;

      const suggestions = optimizer.generateOptimizationSuggestions(deepQuery);

      expect(suggestions.some(s => s.type === 'depth')).toBe(true);
      expect(suggestions.some(s => s.severity === 'medium')).toBe(true);
    });

    it('should suggest for broad queries', () => {
      const broadQuery = `query {
        user {
          ${Array.from({ length: 25 }, (_, i) => `field${i}: String`).join('\n')}
        }
      }`;

      const suggestions = optimizer.generateOptimizationSuggestions(broadQuery);

      expect(suggestions.some(s => s.type === 'breadth')).toBe(true);
    });

    it('should suggest for complex queries', () => {
      const complexQuery = `query {
        ${Array.from({ length: 30 }, (_, i) => `field${i} { id name }`).join('\n')}
      }`;

      const suggestions = optimizer.generateOptimizationSuggestions(complexQuery);

      expect(suggestions.length).toBeGreaterThan(0);
    });

    it('should return no suggestions for simple queries', () => {
      const simpleQuery = `query {
        user {
          id
          name
        }
      }`;

      const suggestions = optimizer.generateOptimizationSuggestions(simpleQuery);

      expect(suggestions.length).toBe(0);
    });

    it('should include helpful messages', () => {
      const query = `query {
        a {
          b {
            c {
              d {
                e {
                  f {
                    id
                  }
                }
              }
            }
          }
        }
      }`;

      const suggestions = optimizer.generateOptimizationSuggestions(query);

      suggestions.forEach(suggestion => {
        expect(suggestion.message).toBeTruthy();
        expect(suggestion.message.length).toBeGreaterThan(0);
      });
    });
  });

  describe('cacheQuery', () => {
    it('should cache queries', () => {
      const queryKey = 'getUserQuery';
      const query = `query { user { id } }`;

      optimizer.cacheQuery(queryKey, query);

      const cached = optimizer.getCachedQuery(queryKey);
      expect(cached).toBeDefined();
      expect(cached.query).toBe(query);
    });

    it('should store timestamp', () => {
      const queryKey = 'testQuery';
      const query = `query { test { id } }`;
      const beforeCache = Date.now();

      optimizer.cacheQuery(queryKey, query);

      const cached = optimizer.getCachedQuery(queryKey);
      expect(cached.timestamp).toBeGreaterThanOrEqual(beforeCache);
      expect(cached.timestamp).toBeLessThanOrEqual(Date.now());
    });

    it('should return undefined for non-existent cache', () => {
      const cached = optimizer.getCachedQuery('nonExistent');
      expect(cached).toBeUndefined();
    });

    it('should overwrite existing cache', () => {
      const queryKey = 'testQuery';
      optimizer.cacheQuery(queryKey, 'query 1');
      optimizer.cacheQuery(queryKey, 'query 2');

      const cached = optimizer.getCachedQuery(queryKey);
      expect(cached.query).toBe('query 2');
    });
  });

  describe('clearCache', () => {
    it('should clear all cached queries', () => {
      optimizer.cacheQuery('q1', 'query 1');
      optimizer.cacheQuery('q2', 'query 2');

      optimizer.clearCache();

      const cached1 = optimizer.getCachedQuery('q1');
      const cached2 = optimizer.getCachedQuery('q2');
      expect(cached1).toBeUndefined();
      expect(cached2).toBeUndefined();
    });

    it('should be safe to call when cache is empty', () => {
      expect(() => optimizer.clearCache()).not.toThrow();
    });
  });

  describe('real-world scenarios', () => {
    it('should analyze typical user profile query', () => {
      const query = `query GetUserProfile($userId: ID!) {
        user(id: $userId) {
          id
          name
          email
          profile {
            avatar
            bio
            location
          }
          posts(limit: 10) {
            id
            title
            createdAt
          }
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);
      const isTooComplex = optimizer.isQueryTooComplex(query, 100);

      expect(complexity.depth).toBeGreaterThan(0);
      expect(complexity.fields).toBeGreaterThan(0);
      expect(isTooComplex).toBe(false);
    });

    it('should optimize query with duplicate fields', () => {
      const query = `query {
        user {
          id
          name
          email
          id
          name
        }
        profile {
          id
          bio
          id
        }
      }`;

      const optimized = optimizer.optimizeQuery(query);

      // Count occurrences of 'id' field
      const idCount = (optimized.match(/\bid\b/g) || []).length;
      expect(idCount).toBeLessThan(4); // Should be reduced from 4
    });

    it('should merge user and posts queries', () => {
      const queries = [
        {
          query: `query GetUser($id: ID!) {
            user(id: $id) {
              id
              name
            }
          }`,
          variables: { id: '123' }
        },
        {
          query: `query GetUserPosts($userId: ID!) {
            posts(userId: $userId) {
              id
              title
            }
          }`,
          variables: { userId: '123' }
        }
      ];

      const merged = optimizer.mergeQueries(queries);

      expect(merged.variables).toEqual({ id: '123', userId: '123' });
      expect(merged.query).toContain('GetUser:');
      expect(merged.query).toContain('GetUserPosts:');
    });
  });

  describe('edge cases', () => {
    it('should handle malformed queries gracefully', () => {
      const malformedQuery = `query { user { id }`;
      const complexity = optimizer.analyzeQueryComplexity(malformedQuery);
      expect(typeof complexity.score).toBe('number');
    });

    it('should handle query with only comments', () => {
      const commentOnlyQuery = `# Just a comment\n# Another comment`;
      const complexity = optimizer.analyzeQueryComplexity(commentOnlyQuery);
      expect(complexity.fields).toBe(0);
    });

    it('should handle query with nested empty objects', () => {
      const query = `query {
        user {
          profile {
            settings {
            }
          }
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(query);
      expect(typeof complexity.depth).toBe('number');
    });

    it('should handle very long queries', () => {
      const longQuery = `query {
        user {
          ${Array.from({ length: 1000 }, (_, i) => `field${i}: String`).join('\n')}
        }
      }`;

      const complexity = optimizer.analyzeQueryComplexity(longQuery);
      expect(complexity.fields).toBe(1000);
    });
  });
});
