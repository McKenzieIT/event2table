/**
 * classNames utility tests
 * 测试类名构建工具函数
 */

import { describe, it, expect } from 'vitest';

import {
  buildConditionalClasses,
  buildWrapperClasses,
  buildInputClasses,
  buildLabelClasses,
  buildCompoundClasses
} from './classNames';

describe('classNames utilities', () => {
  describe('buildConditionalClasses', () => {
    it('应该构建基础类名', () => {
      const result = buildConditionalClasses('cyber-input', {}, []);
      expect(result).toBe('cyber-input');
    });

    it('应该添加修饰符类名', () => {
      const result = buildConditionalClasses('cyber-input', { invalid: true, disabled: false }, []);
      expect(result).toBe('cyber-input cyber-input--invalid');
    });

    it('应该添加额外类名', () => {
      const result = buildConditionalClasses('cyber-input', {}, ['custom-class']);
      expect(result).toBe('custom-class cyber-input');
    });

    it('应该组合所有类名', () => {
      const result = buildConditionalClasses(
        'cyber-input',
        { invalid: true, disabled: true, focused: false },
        ['custom-class-1', 'custom-class-2']
      );
      expect(result).toBe('custom-class-1 custom-class-2 cyber-input cyber-input--invalid cyber-input--disabled');
    });

    it('应该过滤空值', () => {
      const result = buildConditionalClasses('cyber-input', { invalid: false }, ['', 'custom-class']);
      expect(result).toBe('custom-class cyber-input');
    });

    it('应该处理布尔值为 false 的修饰符', () => {
      const result = buildConditionalClasses('cyber-input', { invalid: false, disabled: false }, []);
      expect(result).toBe('cyber-input');
    });
  });

  describe('buildWrapperClasses', () => {
    it('应该构建包装器类名', () => {
      const result = buildWrapperClasses('cyber-checkbox-wrapper', { invalid: true, disabled: false });
      expect(result).toBe('cyber-checkbox-wrapper cyber-checkbox-wrapper--invalid');
    });

    it('应该处理空修饰符', () => {
      const result = buildWrapperClasses('cyber-checkbox-wrapper', {});
      expect(result).toBe('cyber-checkbox-wrapper');
    });
  });

  describe('buildInputClasses', () => {
    it('应该构建输入控件类名', () => {
      const result = buildInputClasses('cyber-checkbox', { checked: true, disabled: false });
      expect(result).toBe('cyber-checkbox cyber-checkbox--checked');
    });

    it('应该处理多个修饰符', () => {
      const result = buildInputClasses('cyber-checkbox', { checked: true, disabled: true, invalid: false });
      expect(result).toBe('cyber-checkbox cyber-checkbox--checked cyber-checkbox--disabled');
    });
  });

  describe('buildLabelClasses', () => {
    it('应该构建标签类名', () => {
      const result = buildLabelClasses('cyber-input__label', { required: true });
      expect(result).toBe('cyber-input__label cyber-input__label--required');
    });

    it('应该处理空修饰符', () => {
      const result = buildLabelClasses('cyber-input__label', {});
      expect(result).toBe('cyber-input__label');
    });
  });

  describe('buildCompoundClasses', () => {
    it('应该构建基础类名', () => {
      const result = buildCompoundClasses('cyber-button');
      expect(result).toBe('cyber-button');
    });

    it('应该添加变体类名', () => {
      const result = buildCompoundClasses('cyber-button', 'primary');
      expect(result).toBe('cyber-button cyber-button--primary');
    });

    it('应该添加尺寸类名', () => {
      const result = buildCompoundClasses('cyber-button', undefined, 'medium');
      expect(result).toBe('cyber-button cyber-button--medium');
    });

    it('应该添加修饰符类名', () => {
      const result = buildCompoundClasses('cyber-button', undefined, undefined, { disabled: true, loading: false });
      expect(result).toBe('cyber-button cyber-button--disabled');
    });

    it('应该添加自定义类名', () => {
      const result = buildCompoundClasses('cyber-button', undefined, undefined, {}, 'my-button');
      expect(result).toBe('cyber-button my-button');
    });

    it('应该组合所有参数', () => {
      const result = buildCompoundClasses(
        'cyber-button',
        'primary',
        'medium',
        { disabled: true, loading: false },
        'my-button'
      );
      expect(result).toBe('cyber-button cyber-button--primary cyber-button--medium cyber-button--disabled my-button');
    });

    it('应该过滤空值', () => {
      const result = buildCompoundClasses('cyber-button', '', undefined, { disabled: false }, '');
      expect(result).toBe('cyber-button');
    });
  });
});
