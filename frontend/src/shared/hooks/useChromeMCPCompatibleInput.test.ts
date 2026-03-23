import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@test/test-utils';
import { useChromeMCPCompatibleInput } from './useChromeMCPCompatibleInput';

describe('useChromeMCPCompatibleInput', () => {
  // Cleanup after each test to prevent state leakage
  afterEach(() => {
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  describe('initial state', () => {
    it('should initialize with empty values', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string; email: string }>()
      );
      
      expect(result.current.values).toEqual({});
    });

    it('should initialize with provided values', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput({
          initialValues: { name: 'John', email: 'john@example.com' },
        })
      );
      
      expect(result.current.values).toEqual({
        name: 'John',
        email: 'john@example.com',
      });
    });
  });

  describe('handleChange', () => {
    it('should update field value', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>({
          initialValues: { name: '' },
        })
      );
      
      act(() => {
        result.current.handleChange('name', 'John');
      });
      
      expect(result.current.values.name).toBe('John');
    });

    it('should update multiple fields', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string; email: string }>({
          initialValues: { name: '', email: '' },
        })
      );
      
      act(() => {
        result.current.handleChange('name', 'John');
        result.current.handleChange('email', 'john@example.com');
      });
      
      expect(result.current.values).toEqual({
        name: 'John',
        email: 'john@example.com',
      });
    });
  });

  describe('register', () => {
    it('should register field and return ref', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>()
      );
      
      const ref = result.current.register('name');
      
      expect(ref).toBeDefined();
      expect(ref.current).toBeNull();
    });

    it('should return same ref for same field', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>()
      );
      
      const ref1 = result.current.register('name');
      const ref2 = result.current.register('name');
      
      expect(ref1).toBe(ref2);
    });
  });

  describe('resetValues', () => {
    it('should reset to initial values', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>({
          initialValues: { name: 'John' },
        })
      );
      
      act(() => {
        result.current.handleChange('name', 'Jane');
        result.current.resetValues();
      });
      
      expect(result.current.values.name).toBe('John');
    });

    it('should reset to new values', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>({
          initialValues: { name: 'John' },
        })
      );
      
      act(() => {
        result.current.resetValues({ name: 'Bob' });
      });
      
      expect(result.current.values.name).toBe('Bob');
    });
  });

  describe('getDomValue', () => {
    it('should return empty string for unregistered field', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>()
      );
      
      const value = result.current.getDomValue('name');
      expect(value).toBe('');
    });

    it('should return current DOM value', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>()
      );
      
      const ref = result.current.register('name');
      
      const mockElement = { value: 'test value' } as HTMLInputElement;
      ref.current = mockElement;
      
      const value = result.current.getDomValue('name');
      expect(value).toBe('test value');
    });
  });

  describe('syncFromDom', () => {
    it('should sync DOM values to state', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string; email: string }>({
          initialValues: { name: '', email: '' },
        })
      );
      
      const nameRef = result.current.register('name');
      const emailRef = result.current.register('email');
      
      const mockNameElement = { value: 'John' } as HTMLInputElement;
      const mockEmailElement = { value: 'john@example.com' } as HTMLInputElement;
      
      nameRef.current = mockNameElement;
      emailRef.current = mockEmailElement;
      
      act(() => {
        result.current.syncFromDom();
      });
      
      expect(result.current.values.name).toBe('John');
      expect(result.current.values.email).toBe('john@example.com');
    });

    it('should only sync changed values', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string; email: string }>({
          initialValues: { name: 'John', email: '' },
        })
      );
      
      const nameRef = result.current.register('name');
      const emailRef = result.current.register('email');
      
      const mockEmailElement = { value: 'john@example.com' } as HTMLInputElement;
      
      nameRef.current = { value: 'John' } as HTMLInputElement;
      emailRef.current = mockEmailElement;
      
      act(() => {
        result.current.syncFromDom();
      });
      
      expect(result.current.values.name).toBe('John');
      expect(result.current.values.email).toBe('john@example.com');
    });
  });

  describe('onValuesChange callback', () => {
    it('should call callback when values change', () => {
      const callback = vi.fn();
      
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>({
          initialValues: { name: '' },
          onValuesChange: callback,
        })
      );
      
      act(() => {
        result.current.handleChange('name', 'John');
      });
      
      expect(callback).toHaveBeenCalledWith({ name: 'John' });
    });

    it('should call callback on DOM sync', () => {
      const callback = vi.fn();
      
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>({
          initialValues: { name: '' },
          onValuesChange: callback,
        })
      );
      
      const ref = result.current.register('name');
      ref.current = { value: 'John' } as HTMLInputElement;
      
      act(() => {
        result.current.syncFromDom();
      });
      
      expect(callback).toHaveBeenCalledWith({ name: 'John' });
    });
  });

  describe('enableDomSync option', () => {
    it('should not sync DOM when disabled', () => {
      const { result } = renderHook(() =>
        useChromeMCPCompatibleInput<{ name: string }>({
          initialValues: { name: '' },
          enableDomSync: false,
        })
      );
      
      const ref = result.current.register('name');
      ref.current = { value: 'John' } as HTMLInputElement;
      
      act(() => {
        result.current.syncFromDom();
      });
      
      expect(result.current.values.name).toBe('');
    });
  });
});
