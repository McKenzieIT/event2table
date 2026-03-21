import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import WhereBuilder, { WhereCondition } from './WhereBuilder';

describe('WhereBuilder Component', () => {
  const mockOnChange = vi.fn();
  const mockOnOpenModal = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('渲染测试', () => {
    it('应该正确渲染 WHERE 条件构建器', () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/WHERE条件/)).toBeInTheDocument();
      expect(screen.getByText(/暂无WHERE条件/)).toBeInTheDocument();
    });

    it('应该显示配置按钮', () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/配置/)).toBeInTheDocument();
    });
  });

  describe('条件显示测试', () => {
    it('应该正确显示单个条件', () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          field: 'role_id',
          operator: '=',
          value: '12345'
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/role_id = '12345'/)).toBeInTheDocument();
    });

    it('应该正确显示多个条件', () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          field: 'role_id',
          operator: '=',
          value: '12345',
          logicalOperator: 'AND'
        },
        {
          id: '2',
          field: 'account_id',
          operator: '=',
          value: '67890'
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/AND role_id = '12345'/)).toBeInTheDocument();
      expect(screen.getByText(/account_id = '67890'/)).toBeInTheDocument();
    });

    it('应该正确显示条件组', () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          type: 'group',
          conditions: [
            { id: '1-1', field: 'role_id', operator: '=', value: '12345' } as any
          ]
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/\(1 个条件\)/)).toBeInTheDocument();
    });
  });

  describe('交互测试', () => {
    it('点击配置按钮应该调用 onOpenModal', () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      const configButton = screen.getByText(/配置/);
      fireEvent.click(configButton);

      expect(mockOnOpenModal).toHaveBeenCalledTimes(1);
    });

    it('点击标题栏应该切换折叠状态', () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      const header = screen.getByText(/WHERE条件/).closest('.section-header');
      
      // 初始状态是折叠的，内容不可见
      expect(screen.queryByText(/点击"配置"按钮编辑WHERE条件/)).not.toBeInTheDocument();

      // 点击展开
      if (header) {
        fireEvent.click(header);
      }
      
      expect(screen.getByText(/点击"配置"按钮编辑WHERE条件/)).toBeInTheDocument();
    });
  });

  describe('边界情况测试', () => {
    it('应该处理 undefined 或 null 的 conditions', () => {
      render(
        <WhereBuilder
          conditions={undefined as any}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/暂无WHERE条件/)).toBeInTheDocument();
    });

    it('应该处理空字段或值的条件', () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          field: '',
          operator: '=',
          value: ''
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/\? = ''/)).toBeInTheDocument();
    });
  });
});
