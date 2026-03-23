/**
 * errorHandler 单元测试
 *
 * 测试错误分类、消息格式化和错误上报功能
 */

import { vi, describe, it, expect, beforeEach } from 'vitest';

import {
  classifyError,
  determineErrorLevel,
  formatErrorMessage,
  createAppError,
  handleError,
  configureErrorReporting,
  shouldRetry,
  getUserFriendlyMessage,
  ErrorType,
  ErrorLevel,
} from './errorHandler';

// Mock fetch
global.fetch = vi.fn();

describe('errorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // 重置错误上报配置
    configureErrorReporting({ enabled: false });
  });

  describe('错误分类', () => {
    it('应该正确分类网络错误', () => {
      const error = new TypeError('Failed to fetch');
      expect(classifyError(error)).toBe(ErrorType.NETWORK);
    });

    it('应该正确分类API错误', () => {
      const error = { status: 500, message: 'Server error' };
      expect(classifyError(error)).toBe(ErrorType.API);
    });

    it('应该正确分类业务错误', () => {
      const error = { code: 'duplicate_game_gid', message: 'Game exists' };
      expect(classifyError(error)).toBe(ErrorType.BUSINESS);
    });

    it('应该将未知错误分类为UNKNOWN', () => {
      const error = 'Some error';
      expect(classifyError(error)).toBe(ErrorType.UNKNOWN);
    });

    it('应该识别AbortError为网络错误', () => {
      const error = new DOMException('Aborted', 'AbortError');
      expect(classifyError(error)).toBe(ErrorType.NETWORK);
    });
  });

  describe('错误级别确定', () => {
    it('应该将网络错误定为WARNING级别', () => {
      const error = new TypeError('Failed to fetch');
      expect(determineErrorLevel(error, ErrorType.NETWORK)).toBe(ErrorLevel.WARNING);
    });

    it('应该将5xx错误定为FATAL级别', () => {
      const error = { status: 500 };
      expect(determineErrorLevel(error, ErrorType.API)).toBe(ErrorLevel.FATAL);
    });

    it('应该将4xx错误定为ERROR级别', () => {
      const error = { status: 404 };
      expect(determineErrorLevel(error, ErrorType.API)).toBe(ErrorLevel.ERROR);
    });

    it('应该将其他错误定为ERROR级别', () => {
      const error = new Error('Some error');
      expect(determineErrorLevel(error, ErrorType.UNKNOWN)).toBe(ErrorLevel.ERROR);
    });
  });

  describe('错误消息格式化', () => {
    it('应该格式化Error对象的错误消息', () => {
      const error = new Error('Test error');
      expect(formatErrorMessage(error)).toBe('Test error');
    });

    it('应该添加上下文前缀', () => {
      const error = new Error('Test error');
      expect(formatErrorMessage(error, '操作')).toBe('操作：Test error');
    });

    it('应该从对象中提取错误消息', () => {
      const error = { message: 'Object error' };
      expect(formatErrorMessage(error)).toBe('Object error');
    });

    it('应该处理字符串错误', () => {
      const error = 'String error';
      expect(formatErrorMessage(error)).toBe('String error');
    });

    it('应该为未知错误提供默认消息', () => {
      const error = null;
      expect(formatErrorMessage(error)).toBe('发生未知错误');
    });

    it('应该映射HTTP状态码错误消息', () => {
      const error = { status: 404 };
      expect(formatErrorMessage(error)).toBe('请求的资源不存在');
    });

    it('应该映射业务错误代码消息', () => {
      const error = { code: 'duplicate_game_gid' };
      expect(formatErrorMessage(error)).toBe('游戏GID已存在');
    });
  });

  describe('创建统一错误对象', () => {
    it('应该创建包含所有必要字段的错误对象', () => {
      const error = new Error('Test error');
      const appError = createAppError(error, '操作');

      expect(appError.type).toBeDefined();
      expect(appError.level).toBeDefined();
      expect(appError.message).toBe('操作：Test error');
      expect(appError.originalError).toBe(error);
      expect(appError.timestamp).toBeGreaterThan(0);
    });

    it('应该提取错误代码', () => {
      const error = { code: 'test_code', message: 'Test' };
      const appError = createAppError(error);

      expect(appError.code).toBe('test_code');
    });

    it('应该提取错误详情', () => {
      const error = { message: 'Test', details: { field: 'value' } };
      const appError = createAppError(error);

      expect(appError.details).toEqual({ field: 'value' });
    });
  });

  describe('错误处理', () => {
    it('应该记录错误到控制台', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const error = new Error('Test error');

      await handleError(error, { report: false });

      expect(consoleErrorSpy).toHaveBeenCalled();
      consoleErrorSpy.mockRestore();
    });

    it('应该调用自定义处理函数', async () => {
      const handler = vi.fn();
      const error = new Error('Test error');

      await handleError(error, {
        report: false,
        handler,
      });

      expect(handler).toHaveBeenCalled();
      expect(handler.mock.calls[0][0]).toHaveProperty('type');
      expect(handler.mock.calls[0][0]).toHaveProperty('message');
    });
  });

  describe('错误上报', () => {
    it('应该在启用时上报错误', async () => {
      configureErrorReporting({
        enabled: true,
        reportUrl: 'https://example.com/api/errors',
      });

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
      });

      const error = new Error('Test error');
      await handleError(error, { report: true });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://example.com/api/errors',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    });

    it('应该在beforeSend返回null时取消上报', async () => {
      configureErrorReporting({
        enabled: true,
        reportUrl: 'https://example.com/api/errors',
        beforeSend: () => null,
      });

      const error = new Error('Test error');
      await handleError(error, { report: true });

      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('应该调用afterSend回调', async () => {
      const afterSend = vi.fn();
      configureErrorReporting({
        enabled: true,
        reportUrl: 'https://example.com/api/errors',
        afterSend,
      });

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: true,
      });

      const error = new Error('Test error');
      await handleError(error, { report: true });

      expect(afterSend).toHaveBeenCalled();
      expect(afterSend.mock.calls[0][1]).toBe(true);
    });
  });

  describe('重试判断', () => {
    it('应该允许重试网络错误', () => {
      const appError = createAppError(new TypeError('Failed to fetch'));
      expect(shouldRetry(appError)).toBe(true);
    });

    it('应该允许重试5xx错误', () => {
      const appError = createAppError({ status: 500 });
      expect(shouldRetry(appError)).toBe(true);
    });

    it('不应该重试4xx错误', () => {
      const appError = createAppError({ status: 404 });
      expect(shouldRetry(appError)).toBe(false);
    });

    it('不应该重试业务错误', () => {
      const appError = createAppError({ code: 'duplicate_game_gid' });
      expect(shouldRetry(appError)).toBe(false);
    });
  });

  describe('用户友好消息', () => {
    it('应该为网络错误提供友好消息', () => {
      const appError = createAppError(new TypeError('Failed to fetch'));
      expect(getUserFriendlyMessage(appError)).toBe('网络连接失败，请检查网络设置后重试');
    });

    it('应该为FATAL级别API错误提供友好消息', () => {
      const appError = createAppError({ status: 500 });
      expect(getUserFriendlyMessage(appError)).toBe('服务暂时不可用，请稍后重试');
    });

    it('应该为业务错误返回原始消息', () => {
      const appError = createAppError({ code: 'duplicate_game_gid' });
      expect(getUserFriendlyMessage(appError)).toBe('游戏GID已存在');
    });

    it('应该为未知错误提供默认消息', () => {
      const appError = createAppError('unknown');
      expect(getUserFriendlyMessage(appError)).toBe('操作失败，请稍后重试');
    });
  });

  describe('便捷方法', () => {
    it('应该处理网络错误', async () => {
      const error = new TypeError('Failed to fetch');
      const result = await handleNetworkError(error, '网络请求');

      expect(result.type).toBe(ErrorType.NETWORK);
      expect(result.message).toContain('网络请求');
    });

    it('应该处理API错误', async () => {
      const error = { status: 500 };
      const result = await handleApiError(error, 'API调用');

      expect(result.type).toBe(ErrorType.API);
      expect(result.message).toContain('API调用');
    });

    it('应该处理业务错误', async () => {
      const error = { code: 'duplicate_game_gid' };
      const result = await handleBusinessError(error, '业务操作');

      expect(result.type).toBe(ErrorType.BUSINESS);
      expect(result.message).toContain('业务操作');
    });
  });
});
