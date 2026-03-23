/**
 * useToggleField hook tests
 * 测试切换字段通用 Hook
 */

import { renderHook, act } from '@test/test-utils';
import { describe, it, expect, vi } from 'vitest';

import { useCheckboxField, useRadioField, useSwitchField } from './useToggleField';

describe('useToggleField hooks', () => {
  describe('useCheckboxField', () => {
    it('应该生成唯一的 fieldId', () => {
      const { result } = renderHook(() => useCheckboxField());
      expect(result.current.fieldId).toBeDefined();
      expect(typeof result.current.fieldId).toBe('string');
    });

    it('应该使用自定义 ID', () => {
      const customId = 'custom-checkbox-id';
      const { result } = renderHook(() => useCheckboxField({ customId }));
      expect(result.current.fieldId).toBe(customId);
    });

    it('应该在有错误时设置 isInvalid 为 true', () => {
      const { result } = renderHook(() => useCheckboxField({ error: 'Error' }));
      expect(result.current.isInvalid).toBe(true);
    });

    it('应该在未禁用时调用 onCheckboxChange', () => {
      const onCheckboxChange = vi.fn();
      const { result } = renderHook(() => useCheckboxField({
        onCheckboxChange,
        disabled: false
      }));

      const mockEvent = {
        target: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleCheckboxChange(mockEvent);
      });

      expect(onCheckboxChange).toHaveBeenCalledTimes(1);
      expect(onCheckboxChange).toHaveBeenCalledWith(true, mockEvent);
    });

    it('应该在禁用时不调用 onCheckboxChange', () => {
      const onCheckboxChange = vi.fn();
      const { result } = renderHook(() => useCheckboxField({
        onCheckboxChange,
        disabled: true
      }));

      const mockEvent = {
        target: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleCheckboxChange(mockEvent);
      });

      expect(onCheckboxChange).not.toHaveBeenCalled();
    });

    it('应该在 onCheckboxChange 为 undefined 时不报错', () => {
      const { result } = renderHook(() => useCheckboxField({ disabled: false }));

      const mockEvent = {
        target: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      expect(() => {
        act(() => {
          result.current.handleCheckboxChange(mockEvent);
        });
      }).not.toThrow();
    });

    it('应该提供 handleChange 作为 handleCheckboxChange 的别名', () => {
      const onCheckboxChange = vi.fn();
      const { result } = renderHook(() => useCheckboxField({
        onCheckboxChange,
        disabled: false
      }));

      const mockEvent = {
        target: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleChange(mockEvent);
      });

      expect(onCheckboxChange).toHaveBeenCalledTimes(1);
    });
  });

  describe('useRadioField', () => {
    it('应该生成唯一的 fieldId', () => {
      const { result } = renderHook(() => useRadioField());
      expect(result.current.fieldId).toBeDefined();
      expect(typeof result.current.fieldId).toBe('string');
    });

    it('应该使用自定义 ID', () => {
      const customId = 'custom-radio-id';
      const { result } = renderHook(() => useRadioField({ customId }));
      expect(result.current.fieldId).toBe(customId);
    });

    it('应该在有错误时设置 isInvalid 为 true', () => {
      const { result } = renderHook(() => useRadioField({ error: 'Error' }));
      expect(result.current.isInvalid).toBe(true);
    });

    it('应该在未禁用时调用 onRadioChange', () => {
      const onRadioChange = vi.fn();
      const { result } = renderHook(() => useRadioField({
        onRadioChange,
        disabled: false
      }));

      const mockEvent = {
        target: { value: 'option1' }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleRadioChange(mockEvent);
      });

      expect(onRadioChange).toHaveBeenCalledTimes(1);
      expect(onRadioChange).toHaveBeenCalledWith('option1', mockEvent);
    });

    it('应该在禁用时不调用 onRadioChange', () => {
      const onRadioChange = vi.fn();
      const { result } = renderHook(() => useRadioField({
        onRadioChange,
        disabled: true
      }));

      const mockEvent = {
        target: { value: 'option1' }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleRadioChange(mockEvent);
      });

      expect(onRadioChange).not.toHaveBeenCalled();
    });

    it('应该在 onRadioChange 为 undefined 时不报错', () => {
      const { result } = renderHook(() => useRadioField({ disabled: false }));

      const mockEvent = {
        target: { value: 'option1' }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      expect(() => {
        act(() => {
          result.current.handleRadioChange(mockEvent);
        });
      }).not.toThrow();
    });

    it('应该提供 handleChange 作为 handleRadioChange 的别名', () => {
      const onRadioChange = vi.fn();
      const { result } = renderHook(() => useRadioField({
        onRadioChange,
        disabled: false
      }));

      const mockEvent = {
        target: { value: 'option1' }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleChange(mockEvent);
      });

      expect(onRadioChange).toHaveBeenCalledTimes(1);
    });
  });

  describe('useSwitchField', () => {
    it('应该生成唯一的 fieldId', () => {
      const { result } = renderHook(() => useSwitchField());
      expect(result.current.fieldId).toBeDefined();
      expect(typeof result.current.fieldId).toBe('string');
    });

    it('应该使用自定义 ID', () => {
      const customId = 'custom-switch-id';
      const { result } = renderHook(() => useSwitchField({ customId }));
      expect(result.current.fieldId).toBe(customId);
    });

    it('应该在有错误时设置 isInvalid 为 true', () => {
      const { result } = renderHook(() => useSwitchField({ error: 'Error' }));
      expect(result.current.isInvalid).toBe(true);
    });

    it('应该在未禁用时调用 onSwitchChange', () => {
      const onSwitchChange = vi.fn();
      const { result } = renderHook(() => useSwitchField({
        onSwitchChange,
        disabled: false,
        checked: false
      }));

      const mockEvent = {
        target: { checked: true },
        currentTarget: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleSwitchChange(mockEvent);
      });

      expect(onSwitchChange).toHaveBeenCalledTimes(1);
      expect(onSwitchChange).toHaveBeenCalledWith(true, mockEvent);
    });

    it('应该在禁用时不调用 onSwitchChange', () => {
      const onSwitchChange = vi.fn();
      const { result } = renderHook(() => useSwitchField({
        onSwitchChange,
        disabled: true,
        checked: false
      }));

      const mockEvent = {
        target: { checked: true },
        currentTarget: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleSwitchChange(mockEvent);
      });

      expect(onSwitchChange).not.toHaveBeenCalled();
    });

    it('应该在按下 Enter 键时切换状态', () => {
      const onSwitchChange = vi.fn();
      const { result } = renderHook(() => useSwitchField({
        onSwitchChange,
        disabled: false,
        checked: false
      }));

      const mockEvent = {
        key: 'Enter',
        target: { checked: false },
        currentTarget: { checked: false },
        preventDefault: vi.fn()
      } as unknown as React.KeyboardEvent<HTMLInputElement>;

      act(() => {
        result.current.handleKeyDown(mockEvent);
      });

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(onSwitchChange).toHaveBeenCalledTimes(1);
      expect(onSwitchChange).toHaveBeenCalledWith(true, expect.any(Object));
    });

    it('应该在按下非 Enter 键时不切换状态', () => {
      const onSwitchChange = vi.fn();
      const { result } = renderHook(() => useSwitchField({
        onSwitchChange,
        disabled: false,
        checked: false
      }));

      const mockEvent = {
        key: 'Space',
        target: { checked: false },
        currentTarget: { checked: false },
        preventDefault: vi.fn()
      } as unknown as React.KeyboardEvent<HTMLInputElement>;

      act(() => {
        result.current.handleKeyDown(mockEvent);
      });

      expect(mockEvent.preventDefault).not.toHaveBeenCalled();
      expect(onSwitchChange).not.toHaveBeenCalled();
    });

    it('应该在禁用时按下 Enter 键不切换状态', () => {
      const onSwitchChange = vi.fn();
      const { result } = renderHook(() => useSwitchField({
        onSwitchChange,
        disabled: true,
        checked: false
      }));

      const mockEvent = {
        key: 'Enter',
        target: { checked: false },
        currentTarget: { checked: false },
        preventDefault: vi.fn()
      } as unknown as React.KeyboardEvent<HTMLInputElement>;

      act(() => {
        result.current.handleKeyDown(mockEvent);
      });

      expect(mockEvent.preventDefault).not.toHaveBeenCalled();
      expect(onSwitchChange).not.toHaveBeenCalled();
    });

    it('应该在 onSwitchChange 为 undefined 时不报错', () => {
      const { result } = renderHook(() => useSwitchField({ disabled: false, checked: false }));

      const mockEvent = {
        target: { checked: true },
        currentTarget: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      expect(() => {
        act(() => {
          result.current.handleSwitchChange(mockEvent);
        });
      }).not.toThrow();
    });

    it('应该提供 handleChange 作为 handleSwitchChange 的别名', () => {
      const onSwitchChange = vi.fn();
      const { result } = renderHook(() => useSwitchField({
        onSwitchChange,
        disabled: false,
        checked: false
      }));

      const mockEvent = {
        target: { checked: true },
        currentTarget: { checked: true }
      } as unknown as React.ChangeEvent<HTMLInputElement>;

      act(() => {
        result.current.handleChange(mockEvent);
      });

      expect(onSwitchChange).toHaveBeenCalledTimes(1);
    });
  });

  describe('边界情况', () => {
    it('应该在所有选项为空时正常工作', () => {
      const { result: checkboxResult } = renderHook(() => useCheckboxField({}));
      const { result: radioResult } = renderHook(() => useRadioField({}));
      const { result: switchResult } = renderHook(() => useSwitchField({}));

      expect(checkboxResult.current.fieldId).toBeDefined();
      expect(radioResult.current.fieldId).toBeDefined();
      expect(switchResult.current.fieldId).toBeDefined();
    });

    it('应该在多次调用时保持稳定性', () => {
      const { result, rerender } = renderHook(() => useCheckboxField({ error: 'test' }));

      const firstFieldId = result.current.fieldId;
      const firstMergedRef = result.current.mergedRef;

      rerender();

      expect(result.current.fieldId).toBe(firstFieldId);
      expect(result.current.mergedRef).toBe(firstMergedRef);
    });
  });
});
