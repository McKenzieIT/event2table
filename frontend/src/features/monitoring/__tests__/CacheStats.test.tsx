/**
 * CacheStats Component Tests
 *
 * Tests for CacheStats component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@test/test-utils';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CacheStats } from '../components/CacheStats';
import * as monitoringApi from '../api/monitoringApi';

// Mock API functions
vi.mock('../api/monitoringApi');
vi.mock('@shared/ui', () => ({
  Spinner: () => <div data-testid="spinner">Loading...</div>,
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('CacheStats Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show loading state', () => {
    vi.mocked(monitoringApi.getCacheStats).mockImplementation(
      () => new Promise(() => {})
    );

    render(<CacheStats />, { wrapper: createWrapper() });

    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('should render cache statistics successfully', async () => {
    const mockData = {
      hit_rate: 0.85,
      miss_rate: 0.15,
      total_requests: 10000,
      cache_size: 512,
      eviction_count: 50,
      timestamp: '2026-03-20T00:00:00Z',
    };

    vi.mocked(monitoringApi.getCacheStats).mockResolvedValueOnce(mockData);

    render(<CacheStats />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Cache Statistics')).toBeInTheDocument();
    });

    expect(screen.getByText('Hit Rate')).toBeInTheDocument();
    expect(screen.getByText('85.00')).toBeInTheDocument();
    expect(screen.getByText('Miss Rate')).toBeInTheDocument();
    expect(screen.getByText('15.00')).toBeInTheDocument();
    expect(screen.getByText('Total Requests')).toBeInTheDocument();
    expect(screen.getByText('10000.00')).toBeInTheDocument();
    expect(screen.getByText('Cache Size')).toBeInTheDocument();
    expect(screen.getByText('512.00')).toBeInTheDocument();
    expect(screen.getByText('MB')).toBeInTheDocument();
    expect(screen.getByText('Eviction Count')).toBeInTheDocument();
    expect(screen.getByText('50.00')).toBeInTheDocument();
  });

  it('should render error state', async () => {
    const mockError = new Error('Failed to load');
    vi.mocked(monitoringApi.getCacheStats).mockRejectedValueOnce(mockError);

    render(<CacheStats />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Failed to load cache statistics')).toBeInTheDocument();
    });

    expect(screen.getByText('Failed to load')).toBeInTheDocument();
  });
});
