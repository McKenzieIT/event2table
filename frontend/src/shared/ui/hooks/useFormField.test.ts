/**
 * useFormField hook tests
 * 测试表单字段通用 Hook
 */

import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useFormField } from './useFormField';

describe('useFormField hook', () => {
  describe('基础功能', () => {
    it('应该生成唯一的 fieldId', () => {
      const { result } = renderHook(() => useFormField());
      expect(result.current.fieldId).toBeDefined();
      expect(typeof result.current.fieldId).toBe('string');
    });

    it('应该使用自定义 ID', () => {
      const customId = 'custom-field-id';
      const { result } = renderHook(() => useFormField({ customId }));
      expect(result.current.fieldId).toBe(customId);
    });

    it('应该创建 fieldRef', () => {
      const { result } = renderHook(() => useFormField());
      expect(result.current.fieldRef).toBeDefined();
      expect(result.current.fieldRef.current).toBeNull();
    });

    it('应该提供 mergedRef 函数', () => {
      const { result } = renderHook(() => useFormField());
      expect(result.current.mergedRef).toBeDefined();
      expect(typeof result.current.mergedRef).toBe('function');
    });
  });

  describe('错误状态', () => {
    it('应该在有错误时设置 isInvalid 为 true', () => {
      const { result } = renderHook(() => useFormField({ error: 'This field is required' }));
      expect(result.current.isInvalid).toBe(true);
    });

    it('应该在无错误时设置 isInvalid 为 false', () => {
      const { result } = renderHook(() => useFormField({ error: undefined }));
      expect(result.current.isInvalid).toBe(false);
    });

    it('应该在错误为空字符串时设置 isInvalid 为 false', () => {
      const { result } = renderHook(() => useFormField({ error: '' }));
      expect(result.current.isInvalid).toBe(false);
    });

    it('应该在错误为 null 时设置 isInvalid 为 false', () => {
      const { result } = renderHook(() => useFormField({ error: null }));
      expect(result.current.isInvalid).toBe(false);
    });
  });

  describe('事件处理器', () => {
    it('应该调用 onChange 处理器', () => {
      const onChange = vi.fn();
      const { result } = renderHook(() => useFormField({ onChange }));

      const mockEvent = {
        target: { value: 'test' }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleChange(mockEvent);
      });

      expect(onChange).toHaveBeenCalledTimes(1);
      expect(onChange).toHaveBeenCalledWith(mockEvent);
    });

    it('应该在 onChange 为 undefined 时不报错', () => {
      const { result } = renderHook(() => useFormField({ onChange: undefined }));

      const mockEvent = {
        target: { value: 'test' }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      expect(() => {
        act(() => {
          result.current.handleChange(mockEvent);
        });
      }).not.toThrow();
    });

    it('应该调用 onBlur 处理器', () => {
      const onBlur = vi.fn();
      const { result } = renderHook(() => useFormField({ onBlur }));

      const mockEvent = {
        target: { value: 'test' }
      } as unknown as React.FocusEvent<HTMLInputElement>;

      act(() => {
        result.current.handleBlur(mockEvent);
      });

      expect(onBlur).toHaveBeenCalledTimes(1);
      expect(onBlur).toHaveBeenCalledWith(mockEvent);
    });

    it('应该在 onBlur 为 undefined 时不报错', () => {
      const { result } = renderHook(() => useFormField({ onBlur: undefined }));

      const mockEvent = {
        target: { value: 'test' }
      } as unknown as React.FocusEvent<HTMLInputElement>;

      expect(() => {
        act(() => {
          result.current.handleBlur(mockEvent);
        });
      }).not.toThrow();
    });

    it('应该调用 onFocus 处理器', () => {
      const onFocus = vi.fn();
      const { result } = renderHook(() => useFormField({ onFocus }));

      const mockEvent = {
        target: { value: 'test' }
      } as unknown as React.FocusEvent<HTMLInputElement>;

      act(() => {
        result.current.handleFocus(mockEvent);
      });

      expect(onFocus).toHaveBeenCalledTimes(1);
      expect(onFocus).toHaveBeenCalledWith(mockEvent);
    });

    it('应该在 onFocus 为 undefined 时不报错', () => {
      const { result } = renderHook(() => useFormField({ onFocus: undefined }));

      const mockEvent = {
        target: { value: 'test' }
      } as unknown as React.FocusEvent<HTMLInputElement>;

      expect(() => {
        act(() => {
          result.current.handleFocus(mockEvent);
        });
      }).not.toThrow();
    });
  });

  describe('ref 合并', () => {
    it('应该合并函数 ref', () => {
      const externalRef = vi.fn();
      const { result } = renderHook(() => useFormField({ ref: externalRef }));

      const mockNode = document.createElement('input');

      act(() => {
        result.current.mergedRef(mockNode);
      });

      expect(externalRef).toHaveBeenCalledWith(mockNode);
      expect(result.current.fieldRef.current).toBe(mockNode);
    });

    it('应该合并对象 ref', () => {
      const externalRef = { current: null };
      const { result } = renderHook(() => useFormField({ ref: externalRef }));

      const mockNode = document.createElement('input');

      act(() => {
        result.current.mergedRef(mockNode);
      });

      expect(externalRef.current).toBe(mockNode);
      expect(result.current.fieldRef.current).toBe(mockNode);
    });

    it('应该在 ref 为 undefined 时正常工作', () => {
      const { result } = renderHook(() => useFormField({ ref: undefined }));

      const mockNode = document.createElement('input');

      expect(() => {
        act(() => {
          result.current.mergedRef(mockNode);
        });
      }).not.toThrow();

      expect(result.current.fieldRef.current).toBe(mockNode);
    });

    it('应该处理 null 节点', () => {
      const externalRef = vi.fn();
      const { result } = renderHook(() => useFormField({ ref: externalRef }));

      act(() => {
        result.current.mergedRef(null);
      });

      expect(externalRef).toHaveBeenCalledWith(null);
    });
  });

  describe('边界情况', () => {
    it('应该在所有选项为空时正常工作', () => {
      const { result } = renderHook(() => useFormField({}));

      expect(result.current.fieldId).toBeDefined();
      expect(result.current.isInvalid).toBe(false);
      expect(result.current.mergedRef).toBeDefined();
    });

    it('应该在多次调用时保持稳定性', () => {
      const { result, rerender } = renderHook(() => useFormField({ error: 'test' }));

      const firstFieldId = result.current.fieldId;
      const firstMergedRef = result.current.mergedRef;

      rerender();

      expect(result.current.fieldId).toBe(firstFieldId);
      expect(result.current.mergedRef).toBe(firstMergedRef);
    });
  });
});
