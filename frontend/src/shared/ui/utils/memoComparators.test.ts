/**
 * memoComparators utility tests
 * 测试 React.memo 比较函数
 */

import { describe, it, expect } from 'vitest';

import {
  compareBaseProps,
  compareValueAndHandlers,
  compareToggleProps,
  compareCheckboxProps,
  compareInputProps,
  compareTextAreaProps,
  compareButtonProps,
  compareBadgeProps,
  compareSpinnerProps,
  compareSearchInputProps
} from './memoComparators';

describe('memoComparators utilities', () => {
  describe('compareBaseProps', () => {
    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { className: 'test', disabled: false, error: null };
      const nextProps = { className: 'test', disabled: false, error: null };
      expect(compareBaseProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 className 不同时返回 false', () => {
      const prevProps = { className: 'test', disabled: false, error: null };
      const nextProps = { className: 'different', disabled: false, error: null };
      expect(compareBaseProps(prevProps, nextProps)).toBe(false);
    });

    it('应该在 disabled 不同时返回 false', () => {
      const prevProps = { className: 'test', disabled: false, error: null };
      const nextProps = { className: 'test', disabled: true, error: null };
      expect(compareBaseProps(prevProps, nextProps)).toBe(false);
    });

    it('应该在 error 不同时返回 false', () => {
      const prevProps = { className: 'test', disabled: false, error: null };
      const nextProps = { className: 'test', disabled: false, error: 'Error' };
      expect(compareBaseProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareValueAndHandlers', () => {
    const onChange = () => {};
    const onBlur = () => {};
    const onFocus = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { value: 'test', onChange, onBlur, onFocus };
      const nextProps = { value: 'test', onChange, onBlur, onFocus };
      expect(compareValueAndHandlers(prevProps, nextProps)).toBe(true);
    });

    it('应该在 value 不同时返回 false', () => {
      const prevProps = { value: 'test', onChange, onBlur, onFocus };
      const nextProps = { value: 'different', onChange, onBlur, onFocus };
      expect(compareValueAndHandlers(prevProps, nextProps)).toBe(false);
    });

    it('应该在 onChange 不同时返回 false', () => {
      const prevProps = { value: 'test', onChange, onBlur, onFocus };
      const nextProps = { value: 'test', onChange: () => {}, onBlur, onFocus };
      expect(compareValueAndHandlers(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareToggleProps', () => {
    const onChange = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { checked: true, disabled: false, error: null, onChange };
      const nextProps = { checked: true, disabled: false, error: null, onChange };
      expect(compareToggleProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 checked 不同时返回 false', () => {
      const prevProps = { checked: true, disabled: false, error: null, onChange };
      const nextProps = { checked: false, disabled: false, error: null, onChange };
      expect(compareToggleProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareCheckboxProps', () => {
    const onChange = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { checked: true, indeterminate: false, disabled: false, error: null, onChange };
      const nextProps = { checked: true, indeterminate: false, disabled: false, error: null, onChange };
      expect(compareCheckboxProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 indeterminate 不同时返回 false', () => {
      const prevProps = { checked: true, indeterminate: false, disabled: false, error: null, onChange };
      const nextProps = { checked: true, indeterminate: true, disabled: false, error: null, onChange };
      expect(compareCheckboxProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareInputProps', () => {
    const onChange = () => {};
    const onBlur = () => {};
    const onFocus = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = {
        type: 'text',
        label: 'Test',
        placeholder: 'Enter text',
        error: null,
        disabled: false,
        required: false,
        helperText: '',
        className: '',
        value: '',
        onChange,
        onBlur,
        onFocus,
        readOnly: false,
        autoFocus: false,
        name: 'test',
        maxLength: 100,
        minLength: 0
      };
      const nextProps = { ...prevProps };
      expect(compareInputProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 type 不同时返回 false', () => {
      const prevProps = {
        type: 'text',
        label: 'Test',
        placeholder: 'Enter text',
        error: null,
        disabled: false,
        required: false,
        helperText: '',
        className: '',
        value: '',
        onChange,
        onBlur,
        onFocus,
        readOnly: false,
        autoFocus: false,
        name: 'test',
        maxLength: 100,
        minLength: 0
      };
      const nextProps = { ...prevProps, type: 'password' };
      expect(compareInputProps(prevProps, nextProps)).toBe(false);
    });

    it('应该在 label 不同时返回 false', () => {
      const prevProps = {
        type: 'text',
        label: 'Test',
        placeholder: 'Enter text',
        error: null,
        disabled: false,
        required: false,
        helperText: '',
        className: '',
        value: '',
        onChange,
        onBlur,
        onFocus,
        readOnly: false,
        autoFocus: false,
        name: 'test',
        maxLength: 100,
        minLength: 0
      };
      const nextProps = { ...prevProps, label: 'Different' };
      expect(compareInputProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareTextAreaProps', () => {
    const onChange = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { value: 'test', error: null, disabled: false, onChange };
      const nextProps = { value: 'test', error: null, disabled: false, onChange };
      expect(compareTextAreaProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 value 不同时返回 false', () => {
      const prevProps = { value: 'test', error: null, disabled: false, onChange };
      const nextProps = { value: 'different', error: null, disabled: false, onChange };
      expect(compareTextAreaProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareButtonProps', () => {
    const onClick = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { variant: 'primary', size: 'medium', disabled: false, loading: false, className: '', children: 'Click', onClick };
      const nextProps = { variant: 'primary', size: 'medium', disabled: false, loading: false, className: '', children: 'Click', onClick };
      expect(compareButtonProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 children 不同时返回 false', () => {
      const prevProps = { variant: 'primary', size: 'medium', disabled: false, loading: false, className: '', children: 'Click', onClick };
      const nextProps = { variant: 'primary', size: 'medium', disabled: false, loading: false, className: '', children: 'Different', onClick };
      expect(compareButtonProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareBadgeProps', () => {
    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { variant: 'primary', size: 'medium', dot: false, pill: false, className: '', children: 'Badge' };
      const nextProps = { variant: 'primary', size: 'medium', dot: false, pill: false, className: '', children: 'Badge' };
      expect(compareBadgeProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 dot 不同时返回 false', () => {
      const prevProps = { variant: 'primary', size: 'medium', dot: false, pill: false, className: '', children: 'Badge' };
      const nextProps = { variant: 'primary', size: 'medium', dot: true, pill: false, className: '', children: 'Badge' };
      expect(compareBadgeProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareSpinnerProps', () => {
    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { size: 'medium', label: 'Loading...' };
      const nextProps = { size: 'medium', label: 'Loading...' };
      expect(compareSpinnerProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 size 不同时返回 false', () => {
      const prevProps = { size: 'medium', label: 'Loading...' };
      const nextProps = { size: 'small', label: 'Loading...' };
      expect(compareSpinnerProps(prevProps, nextProps)).toBe(false);
    });
  });

  describe('compareSearchInputProps', () => {
    const onChange = () => {};
    const onClear = () => {};

    it('应该在所有 props 相同时返回 true', () => {
      const prevProps = { value: 'test', disabled: false, onChange, onClear, placeholder: 'Search...', debounceMs: 300, className: '' };
      const nextProps = { value: 'test', disabled: false, onChange, onClear, placeholder: 'Search...', debounceMs: 300, className: '' };
      expect(compareSearchInputProps(prevProps, nextProps)).toBe(true);
    });

    it('应该在 debounceMs 不同时返回 false', () => {
      const prevProps = { value: 'test', disabled: false, onChange, onClear, placeholder: 'Search...', debounceMs: 300, className: '' };
      const nextProps = { value: 'test', disabled: false, onChange, onClear, placeholder: 'Search...', debounceMs: 500, className: '' };
      expect(compareSearchInputProps(prevProps, nextProps)).toBe(false);
    });
  });
});
