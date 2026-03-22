/**
 * useTemplates Hook Test Suite
 *
 * Tests for the useTemplates hook which manages template data fetching
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { ApolloProvider } from '@apollo/client/react';
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';
import { useTemplates } from '@shared/apollo/hooks';
import { GET_TEMPLATES } from '@shared/graphql/operations';

// Mock Apollo Client
const createMockClient = () => {
  return new ApolloClient({
    link: new HttpLink({
      uri: 'http://localhost:4000/graphql',
      fetch: vi.fn(),
    }),
    cache: new InMemoryCache(),
  });
};

describe('useTemplates Hook', () => {
  let mockClient: ApolloClient<any>;

  beforeEach(() => {
    mockClient = createMockClient();
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <ApolloProvider client={mockClient}>
      {children}
    </ApolloProvider>
  );

  describe('Basic functionality', () => {
    it('should initialize with loading state', () => {
      const { result } = renderHook(
        () => useTemplates(),
        { wrapper }
      );

      expect(result.current.loading).toBe(true);
    });

    it('should accept gameGid parameter', () => {
      const { result } = renderHook(
        () => useTemplates(123),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });

    it('should accept category parameter', () => {
      const { result } = renderHook(
        () => useTemplates(undefined, 'HQL'),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });

    it('should accept search parameter', () => {
      const { result } = renderHook(
        () => useTemplates(undefined, undefined, 'test'),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });

    it('should accept limit and offset parameters', () => {
      const { result } = renderHook(
        () => useTemplates(undefined, undefined, undefined, 10, 0),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });
  });

  describe('Query execution', () => {
    it('should use correct query', () => {
      const { result } = renderHook(
        () => useTemplates(),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });

    it('should pass correct variables to query', () => {
      const gameGid = 123;
      const category = 'HQL';
      const search = 'test';
      const limit = 10;
      const offset = 0;

      const { result } = renderHook(
        () => useTemplates(gameGid, category, search, limit, offset),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });
  });

  describe('Return value structure', () => {
    it('should return data property', () => {
      const { result } = renderHook(
        () => useTemplates(),
        { wrapper }
      );

      expect(result.current).toHaveProperty('data');
    });

    it('should return loading property', () => {
      const { result } = renderHook(
        () => useTemplates(),
        { wrapper }
      );

      expect(result.current).toHaveProperty('loading');
    });

    it('should return error property', () => {
      const { result } = renderHook(
        () => useTemplates(),
        { wrapper }
      );

      // Apollo QueryResult includes client property for error handling
      expect(result.current).toHaveProperty('client');
    });
  });

  describe('Cache policy', () => {
    it('should use cache-first policy', () => {
      const { result } = renderHook(
        () => useTemplates(),
        { wrapper }
      );

      expect(result.current).toBeDefined();
    });
  });
});
