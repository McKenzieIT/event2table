/**
 * FieldRecommendation Component Tests
 *
 * Unit tests for field recommendation UI components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { FieldRecommendation } from '../components/FieldRecommendation';
import { FieldRecommendationDropdown } from '../components/FieldRecommendationDropdown';
import { FieldTypeSuggestion } from '../components/FieldTypeSuggestion';

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

// Mock the API
vi.mock('../api/fieldRecommendationApi', () => ({
  getRecommendations: vi.fn(),
  getCommonPatterns: vi.fn(),
  inferFieldType: vi.fn(),
}));

// Mock the hooks
vi.mock('../hooks/useCommonPatterns', () => ({
  useCommonPatterns: vi.fn(),
}));

import { getRecommendations, getCommonPatterns, inferFieldType } from '../api/fieldRecommendationApi';
import { useCommonPatterns } from '../hooks/useCommonPatterns';

describe('FieldRecommendation Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render recommendation buttons', () => {
    const onApplyRecommendation = vi.fn();
    const onApplyTypeInference = vi.fn();

    render(
      <FieldRecommendation
        paramName="userId"
        gameGid={10000147}
        onApplyRecommendation={onApplyRecommendation}
        onApplyTypeInference={onApplyTypeInference}
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('智能推荐')).toBeInTheDocument();
    expect(screen.getByText('类型推断')).toBeInTheDocument();
  });

  it('should disable buttons when paramName is empty', () => {
    const onApplyRecommendation = vi.fn();
    const onApplyTypeInference = vi.fn();

    render(
      <FieldRecommendation
        paramName=""
        gameGid={10000147}
        onApplyRecommendation={onApplyRecommendation}
        onApplyTypeInference={onApplyTypeInference}
      />,
      { wrapper: createWrapper() }
    );

    const smartRecommendButton = screen.getByText('智能推荐').closest('button');
    const typeInferButton = screen.getByText('类型推断').closest('button');

    expect(smartRecommendButton).toBeDisabled();
    expect(typeInferButton).toBeDisabled();
  });

  it('should call onApplyRecommendation when recommendation is applied', async () => {
    const mockRecommendation = {
      recommendedName: 'user_id',
      recommendedType: 'string',
      confidence: 0.95,
      alternatives: [],
      reason: 'Matches pattern',
    };

    (getRecommendations as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockRecommendation);

    const onApplyRecommendation = vi.fn();
    const onApplyTypeInference = vi.fn();

    render(
      <FieldRecommendation
        paramName="userId"
        gameGid={10000147}
        onApplyRecommendation={onApplyRecommendation}
        onApplyTypeInference={onApplyTypeInference}
      />,
      { wrapper: createWrapper() }
    );

    // Click smart recommendation button
    fireEvent.click(screen.getByText('智能推荐'));

    await waitFor(() => {
      expect(screen.getByText('应用推荐')).toBeInTheDocument();
    });

    // Click apply button
    fireEvent.click(screen.getByText('应用推荐'));

    expect(onApplyRecommendation).toHaveBeenCalledWith(mockRecommendation);
  });
});

describe('FieldRecommendationDropdown Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock useCommonPatterns to return empty data by default
    (useCommonPatterns as ReturnType<typeof vi.fn>).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      isSuccess: true,
      isError: false,
    });
  });

  it('should render dropdown trigger', () => {
    const onSelectPattern = vi.fn();

    render(
      <FieldRecommendationDropdown
        onSelectPattern={onSelectPattern}
        placeholder="选择字段模式..."
      />,
      { wrapper: createWrapper() }
    );

    expect(screen.getByText('选择字段模式...')).toBeInTheDocument();
  });

  it('should open dropdown when clicked', () => {
    const onSelectPattern = vi.fn();

    render(
      <FieldRecommendationDropdown
        onSelectPattern={onSelectPattern}
        placeholder="选择字段模式..."
      />,
      { wrapper: createWrapper() }
    );

    const trigger = screen.getByText('选择字段模式...').closest('button');
    fireEvent.click(trigger!);

    // Should show search input
    expect(screen.getByPlaceholderText('搜索字段模式...')).toBeInTheDocument();
  });

  it('should call onSelectPattern when pattern is selected', async () => {
    const mockPatterns = [
      {
        name: 'user_id',
        description: 'User identifier',
        examples: ['123'],
        fieldType: 'string',
      },
    ];

    // Mock useCommonPatterns to return patterns
    (useCommonPatterns as ReturnType<typeof vi.fn>).mockReturnValue({
      data: mockPatterns,
      isLoading: false,
      error: null,
      isSuccess: true,
      isError: false,
    });

    const onSelectPattern = vi.fn();

    render(
      <FieldRecommendationDropdown
        onSelectPattern={onSelectPattern}
        placeholder="选择字段模式..."
      />,
      { wrapper: createWrapper() }
    );

    // Open dropdown
    const trigger = screen.getByText('选择字段模式...').closest('button');
    fireEvent.click(trigger!);

    await waitFor(() => {
      expect(screen.getByText('user_id')).toBeInTheDocument();
    });

    // Click on pattern
    fireEvent.click(screen.getByText('user_id'));

    expect(onSelectPattern).toHaveBeenCalledWith(mockPatterns[0]);
  });
});

describe('FieldTypeSuggestion Component', () => {
  it('should render type suggestion with confidence', () => {
    const mockInference = {
      inferredType: 'int',
      confidence: 0.9,
      possibleTypes: [
        { type: 'int', probability: 0.9 },
        { type: 'string', probability: 0.1 },
      ],
      reasoning: 'Numeric values detected',
    };

    const onApplyType = vi.fn();

    render(
      <FieldTypeSuggestion
        inferenceData={mockInference}
        onApplyType={onApplyType}
      />
    );

    expect(screen.getByText('推荐类型')).toBeInTheDocument();
    expect(screen.getByText('int')).toBeInTheDocument();
    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('Numeric values detected')).toBeInTheDocument();
  });

  it('should call onApplyType when apply button is clicked', () => {
    const mockInference = {
      inferredType: 'int',
      confidence: 0.9,
      possibleTypes: [
        { type: 'int', probability: 0.9 },
        { type: 'string', probability: 0.1 },
      ],
      reasoning: 'Numeric values detected',
    };

    const onApplyType = vi.fn();

    render(
      <FieldTypeSuggestion
        inferenceData={mockInference}
        onApplyType={onApplyType}
      />
    );

    fireEvent.click(screen.getByText('应用推荐类型'));

    expect(onApplyType).toHaveBeenCalledWith('int');
  });

  it('should show alternative types when showAllTypes is true', () => {
    const mockInference = {
      inferredType: 'int',
      confidence: 0.9,
      possibleTypes: [
        { type: 'int', probability: 0.9 },
        { type: 'string', probability: 0.1 },
      ],
      reasoning: 'Numeric values detected',
    };

    const onApplyType = vi.fn();

    render(
      <FieldTypeSuggestion
        inferenceData={mockInference}
        onApplyType={onApplyType}
        showAllTypes={true}
      />
    );

    expect(screen.getByText('其他可能类型:')).toBeInTheDocument();
    expect(screen.getByText('string')).toBeInTheDocument();
  });
});
