/**
 * useFieldRecommendations Hook Tests
 *
 * Unit tests for field recommendation React Query hooks
 */

import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import React from 'react';
import { useFieldRecommendations } from '../hooks/useFieldRecommendations';
import { useCommonPatterns } from '../hooks/useCommonPatterns';
import { useFieldTypeInference } from '../hooks/useFieldTypeInference';
import { getRecommendations, getCommonPatterns as fetchPatterns, inferFieldType as fetchTypeInference } from '../api/fieldRecommendationApi';

// Mock the API functions
vi.mock('../api/fieldRecommendationApi');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useFieldRecommendations', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call getRecommendations when mutate is invoked', async () => {
    const mockRecommendation = {
      recommendedName: 'user_id',
      recommendedType: 'string',
      confidence: 0.95,
      alternatives: [],
      reason: 'Matches pattern',
    };

    (getRecommendations as jest.Mock).mockResolvedValueOnce(mockRecommendation);

    const { result } = renderHook(() => useFieldRecommendations(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      paramName: 'userId',
      gameGid: 10000147,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(getRecommendations).toHaveBeenCalledWith({
      paramName: 'userId',
      gameGid: 10000147,
    });
    expect(result.current.data).toEqual(mockRecommendation);
  });

  it('should handle errors correctly', async () => {
    const mockError = new Error('API Error');
    (getRecommendations as any).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useFieldRecommendations(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      paramName: 'userId',
      gameGid: 10000147,
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(mockError);
  });
});

describe('useCommonPatterns', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch common patterns on mount', async () => {
    const mockPatterns = [
      {
        name: 'user_id',
        description: 'User identifier',
        examples: ['123'],
        fieldType: 'string',
      },
    ];

    (fetchPatterns as any).mockResolvedValueOnce(mockPatterns);

    const { result } = renderHook(() => useCommonPatterns(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(fetchPatterns).toHaveBeenCalled();
    expect(result.current.data).toEqual(mockPatterns);
  });

  it('should handle errors correctly', async () => {
    const mockError = new Error('Failed to fetch');
    (fetchPatterns as any).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useCommonPatterns(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(mockError);
  });
});

describe('useFieldTypeInference', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should call inferFieldType when mutate is invoked', async () => {
    const mockInference = {
      inferredType: 'int',
      confidence: 0.9,
      possibleTypes: [
        { type: 'int', probability: 0.9 },
        { type: 'string', probability: 0.1 },
      ],
      reasoning: 'Numeric values',
    };

    (fetchTypeInference as any).mockResolvedValueOnce(mockInference);

    const { result } = renderHook(() => useFieldTypeInference(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      paramName: 'userId',
      gameGid: 10000147,
      sampleValues: ['123', '456'],
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(fetchTypeInference).toHaveBeenCalledWith({
      paramName: 'userId',
      gameGid: 10000147,
      sampleValues: ['123', '456'],
    });
    expect(result.current.data).toEqual(mockInference);
  });

  it('should handle errors correctly', async () => {
    const mockError = new Error('Inference failed');
    (fetchTypeInference as any).mockRejectedValueOnce(mockError);

    const { result } = renderHook(() => useFieldTypeInference(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      paramName: 'userId',
      gameGid: 10000147,
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(mockError);
  });
});
