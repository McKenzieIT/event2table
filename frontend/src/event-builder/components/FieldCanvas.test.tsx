import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import FieldCanvas from './FieldCanvas';

describe('FieldCanvas Component', () => {
  const mockProps = {
    fields: [],
    parameters: [],
    whereConditions: [],
    onFieldsChange: vi.fn(),
    onAddField: vi.fn(),
    onRemoveField: vi.fn(),
    onUpdateField: vi.fn(),
    onReorderFields: vi.fn(),
    isLoading: false,
    hasError: false
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('渲染测试', () => {
    it('应该正确渲染 FieldCanvas 组件', () => {
      render(<FieldCanvas {...mockProps} />);
      
      expect(screen.getByText(/字段画布/)).toBeInTheDocument();
    });

    it('应该在加载状态显示 Loading 组件', () => {
      render(<FieldCanvas {...mockProps} isLoading={true} />);
      
      expect(screen.getByText(/加载中/)).toBeInTheDocument();
    });

    it('应该在错误状态显示 Error 组件', () => {
      render(<FieldCanvas {...mockProps} hasError={true} />);
      
      expect(screen.getByText(/加载失败/)).toBeInTheDocument();
    });

    it('应该显示字段统计信息', () => {
      const fields = [
        {
          id: '1',
          type: 'parameter',
          name: 'role_id',
          displayName: '角色ID',
          dataType: 'string',
          isEditable: true,
          fieldType: 'param'
        },
        {
          id: '2',
          type: 'basic',
          name: 'ds',
          displayName: '日期',
          dataType: 'string',
          isEditable: false,
          fieldType: 'base'
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      expect(screen.getByText(/2/)).toBeInTheDocument();
    });
  });

  describe('字段显示测试', () => {
    it('应该正确显示参数字段', () => {
      const fields = [
        {
          id: '1',
          type: 'parameter',
          name: 'role_id',
          displayName: '角色ID',
          dataType: 'string',
          isEditable: true,
          fieldType: 'param',
          paramId: 1
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      expect(screen.getByText(/角色ID/)).toBeInTheDocument();
    });

    it('应该正确显示基础字段', () => {
      const fields = [
        {
          id: '1',
          type: 'basic',
          name: 'ds',
          displayName: '日期',
          dataType: 'string',
          isEditable: false,
          fieldType: 'base'
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      expect(screen.getByText(/日期/)).toBeInTheDocument();
    });

    it('应该正确显示自定义字段', () => {
      const fields = [
        {
          id: '1',
          type: 'custom',
          name: 'custom_field',
          displayName: '自定义字段',
          dataType: 'string',
          isEditable: true,
          fieldType: 'custom'
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      expect(screen.getByText(/自定义字段/)).toBeInTheDocument();
    });

    it('应该正确显示固定字段', () => {
      const fields = [
        {
          id: '1',
          type: 'fixed',
          name: 'fixed_value',
          displayName: '固定值',
          dataType: 'string',
          isEditable: true,
          fieldType: 'fixed',
          fixedValue: 'test'
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);
      
      expect(screen.getByText(/固定值/)).toBeInTheDocument();
    });
  });

  describe('参数显示测试', () => {
    it('应该正确显示可用参数列表', () => {
      const parameters = [
        {
          id: '1',
          name: 'role_id',
          displayName: '角色ID',
          dataType: 'string'
        },
        {
          id: '2',
          name: 'account_id',
          displayName: '账号ID',
          dataType: 'string'
        }
      ];

      render(<FieldCanvas {...mockProps} parameters={parameters} />);
      
      expect(screen.getByText(/角色ID/)).toBeInTheDocument();
      expect(screen.getByText(/账号ID/)).toBeInTheDocument();
    });
  });

  describe('边界情况测试', () => {
    it('应该处理 undefined 或 null 的 fields', () => {
      render(<FieldCanvas {...mockProps} fields={undefined as any} />);
      
      expect(screen.getByText(/0/)).toBeInTheDocument();
    });

    it('应该处理 undefined 或 null 的 parameters', () => {
      render(<FieldCanvas {...mockProps} parameters={undefined as any} />);
      
      expect(screen.getByText(/字段画布/)).toBeInTheDocument();
    });

    it('应该处理空数组', () => {
      render(<FieldCanvas {...mockProps} fields={[]} parameters={[]} />);
      
      expect(screen.getByText(/0/)).toBeInTheDocument();
    });
  });
});
