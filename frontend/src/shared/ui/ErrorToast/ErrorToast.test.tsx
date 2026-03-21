/**
 * ErrorToast 组件单元测试
 *
 * 测试错误提示组件的渲染、交互和自动消失功能
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ErrorToast, { useErrorToast, ErrorLevel } from './ErrorToast';

// Mock timers
jest.useFakeTimers();

describe('ErrorToast Component', () => {
  beforeEach(() => {
    jest.clearAllTimers();
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('基本渲染', () => {
    it('应该不渲染任何内容当没有错误时', () => {
      const { container } = render(
        <ErrorToast
          toasts={[]}
          onRemove={() => {}}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('应该渲染错误提示', () => {
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Test error',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
        />
      );

      expect(screen.getByText('Test error')).toBeInTheDocument();
    });

    it('应该渲染多个错误提示', () => {
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Error 1',
          duration: 5000,
          timestamp: Date.now(),
        },
        {
          id: '2',
          level: 'warning' as ErrorLevel,
          message: 'Warning 1',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
        />
      );

      expect(screen.getByText('Error 1')).toBeInTheDocument();
      expect(screen.getByText('Warning 1')).toBeInTheDocument();
    });

    it('应该限制最大显示数量', () => {
      const toasts = Array.from({ length: 10 }, (_, i) => ({
        id: String(i),
        level: 'error' as ErrorLevel,
        message: `Error ${i}`,
        duration: 5000,
        timestamp: Date.now(),
      }));

      const { container } = render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
          maxToasts={3}
        />
      );

      // 应该只显示最后3个
      const toastElements = container.querySelectorAll('[role="alert"]');
      expect(toastElements.length).toBe(3);
    });
  });

  describe('错误级别样式', () => {
    it('应该为error级别应用正确的样式', () => {
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Error message',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      const { container } = render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
        />
      );

      const toastElement = container.firstChild as HTMLElement;
      expect(toastElement).toHaveStyle({
        backgroundColor: '#fee2e2',
        borderLeft: '4px solid #dc2626',
      });
    });

    it('应该为warning级别应用正确的样式', () => {
      const toasts = [
        {
          id: '1',
          level: 'warning' as ErrorLevel,
          message: 'Warning message',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      const { container } = render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
        />
      );

      const toastElement = container.firstChild as HTMLElement;
      expect(toastElement).toHaveStyle({
        backgroundColor: '#fef3c7',
        borderLeft: '4px solid #f59e0b',
      });
    });

    it('应该为info级别应用正确的样式', () => {
      const toasts = [
        {
          id: '1',
          level: 'info' as ErrorLevel,
          message: 'Info message',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      const { container } = render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
        />
      );

      const toastElement = container.firstChild as HTMLElement;
      expect(toastElement).toHaveStyle({
        backgroundColor: '#dbeafe',
        borderLeft: '4px solid #3b82f6',
      });
    });
  });

  describe('交互功能', () => {
    it('应该在点击关闭按钮时移除错误', () => {
      const onRemove = jest.fn();
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Test error',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      render(
        <ErrorToast
          toasts={toasts}
          onRemove={onRemove}
        />
      );

      const closeButton = screen.getByRole('button', { name: /关闭/i });
      fireEvent.click(closeButton);

      expect(onRemove).toHaveBeenCalledWith('1');
    });

    it('应该在自动消失时调用onRemove', async () => {
      const onRemove = jest.fn();
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Test error',
          duration: 1000,
          timestamp: Date.now(),
        },
      ];

      render(
        <ErrorToast
          toasts={toasts}
          onRemove={onRemove}
        />
      );

      // 快进时间
      jest.advanceTimersByTime(1000);
      jest.advanceTimersByTime(300); // 等待退出动画

      await waitFor(() => {
        expect(onRemove).toHaveBeenCalledWith('1');
      });
    });

    it('应该不自动移除duration为0的错误', () => {
      const onRemove = jest.fn();
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Test error',
          duration: 0,
          timestamp: Date.now(),
        },
      ];

      render(
        <ErrorToast
          toasts={toasts}
          onRemove={onRemove}
        />
      );

      // 快进时间
      jest.advanceTimersByTime(5000);

      expect(onRemove).not.toHaveBeenCalled();
    });
  });

  describe('位置配置', () => {
    it('应该支持top-right位置', () => {
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Test error',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      const { container } = render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
          position="top-right"
        />
      );

      const toastContainer = container.firstChild as HTMLElement;
      expect(toastContainer).toHaveStyle({
        top: '20px',
        right: '20px',
      });
    });

    it('应该支持bottom-left位置', () => {
      const toasts = [
        {
          id: '1',
          level: 'error' as ErrorLevel,
          message: 'Test error',
          duration: 5000,
          timestamp: Date.now(),
        },
      ];

      const { container } = render(
        <ErrorToast
          toasts={toasts}
          onRemove={() => {}}
          position="bottom-left"
        />
      );

      const toastContainer = container.firstChild as HTMLElement;
      expect(toastContainer).toHaveStyle({
        bottom: '20px',
        left: '20px',
      });
    });
  });
});

describe('useErrorToast Hook', () => {
  beforeEach(() => {
    jest.clearAllTimers();
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('应该提供showError方法', () => {
    const { result } = renderHook(() => useErrorToast());

    expect(result.current.showError).toBeDefined();
    expect(typeof result.current.showError).toBe('function');
  });

  it('应该提供showWarning方法', () => {
    const { result } = renderHook(() => useErrorToast());

    expect(result.current.showWarning).toBeDefined();
    expect(typeof result.current.showWarning).toBe('function');
  });

  it('应该提供showInfo方法', () => {
    const { result } = renderHook(() => useErrorToast());

    expect(result.current.showInfo).toBeDefined();
    expect(typeof result.current.showInfo).toBe('function');
  });

  it('应该添加错误提示', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showError('Test error');
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].message).toBe('Test error');
    expect(result.current.toasts[0].level).toBe('error');
  });

  it('应该添加警告提示', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showWarning('Test warning');
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].message).toBe('Test warning');
    expect(result.current.toasts[0].level).toBe('warning');
  });

  it('应该添加信息提示', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showInfo('Test info');
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].message).toBe('Test info');
    expect(result.current.toasts[0].level).toBe('info');
  });

  it('应该支持自定义显示时长', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showError('Test error', 10000);
    });

    expect(result.current.toasts[0].duration).toBe(10000);
  });

  it('应该移除指定的错误提示', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showError('Error 1');
      result.current.showError('Error 2');
    });

    expect(result.current.toasts).toHaveLength(2);

    act(() => {
      result.current.removeToast(result.current.toasts[0].id);
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].message).toBe('Error 2');
  });

  it('应该清空所有错误提示', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showError('Error 1');
      result.current.showError('Error 2');
      result.current.showError('Error 3');
    });

    expect(result.current.toasts).toHaveLength(3);

    act(() => {
      result.current.clearToasts();
    });

    expect(result.current.toasts).toHaveLength(0);
  });

  it('应该自动移除过期的错误提示', () => {
    const { result } = renderHook(() => useErrorToast());

    act(() => {
      result.current.showError('Error 1', 1000);
    });

    expect(result.current.toasts).toHaveLength(1);

    // 快进时间
    jest.advanceTimersByTime(1000);
    jest.advanceTimersByTime(300); // 等待退出动画

    expect(result.current.toasts).toHaveLength(0);
  });
});
