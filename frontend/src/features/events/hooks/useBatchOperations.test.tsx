/**
 * useBatchOperations Hook Tests
 *
 * 测试批量操作hooks的功能
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, act, waitFor } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import {
  useBatchEdit,
  useBatchDelete,
  useBatchValidate,
  useBatchOperations,
  type BatchEditFormData,
  type Event,
} from './useBatchOperations';

// Mock fetch
global.fetch = vi.fn();

// Mock useToast
vi.mock('@shared/ui', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  }),
}));

describe('useBatchEdit', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should successfully batch edit events', async () => {
    const mockResponse = {
      success: true,
      data: { updated_count: 3 },
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const onSuccess = vi.fn();
    const onError = vi.fn();

    const { result } = renderHook(
      () => useBatchEdit({ onSuccess, onError }),
      {
        wrapper: ({ children }) => (
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        ),
      }
    );

    const formData: BatchEditFormData = {
      eventName: 'NewEventName',
      categoryId: 1,
    };

    act(() => {
      result.current.batchEdit({
        eventIds: [1, 2, 3],
        formData,
      });
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/events/batch', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: expect.stringContaining('NewEventName'),
    });

    expect(onSuccess).toHaveBeenCalledWith(3);
    expect(onError).not.toHaveBeenCalled();
  });

  it('should handle batch edit errors', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const onSuccess = vi.fn();
    const onError = vi.fn();

    const { result } = renderHook(
      () => useBatchEdit({ onSuccess, onError }),
      {
        wrapper: ({ children }) => (
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        ),
      }
    );

    const formData: BatchEditFormData = {
      eventName: 'NewEventName',
    };

    act(() => {
      result.current.batchEdit({
        eventIds: [1, 2, 3],
        formData,
      });
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(onSuccess).not.toHaveBeenCalled();
    expect(onError).toHaveBeenCalledWith(expect.any(Error));
  });
});

describe('useBatchDelete', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should successfully batch delete events', async () => {
    const mockResponse = {
      success: true,
      data: { deleted_count: 2 },
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const onSuccess = vi.fn();
    const onError = vi.fn();

    const { result } = renderHook(
      () => useBatchDelete({ onSuccess, onError }),
      {
        wrapper: ({ children }) => (
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        ),
      }
    );

    act(() => {
      result.current.batchDelete([1, 2]);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/events/batch', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [1, 2] }),
    });

    expect(onSuccess).toHaveBeenCalledWith(2);
    expect(onError).not.toHaveBeenCalled();
  });

  it('should handle batch delete errors', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    const onSuccess = vi.fn();
    const onError = vi.fn();

    const { result } = renderHook(
      () => useBatchDelete({ onSuccess, onError }),
      {
        wrapper: ({ children }) => (
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        ),
      }
    );

    act(() => {
      result.current.batchDelete([1, 2]);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(onSuccess).not.toHaveBeenCalled();
    expect(onError).toHaveBeenCalledWith(expect.any(Error));
  });
});

describe('useBatchValidate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should validate events with no issues', () => {
    const onComplete = vi.fn();

    const { result } = renderHook(() => useBatchValidate({ onComplete }));

    const events: Event[] = [
      {
        id: 1,
        gameGid: 100,
        eventName: 'TestEvent',
        eventNameCn: '测试事件',
        categoryId: 1,
        categoryName: '测试分类',
        sourceTable: 'test_source',
        targetTable: 'test_target',
        fields: [{ name: 'param1', alias: '参数1', dataType: 'string', baseType: 'string' }],
      },
    ];

    act(() => {
      const validationResult = result.current.validateEvents(events);
      expect(validationResult.totalEvents).toBe(1);
      expect(validationResult.validEvents).toBe(1);
      expect(validationResult.invalidEvents).toBe(0);
      expect(validationResult.issues).toHaveLength(0);
    });

    expect(onComplete).toHaveBeenCalled();
  });

  it('should detect missing event name', () => {
    const onComplete = vi.fn();

    const { result } = renderHook(() => useBatchValidate({ onComplete }));

    const events: Event[] = [
      {
        id: 1,
        gameGid: 100,
        eventName: '',
        eventNameCn: '测试事件',
        categoryId: 1,
        categoryName: '测试分类',
        sourceTable: 'test_source',
        targetTable: 'test_target',
        fields: [{ name: 'param1', alias: '参数1', dataType: 'string', baseType: 'string' }],
      },
    ];

    act(() => {
      const validationResult = result.current.validateEvents(events);
      expect(validationResult.totalEvents).toBe(1);
      expect(validationResult.validEvents).toBe(0);
      expect(validationResult.invalidEvents).toBe(1);
      expect(validationResult.issues).toHaveLength(1); // 修改：只检测英文名称缺失
      expect(validationResult.issues[0].type).toBe('MISSING_NAME');
    });

    expect(onComplete).toHaveBeenCalled();
  });

  it('should detect invalid event name format', () => {
    const onComplete = vi.fn();

    const { result } = renderHook(() => useBatchValidate({ onComplete }));

    const events: Event[] = [
      {
        id: 1,
        gameGid: 100,
        eventName: '123Invalid',
        eventNameCn: '测试事件',
        categoryId: 1,
        categoryName: '测试分类',
        sourceTable: 'test_source',
        targetTable: 'test_target',
        fields: [],
      },
    ];

    act(() => {
      const validationResult = result.current.validateEvents(events);
      expect(validationResult.issues).toHaveLength(2); // 修改：同时检测名称格式和缺少参数
      const nameFormatIssue = validationResult.issues.find(
        issue => issue.type === 'INVALID_NAME_FORMAT'
      );
      expect(nameFormatIssue).toBeDefined();
      expect(nameFormatIssue?.severity).toBe('warning');
    });
  });

  it('should detect missing category', () => {
    const onComplete = vi.fn();

    const { result } = renderHook(() => useBatchValidate({ onComplete }));

    const events: Event[] = [
      {
        id: 1,
        gameGid: 100,
        eventName: 'TestEvent',
        eventNameCn: '测试事件',
        sourceTable: 'test_source',
        targetTable: 'test_target',
        fields: [],
      },
    ];

    act(() => {
      const validationResult = result.current.validateEvents(events);
      expect(validationResult.issues).toHaveLength(2); // 修改：同时检测缺少分类和缺少参数
      const categoryIssue = validationResult.issues.find(
        issue => issue.type === 'MISSING_CATEGORY'
      );
      expect(categoryIssue).toBeDefined();
      expect(categoryIssue?.severity).toBe('warning');
    });
  });

  it('should detect missing source table', () => {
    const onComplete = vi.fn();

    const { result } = renderHook(() => useBatchValidate({ onComplete }));

    const events: Event[] = [
      {
        id: 1,
        gameGid: 100,
        eventName: 'TestEvent',
        eventNameCn: '测试事件',
        categoryId: 1,
        categoryName: '测试分类',
        sourceTable: '',
        targetTable: 'test_target',
        fields: [],
      },
    ];

    act(() => {
      const validationResult = result.current.validateEvents(events);
      expect(validationResult.issues).toHaveLength(2); // 修改：同时检测缺少源表和缺少参数
      const sourceTableIssue = validationResult.issues.find(
        issue => issue.type === 'MISSING_SOURCE_TABLE'
      );
      expect(sourceTableIssue).toBeDefined();
      expect(sourceTableIssue?.severity).toBe('error');
    });
  });

  it('should detect no parameters', () => {
    const onComplete = vi.fn();

    const { result } = renderHook(() => useBatchValidate({ onComplete }));

    const events: Event[] = [
      {
        id: 1,
        gameGid: 100,
        eventName: 'TestEvent',
        eventNameCn: '测试事件',
        categoryId: 1,
        categoryName: '测试分类',
        sourceTable: 'test_source',
        targetTable: 'test_target',
        fields: [],
      },
    ];

    act(() => {
      const validationResult = result.current.validateEvents(events);
      const noParamIssue = validationResult.issues.find(
        issue => issue.type === 'NO_PARAMETERS'
      );
      expect(noParamIssue).toBeDefined();
      expect(noParamIssue?.severity).toBe('warning');
    });
  });
});

describe('useBatchOperations', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should provide all batch operations', () => {
    const { result } = renderHook(
      () => useBatchOperations(),
      {
        wrapper: ({ children }) => (
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        ),
      }
    );

    expect(result.current.batchEdit).toBeDefined();
    expect(result.current.batchDelete).toBeDefined();
    expect(result.current.batchValidate).toBeDefined();
  });
});