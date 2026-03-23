import type { CanvasField } from '@shared/hooks/useEventNodeBuilder';
import { render, screen } from '@test/test-utils';
import { describe, it, expect, vi } from 'vitest';

import FieldCanvas from './FieldCanvas';

describe('FieldCanvas Component', () => {
  const mockProps = {
    fields: [] as CanvasField[],
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

      expect(screen.getByText(/加载参数中/)).toBeInTheDocument();
    });

    it('应该在错误状态显示 Error 组件', () => {
      render(<FieldCanvas {...mockProps} hasError={true} />);

      expect(screen.getByText(/加载参数失败/)).toBeInTheDocument();
    });

    it('应该显示字段统计信息', () => {
      const fields: CanvasField[] = [
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
      const fields: CanvasField[] = [
        {
          id: '1',
          type: 'parameter',
          name: 'role_id',
          fieldName: 'role_id',
          alias: '角色ID',
          displayName: '角色ID',
          dataType: 'string',
          isEditable: true,
          fieldType: 'param',
          paramId: 1
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);

      // 使用 getAllByText 处理多个匹配（alias 和 original-name 都包含该文本）
      const elements = screen.getAllByText(/角色ID/);
      expect(elements.length).toBeGreaterThan(0);
    });

    it('应该正确显示基础字段', () => {
      const fields: CanvasField[] = [
        {
          id: '1',
          type: 'basic',
          name: 'ds',
          fieldName: 'ds',
          alias: '日期',
          displayName: '日期',
          dataType: 'string',
          isEditable: false,
          fieldType: 'base'
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);

      const elements = screen.getAllByText(/日期/);
      expect(elements.length).toBeGreaterThan(0);
    });

    it('应该正确显示自定义字段', () => {
      const fields: CanvasField[] = [
        {
          id: '1',
          type: 'custom',
          name: 'custom_field',
          fieldName: 'custom_field',
          alias: '自定义字段',
          displayName: '自定义字段',
          dataType: 'string',
          isEditable: true,
          fieldType: 'custom'
        }
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);

      // 自定义字段会出现在多个位置：字段别名、工具栏按钮等
      const elements = screen.getAllByText(/自定义字段/);
      expect(elements.length).toBeGreaterThan(0);
    });

    it('应该正确显示固定字段', () => {
      const fields: CanvasField[] = [
        {
          id: '1',
          type: 'fixed',
          name: 'fixed_value',
          fieldName: 'fixed_value',
          alias: '固定值字段',
          displayName: '固定值字段',
          dataType: 'string',
          isEditable: true,
          fieldType: 'fixed',
          fixedValue: 'test'
        } as CanvasField
      ];

      render(<FieldCanvas {...mockProps} fields={fields} />);

      // 使用独特的 alias 避免与工具栏按钮文本冲突
      const elements = screen.getAllByText(/固定值字段/);
      expect(elements.length).toBeGreaterThan(0);
    });
  });

  describe('参数显示测试', () => {
    it('应该正确处理 parameters prop', () => {
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

      // 组件接收 parameters 但不直接显示它们
      // parameters 用于拖拽添加字段时的数据源
      render(<FieldCanvas {...mockProps} parameters={parameters} />);

      // 验证组件正常渲染（不崩溃）
      expect(screen.getByText(/字段画布/)).toBeInTheDocument();
      // 显示空状态提示
      expect(screen.getByText(/从左侧拖拽参数到此处添加字段/)).toBeInTheDocument();
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